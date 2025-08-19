import json
import asyncio
import logging
import weakref
from typing import Dict, Set, Optional
from django.http import StreamingHttpResponse
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from asgiref.sync import sync_to_async
from django.apps import AppConfig
from constants import (
    MAX_TIME_RETRY_CONNECTION,
    MAX_QUEUE_SIZE,
    DEFAULT_TIMEOUT
)

logger = logging.getLogger(__name__)


class SSEManager:
    def __init__(self):
        self.connections: Dict[int, Set] = {}
        self._lock = asyncio.Lock()
        self._shutdown = False

    async def add_connection(self, user_id: int, connection):
        async with self._lock:
            if user_id not in self.connections:
                self.connections[user_id] = set()
            self.connections[user_id].add(connection)
        logger.info(f"Added SSE connection for user {user_id}")

    async def remove_connection(self, user_id: int, connection):
        async with self._lock:
            if user_id in self.connections:
                self.connections[user_id].discard(connection)
                if not self.connections[user_id]:
                    del self.connections[user_id]
        logger.info(f"Removed SSE connection for user {user_id}")

    async def send_to_user(self, user_id: int, data: dict):
        """Gửi data đến user"""
        if self._shutdown:
            return
            
        async with self._lock:
            if user_id not in self.connections:
                return
            connections = list(self.connections[user_id])

        message = self._format_sse_message(data)
        dead_connections = set()

        for connection in connections:
            try:
                if hasattr(connection, 'send_message'):
                    await connection.send_message(message)
            except Exception as e:
                logger.error(f"Error sending to connection: {e}")
                dead_connections.add(connection)

        if dead_connections:
            async with self._lock:
                for dc in dead_connections:
                    if user_id in self.connections:
                        self.connections[user_id].discard(dc)
                if user_id in self.connections and not self.connections[user_id]:
                    del self.connections[user_id]

    async def shutdown(self):
        """Graceful shutdown tất cả connections"""
        self._shutdown = True
        async with self._lock:
            all_connections = []
            for user_connections in self.connections.values():
                all_connections.extend(user_connections)
            
            for connection in all_connections:
                try:
                    connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self.connections.clear()

    def _format_sse_message(self, data: dict) -> str:
        json_data = json.dumps(data, cls=DjangoJSONEncoder, ensure_ascii=False)
        return f"data: {json_data}\n\n"


# Global SSE manager
sse_manager = SSEManager()


class ASGISSEConnection:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)  # Giới hạn queue size
        self.closed = False
        self._close_event = asyncio.Event()

    async def send_message(self, message: str):
        if not self.closed:
            try:
                # Non-blocking put với timeout
                await asyncio.wait_for(
                    self.message_queue.put(message), 
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"Message queue full for user {self.user_id}, dropping message")

    async def get_message(self, timeout=1.0):
        """Lấy message với timeout"""
        if self.closed:
            return None
            
        try:
            return await asyncio.wait_for(self.message_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def close(self):
        self.closed = True
        self._close_event.set()

    async def wait_for_close(self):
        """Wait for connection to be closed"""
        await self._close_event.wait()


async def sse_event_stream(user_id: int):
    connection = ASGISSEConnection(user_id)
    await sse_manager.add_connection(user_id, connection)

    try:
        # Initial message
        initial_message = sse_manager._format_sse_message({
            'type': 'connection',
            'data': {
                'status': 'connected',
                'user_id': user_id,
                'timestamp': timezone.now().isoformat()
            }
        })
        yield initial_message

        last_sent = timezone.now()
        heartbeat_task = None

        while not connection.closed and not sse_manager._shutdown:
            try:
                # Tạo timeout task cho việc lấy message
                message_task = asyncio.create_task(connection.get_message(timeout=DEFAULT_TIMEOUT))
                close_task = asyncio.create_task(connection.wait_for_close())
                
                # Wait for either message or close event
                done, pending = await asyncio.wait(
                    [message_task, close_task],
                    timeout=DEFAULT_TIMEOUT,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                if close_task in done:
                    # Connection closed
                    break

                message = None
                if message_task in done:
                    try:
                        message = await message_task
                    except Exception:
                        pass

                if message:
                    yield message
                    last_sent = timezone.now()
                else:
                    # Check for heartbeat
                    if (timezone.now() - last_sent).total_seconds() >= MAX_TIME_RETRY_CONNECTION:
                        heartbeat = {
                            'type': 'heartbeat',
                            'data': {'timestamp': timezone.now().isoformat()}
                        }
                        yield sse_manager._format_sse_message(heartbeat)
                        last_sent = timezone.now()

            except asyncio.CancelledError:
                logger.info(f"SSE stream cancelled for user {user_id}")
                break
            except Exception as e:
                logger.error(f"Error in SSE stream for user {user_id}: {e}")
                break

    except asyncio.CancelledError:
        logger.info(f"SSE stream cancelled for user {user_id}")
    except Exception as e:
        logger.error(f"Error in SSE stream for user {user_id}: {e}")
    finally:
        connection.close()
        await sse_manager.remove_connection(user_id, connection)


def create_sse_response(user_id: int) -> StreamingHttpResponse:
    """Tạo StreamingHttpResponse cho SSE trong môi trường ASGI"""
    
    async def async_stream():
        try:
            async for chunk in sse_event_stream(user_id):
                yield chunk.encode('utf-8')
        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for user {user_id}")
        except Exception as e:
            logger.error(f"Error in async stream for user {user_id}: {e}")

    response = StreamingHttpResponse(
        async_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Headers'] = 'Cache-Control'
    response['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
    return response


async def send_notification_to_user(user_id: int, notification, redirect_url=None):
    """Gửi thông báo đến user qua SSE"""
    try:
        notification_data = {
            'type': 'notification',
            'data': {
                'id': notification.id,
                'title': notification.title,
                'content': notification.content,
                'notification_type': notification.type,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
            }
        }
        if redirect_url:
            notification_data['data']['redirect_url'] = redirect_url
            
        await sse_manager.send_to_user(user_id, notification_data)
        logger.info(f"Sent notification to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending notification via SSE: {e}")


# Sync wrapper cho trường hợp cần gọi từ sync code
def send_notification_to_user_sync(user_id: int, notification, redirect_url=None):
    """Sync wrapper cho send_notification_to_user"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Nếu loop đang chạy, tạo task
            task = asyncio.create_task(
                send_notification_to_user(user_id, notification, redirect_url)
            )
            return task
        else:
            # Nếu loop không chạy, chạy trực tiếp
            return loop.run_until_complete(
                send_notification_to_user(user_id, notification, redirect_url)
            )
    except RuntimeError:
        # Không có event loop, tạo mới
        return asyncio.run(
            send_notification_to_user(user_id, notification, redirect_url)
        )

class SSEConfig(AppConfig):
    name = 'docwn'
    
    def ready(self):
        import atexit
        import signal
        
        def cleanup():
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(sse_manager.shutdown())
                else:
                    loop.run_until_complete(sse_manager.shutdown())
            except Exception as e:
                logger.error(f"Error during SSE cleanup: {e}")
        
        # Register cleanup handlers
        atexit.register(cleanup)
        signal.signal(signal.SIGTERM, lambda signum, frame: cleanup())
        signal.signal(signal.SIGINT, lambda signum, frame: cleanup())
