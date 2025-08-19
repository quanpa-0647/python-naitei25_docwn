class SSENotificationManager {
    constructor() {
        this.eventSource = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 5000;
        this.notificationSound = null;
        
        this.init();
    }
    
    init() {
        this.loadNotificationSound();
        this.setupEventListeners();
        this.connectSSE();
    }
    
    loadNotificationSound() {
        // Base64 encoded notification sound
        this.notificationSound = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmIdBSuDy/LWfywGKILM8+KAQF+a2/LGdiMFl2+z09eUVAjOhsnzu4IxBAIAAAI=');
    }
    
    connectSSE() {
        if (this.eventSource && this.eventSource.readyState !== EventSource.CLOSED) {
            return;
        }
        
        try {
            this.eventSource = new EventSource('/interactions/sse/stream/');
            
            this.eventSource.onopen = () => {
                // console.log('✅ SSE Connected');
                this.reconnectAttempts = 0;
                this.hideConnectionStatus();
            };
            
            this.eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleNotification(data);
                } catch (error) {
                    // console.error('Error parsing SSE data:', error);
                }
            };
            
            this.eventSource.onerror = (error) => {
                // console.error('❌ SSE Error:', error);
                // this.showConnectionStatus(gettext('Mất kết nối, đang thử kết nối lại...'));
                this.handleReconnection();
            };
            
        } catch (error) {
            // console.error('Failed to create SSE connection:', error);
            this.handleReconnection();
        }
    }
    
    handleReconnection() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
        }
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
            
            // console.log(`🔄 Reconnecting in ${delay/1000}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connectSSE();
            }, delay);
        } else {
            // console.error('❌ Max reconnection attempts reached');
            // this.showConnectionStatus(gettext('Không thể kết nối. Vui lòng tải lại trang.'), 'error');
        }
    }
    
    handleNotification(data) {
        if (data.type === 'notification') {
            // Show popup notification
            this.showPopupNotification(data.data);
            
            // Add to notification list (tích hợp với NotificationListManager)
            if (window.notificationListManager) {
                window.notificationListManager.prependNotification(data.data);
                window.notificationListManager.updateNotificationBadge(1);
            }
            
            // Play sound
            // this.playNotificationSound();
        }
    }
    
    showPopupNotification(notification) {
        // Remove existing popup notifications to avoid overlap
        const existingPopups = document.querySelectorAll('.notification-popup');
        existingPopups.forEach(popup => popup.remove());
        
        // Create popup notification
        const popup = document.createElement('div');
        popup.className = 'notification-popup';
        popup.style.cssText = `
            position: fixed; 
            top: 80px; 
            right: 20px; 
            z-index: 9999;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 16px 20px;
            border-radius: 12px; 
            max-width: 380px; 
            min-width: 280px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            animation: slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            transition: all 0.3s ease;
        `;
        
        popup.innerHTML = `
            <div style="display: flex; align-items: start; gap: 12px;">
                <div style="
                    background: rgba(255,255,255,0.2); 
                    border-radius: 50%; 
                    padding: 8px; 
                    flex-shrink: 0;
                ">
                    <i class="bx bx-bell" style="font-size: 18px;"></i>
                </div>
                <div style="flex-grow: 1; min-width: 0;">
                    <div style="
                        font-weight: 600; 
                        margin-bottom: 6px; 
                        font-size: 15px;
                        line-height: 1.3;
                    ">${this.escapeHtml(notification.title)}</div>
                    <div style="
                        font-size: 13px; 
                        line-height: 1.4; 
                        opacity: 0.9;
                        word-wrap: break-word;
                    ">${this.escapeHtml(notification.content)}</div>
                    <div style="
                        font-size: 11px; 
                        opacity: 0.7; 
                        margin-top: 6px;
                        display: flex;
                        align-items: center;
                        gap: 4px;
                    ">
                        <i class="bx bx-time"></i>
                        ${gettext("Vừa xong")}
                    </div>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: rgba(255,255,255,0.2); 
                    border: none; 
                    color: white;
                    cursor: pointer; 
                    font-size: 16px;
                    border-radius: 50%;
                    width: 28px;
                    height: 28px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                    transition: all 0.2s ease;
                " onmouseover="this.style.background='rgba(255,255,255,0.3)'" 
                   onmouseout="this.style.background='rgba(255,255,255,0.2)'">×</button>
            </div>
        `;
        
        // Add hover effects
        popup.addEventListener('mouseenter', () => {
            popup.style.transform = 'translateY(-2px)';
            popup.style.boxShadow = '0 12px 40px rgba(0,0,0,0.4)';
        });
        
        popup.addEventListener('mouseleave', () => {
            popup.style.transform = 'translateY(0)';
            popup.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)';
        });
        
        // Click to dismiss
        popup.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                popup.remove();
            }
        });
        
        document.body.appendChild(popup);
        
        // Auto remove after 8 seconds
        setTimeout(() => {
            if (popup.parentNode) {
                popup.style.animation = 'slideOutRight 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
                setTimeout(() => popup.remove(), 400);
            }
        }, 8000);
    }
    
    // playNotificationSound() {
    //     try {
    //         if (this.notificationSound) {
    //             this.notificationSound.currentTime = 0;
    //             this.notificationSound.volume = 0.3;
    //             this.notificationSound.play().catch(e => {
    //                 console.log('Could not play notification sound:', e);
    //             });
    //         }
    //     } catch (error) {
    //         console.log('Notification sound error:', error);
    //     }
    // }
    
    showConnectionStatus(message, type = 'warning') {
        let statusBar = document.getElementById('connection-status');
        
        if (!statusBar) {
            statusBar = document.createElement('div');
            statusBar.id = 'connection-status';
            statusBar.style.cssText = `
                position: fixed; 
                top: 0; 
                left: 0; 
                right: 0; 
                z-index: 10000;
                padding: 8px 16px;
                text-align: center;
                font-size: 13px;
                font-weight: 500;
                color: white;
                background: ${type === 'error' ? '#dc3545' : '#ffc107'};
                animation: slideDownStatus 0.3s ease-out;
            `;
            document.body.appendChild(statusBar);
        }
        
        statusBar.textContent = message;
        statusBar.style.display = 'block';
    }
    
    hideConnectionStatus() {
        const statusBar = document.getElementById('connection-status');
        if (statusBar) {
            statusBar.style.animation = 'slideUpStatus 0.3s ease-in';
            setTimeout(() => {
                if (statusBar.parentNode) {
                    statusBar.remove();
                }
            }, 300);
        }
    }
    
    setupEventListeners() {
        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible' && 
                (!this.eventSource || this.eventSource.readyState === EventSource.CLOSED)) {
                this.connectSSE();
            }
        });
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            this.disconnect();
        });
    }
    
    disconnect() {
        if (this.eventSource) {
            this.eventSource.close();
            this.eventSource = null;
            // console.log('🔌 SSE Disconnected');
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Enhanced Notification List Manager with Offset-based Pagination
class NotificationListManager {
    constructor() {
        this.offset = 0;
        this.loading = false;
        this.hasMore = true;
        
        this.notificationList = document.getElementById('notificationList');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.notificationBtn = document.getElementById('notificationBtn');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Scroll event for loading more notifications
        if (this.notificationList) {
            this.notificationList.addEventListener('scroll', () => {
                if (this.loading || !this.hasMore) return;
                
                const scrollTop = this.notificationList.scrollTop;
                const scrollHeight = this.notificationList.scrollHeight;
                const clientHeight = this.notificationList.clientHeight;
                
                // Load more when scrolled to bottom (with 10px threshold)
                if (scrollTop + clientHeight >= scrollHeight - 10) {
                    this.loadMoreNotifications();
                }
            });
        }
        
        // Click event for notification items (mark as read)
        if (this.notificationList) {
            this.notificationList.addEventListener('click', (e) => {
                const notificationItem = e.target.closest('.notification-item');
                if (notificationItem && notificationItem.classList.contains('unread')) {
                    const notificationId = notificationItem.dataset.notificationId;
                    this.markNotificationAsRead(notificationId, notificationItem);
                }
            });
        }

        if (this.notificationBtn) {
            this.notificationBtn.addEventListener('click', (e) => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                
                if (this.notificationList) {
                    this.notificationList.scrollTop = 0;
                }
            });
        }
        
        const notificationDropdown = document.querySelector('.notification-menu');
        if (notificationDropdown) {
            notificationDropdown.addEventListener('show.bs.dropdown', () => {
                if (this.notificationList) {
                    this.notificationList.scrollTop = 0;
                }
            });
        }
    }
    
    loadMoreNotifications() {
        if (this.loading || !this.hasMore) return;
        
        this.loading = true;
        this.loadingIndicator.classList.remove('d-none');
        
        fetch(`/interactions/ajax/notifications/load_more/?offset=${this.offset}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken(),
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.notifications.length > 0) {
                this.offset += data.notifications.length;
                this.appendNotifications(data.notifications);
                this.hasMore = data.has_more;
            } else {
                this.hasMore = false;
            }
        })
        .catch(error => {
            // console.error('Error loading more notifications:', error);
        })
        .finally(() => {
            this.loading = false;
            this.loadingIndicator.classList.add('d-none');
        });
    }
    
    appendNotifications(notifications) {
        notifications.forEach(notification => {
            const notificationHtml = this.createNotificationHTML(notification);
            this.notificationList.insertAdjacentHTML('beforeend', notificationHtml);
        });
    }
    
    // Method để prepend notification mới từ SSE
    prependNotification(notification) {
        if (!this.notificationList) return;
        
        // Check if "no notifications" message exists and remove it
        const emptyMessage = this.notificationList.querySelector('.dropdown-item-text');
        if (emptyMessage) {
            emptyMessage.remove();
        }
        
        // Create notification HTML and prepend to list
        const notificationHtml = this.createNotificationHTML({
            ...notification,
            is_read: false,
            created_at: gettext('Vừa xong')
        });
        
        this.notificationList.insertAdjacentHTML('afterbegin', notificationHtml);
        
        // Tăng offset để đồng bộ với việc thêm thông báo mới
        this.offset++;
        
        // Add animation to new notification
        const newItem = this.notificationList.firstElementChild;
        if (newItem) {
            newItem.style.animation = 'slideInDown 0.4s ease-out';
            newItem.style.background = 'rgba(13, 110, 253, 0.1)';
            
            // Remove animation and highlight after delay
            setTimeout(() => {
                newItem.style.animation = '';
                newItem.style.background = '';
            }, 2000);
        }
        
        // Limit to 50 notifications max in DOM for performance
        const items = this.notificationList.querySelectorAll('.notification-item');
        if (items.length > 50) {
            items[items.length - 1].remove();
            // Giảm offset để đồng bộ với việc xóa thông báo cuối
            this.offset--;
        }
    }
    
    createNotificationHTML(notification) {
        const unreadClass = notification.is_read ? '' : 'unread';
        const unreadIndicator = notification.is_read ? '' : `
            <div class="unread-indicator">
                <span class="badge bg-primary rounded-pill">&nbsp;</span>
            </div>
        `;
        
        return `
            <div class="dropdown-item notification-item ${unreadClass}" data-notification-id="${notification.id}">
                <div class="d-flex align-items-start">
                    <div class="notification-icon me-2">
                        <i class="bx bx-info-circle text-primary"></i>
                    </div>
                    <div class="notification-content flex-grow-1">
                        <div class="notification-title fw-bold">${this.escapeHtml(notification.title)}</div>
                        <div class="notification-message text-muted small">${this.escapeHtml(notification.content)}</div>
                        <div class="notification-time text-muted small">
                            <i class="bx bx-time"></i>
                            ${notification.created_at}
                        </div>
                    </div>
                    ${unreadIndicator}
                </div>
            </div>
        `;
    }
    
    markNotificationAsRead(notificationId, notificationElement) {
        const isUnread = notificationElement.classList.contains('unread');
        
        fetch(`/interactions/ajax/notifications/${notificationId}/mark_read/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                notificationElement.classList.remove('unread');
                const unreadIndicator = notificationElement.querySelector('.unread-indicator');
                if (unreadIndicator) {
                    unreadIndicator.remove();
                }
                
                // Chỉ update badge count nếu thông báo trước đó là unread
                if (isUnread) {
                    this.updateNotificationBadge(-1);
                }
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
    }
    
    updateNotificationBadge(change) {
        const badge = this.notificationBtn ? this.notificationBtn.querySelector('.badge') : null;
        
        if (change > 0) {
            // Tăng counter
            if (badge) {
                const currentCount = parseInt(badge.textContent) || 0;
                const newCount = currentCount + change;
                badge.textContent = newCount;
                
                // Add animation
                badge.style.animation = 'pulse 0.6s ease-in-out';
                setTimeout(() => {
                    badge.style.animation = '';
                }, 600);
            } else if (this.notificationBtn) {
                // Tạo badge mới nếu chưa có
                const newBadge = document.createElement('span');
                newBadge.className = 'badge bg-danger rounded-pill ms-1';
                newBadge.textContent = change;
                newBadge.style.animation = 'pulse 0.6s ease-in-out';
                this.notificationBtn.appendChild(newBadge);
                
                setTimeout(() => {
                    newBadge.style.animation = '';
                }, 600);
            }
        } else if (change < 0 && badge) {
            // Giảm counter
            const currentCount = parseInt(badge.textContent) || 0;
            const newCount = Math.max(0, currentCount + change);
            
            if (newCount === 0) {
                badge.remove();
            } else {
                badge.textContent = newCount;
            }
        }
        
        // Update header count in dropdown
        this.updateHeaderCount(change);
    }
    
    updateHeaderCount(change) {
        const headerCount = document.querySelector('.notification-menu .dropdown-header small');
        if (headerCount && change !== 0) {
            const text = headerCount.textContent;
            const currentCount = parseInt(text) || 0;
            const newCount = Math.max(0, currentCount + change);
            
            if (newCount === 0) {
                headerCount.textContent = '';
                headerCount.style.display = 'none';
            } else {
                headerCount.textContent = newCount + " " + gettext('chưa đọc');
                headerCount.style.display = 'inline';
            }
        }
    }
    
    getCSRFToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            return meta.getAttribute('content');
        }
        
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Add required CSS animations
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from { 
            transform: translateX(100%); 
            opacity: 0; 
        }
        to { 
            transform: translateX(0); 
            opacity: 1; 
        }
    }
    
    @keyframes slideOutRight {
        from { 
            transform: translateX(0); 
            opacity: 1; 
        }
        to { 
            transform: translateX(100%); 
            opacity: 0; 
        }
    }
    
    @keyframes slideDownStatus {
        from { 
            transform: translateY(-100%); 
            opacity: 0; 
        }
        to { 
            transform: translateY(0); 
            opacity: 1; 
        }
    }
    
    @keyframes slideUpStatus {
        from { 
            transform: translateY(0); 
            opacity: 1; 
        }
        to { 
            transform: translateY(-100%); 
            opacity: 0; 
        }
    }
    
    @keyframes slideInDown {
        from { 
            transform: translateY(-20px); 
            opacity: 0; 
        }
        to { 
            transform: translateY(0); 
            opacity: 1; 
        }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    .notification-popup:hover {
        transform: translateY(-2px);
    }
    
    .notification-item {
        transition: all 0.2s ease;
    }
    
    .notification-item:hover {
        background-color: rgba(0,0,0,0.05) !important;
    }
    
    .notification-item.unread {
        background-color: rgba(13, 110, 253, 0.05);
        border-left: 3px solid #0d6efd;
    }
`;
document.head.appendChild(notificationStyles);

// Initialize managers when DOM is ready
let sseNotificationManager;
let notificationListManager;

function initializeManagers() {
    // Initialize notification list manager first
    notificationListManager = new NotificationListManager();
    
    // Make it globally accessible for SSE manager
    window.notificationListManager = notificationListManager;
    
    // Initialize SSE manager
    sseNotificationManager = new SSENotificationManager();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeManagers);
} else {
    initializeManagers();
}