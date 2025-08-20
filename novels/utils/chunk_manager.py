from .helpers import count_words
from .simple_chunker import SimpleChunker
from .html_chunker import HtmlChunker


class ChunkManager:
    """Manager class for handling chapter content chunking operations."""
    
    @staticmethod
    def create_normal_chunks_for_chapter(chapter, content: str, chunker: SimpleChunker = None):
        """
        Create chunks for a chapter using simple normal chunking.
        
        Args:
            chapter: Chapter model instance
            content: Raw content to be chunked
            chunker: Optional SimpleChunker instance
        """
        from novels.models import Chunk
        
        if chunker is None:
            chunker = SimpleChunker()
            
        # Calculate total word count from original content first
        total_word_count = count_words(content)
        
        # Clear existing chunks only if chapter is saved (has a primary key)
        if chapter.pk:
            Chunk.objects.filter(chapter=chapter).delete()
        
        # Create new chunks
        chunks_data = chunker.split_into_chunks(content)
        
        for position, (chunk_content, word_count) in enumerate(chunks_data, 1):
            Chunk.objects.create(
                chapter=chapter,
                position=position,
                content=chunk_content,
                word_count=word_count
            )
        
        # Update chapter word count with pre-calculated total
        chapter.word_count = total_word_count
        chapter.save(update_fields=['word_count'])
        
        return len(chunks_data)
    
    @staticmethod
    def create_html_chunks_for_chapter(chapter, content: str, chunker: HtmlChunker = None):
        """
        Create chunks for a chapter using HTML-aware chunking for rich text content.
        
        Args:
            chapter: Chapter model instance
            content: HTML content to be chunked
            chunker: Optional HtmlChunker instance
        """
        from novels.models import Chunk
        from bs4 import BeautifulSoup
        
        if chunker is None:
            chunker = HtmlChunker()
        
        # Extract text content for word counting (preserve original HTML for chunks)
        soup = BeautifulSoup(content, 'html.parser')
        total_word_count = count_words(soup.get_text())
        
        # Clear existing chunks only if chapter is saved (has a primary key)
        if chapter.pk:
            Chunk.objects.filter(chapter=chapter).delete()
        
        # Create new chunks using HTML-aware chunking
        chunks_data = chunker.split_into_chunks(content)
        
        for position, (chunk_content, word_count) in enumerate(chunks_data, 1):
            # Validate that each chunk is valid HTML
            if chunker.validate_html_chunk(chunk_content):
                Chunk.objects.create(
                    chapter=chapter,
                    position=position,
                    content=chunk_content,
                    word_count=word_count
                )
            else:
                # Fallback: wrap in paragraph tags if HTML is invalid
                safe_content = f'<p>{chunk_content}</p>'
                Chunk.objects.create(
                    chapter=chapter,
                    position=position,
                    content=safe_content,
                    word_count=word_count
                )
        
        # Update chapter word count with pre-calculated total
        chapter.word_count = total_word_count
        chapter.save(update_fields=['word_count'])
        
        return len(chunks_data)
    
    @staticmethod
    def create_chunks_for_chapter(chapter, content: str, chunker: SimpleChunker = None):
        """
        Create chunks for a chapter using normal chunking.
        
        Args:
            chapter: Chapter model instance
            content: Raw content to be chunked  
            chunker: Optional SimpleChunker instance
        """
        return ChunkManager.create_normal_chunks_for_chapter(chapter, content, chunker)
    
    @staticmethod
    def update_chapter_chunks(chapter, new_content: str, chunker: SimpleChunker = None):
        """
        Update chunks for an existing chapter.
        
        Args:
            chapter: Chapter model instance
            new_content: New content to replace existing chunks
            chunker: Optional SimpleChunker instance
        """
        return ChunkManager.create_normal_chunks_for_chapter(chapter, new_content, chunker)
