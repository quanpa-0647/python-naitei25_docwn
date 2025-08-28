import re
from typing import List, Tuple
from bs4 import BeautifulSoup, NavigableString
from constants import MAX_CHUNK_SIZE, HTML_TAG_OVERHEAD, BEAUTIFULSOUP_PARSER, HTML_BLOCK_ELEMENTS
from .helpers import count_words

class HtmlChunker:
    """
    A chunker specifically designed for HTML content that ensures each chunk contains valid HTML blocks.
    """
    
    def __init__(self, max_chunk_size: int = MAX_CHUNK_SIZE):
        """
        Initialize the HTML chunker.
        
        Args:
            max_chunk_size: Maximum size of each chunk in characters (default: MAX_CHUNK_SIZE for MySQL TEXT)
        """
        self.max_chunk_size = max_chunk_size
        
    def split_into_chunks(self, content: str) -> List[Tuple[str, int]]:
        """
        Split HTML content into chunks while maintaining valid HTML structure.
        
        Args:
            content: The HTML content to chunk
            
        Returns:
            List of tuples containing (chunk_content, word_count)
        """
        if not content or not content.strip():
            return []
            
        # Clean and normalize HTML content
        content = self._normalize_html_content(content)
        
        # Parse HTML content
        soup = BeautifulSoup(content, BEAUTIFULSOUP_PARSER)
        
        # Get all top-level elements
        elements = list(soup.children)
        
        # Group elements into chunks
        chunks = self._create_html_chunks(elements)
        
        # Calculate word counts for each chunk and clean up
        result = []
        for chunk_html in chunks:
            if chunk_html.strip():
                word_count = count_words(self._extract_text_from_html(chunk_html))
                result.append((chunk_html.strip(), word_count))
                
        return result
    
    def _normalize_html_content(self, content: str) -> str:
        """Normalize HTML content for proper chunking."""
        # Remove excessive whitespace between tags but preserve single spaces and line breaks
        # that might be important for word separation
        content = re.sub(r'>\s*\n\s*<', '> <', content)  # Replace newlines between tags with single space
        content = re.sub(r'>\s{2,}<', '> <', content)  # Replace multiple spaces between tags with single space
        
        # Normalize line breaks in text content
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        
        # Remove empty paragraphs
        content = re.sub(r'<p[^>]*>\s*</p>', '', content)
        
        return content.strip()
    
    def _create_html_chunks(self, elements: List) -> List[str]:
        """Create chunks by grouping HTML elements."""
        chunks = []
        current_chunk_elements = []
        current_size = 0
        
        for element in elements:
            if isinstance(element, NavigableString):
                # Include all NavigableString elements, even whitespace-only ones,
                # as they may be important for word separation
                element_html = str(element)
                element_size = len(element_html)
            else:
                element_html = str(element)
                element_size = len(element_html)
            
            # Check if adding this element would exceed the chunk size
            if current_size + element_size > self.max_chunk_size and current_chunk_elements:
                # Finalize current chunk
                chunk_html = ''.join(str(elem) for elem in current_chunk_elements)
                if chunk_html.strip():
                    chunks.append(chunk_html)
                
                # Start new chunk
                current_chunk_elements = [element]
                current_size = element_size
            else:
                # Add element to current chunk
                current_chunk_elements.append(element)
                current_size += element_size
        
        # Add the final chunk if it has content
        if current_chunk_elements:
            chunk_html = ''.join(str(elem) for elem in current_chunk_elements)
            if chunk_html.strip():
                chunks.append(chunk_html)
        
        # Ensure chunks don't exceed max size by splitting large elements if necessary
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split large chunks more aggressively
                split_chunks = self._split_large_chunk(chunk)
                final_chunks.extend(split_chunks)
        
        return final_chunks
    
    def _split_large_chunk(self, chunk_html: str) -> List[str]:
        """Split a large HTML chunk that exceeds the maximum size."""
        chunks = []
        soup = BeautifulSoup(chunk_html, BEAUTIFULSOUP_PARSER)
        
        # Try to split by paragraphs first
        paragraphs = soup.find_all(HTML_BLOCK_ELEMENTS)
        
        if paragraphs and len(paragraphs) > 1:
            # Split by paragraphs
            current_elements = []
            current_size = 0
            
            for p in paragraphs:
                p_html = str(p)
                p_size = len(p_html)
                
                if current_size + p_size > self.max_chunk_size and current_elements:
                    chunk = ''.join(current_elements)
                    if chunk.strip():
                        chunks.append(chunk)
                    current_elements = [p_html]
                    current_size = p_size
                else:
                    current_elements.append(p_html)
                    current_size += p_size
            
            if current_elements:
                chunk = ''.join(current_elements)
                if chunk.strip():
                    chunks.append(chunk)
        else:
            # If we can't split by paragraphs, split by text content more aggressively
            # This is a fallback for very long single elements
            text_content = soup.get_text()
            if len(text_content) > self.max_chunk_size:
                # Split the text and wrap in simple paragraphs
                words = text_content.split()
                current_words = []
                current_size = 0
                
                for word in words:
                    word_size = len(word) + 1  # +1 for space
                    
                    if current_size + word_size > self.max_chunk_size - HTML_TAG_OVERHEAD and current_words:  # Buffer for HTML tags
                        chunk_text = ' '.join(current_words)
                        chunks.append(f'<p>{chunk_text}</p>')
                        current_words = [word]
                        current_size = word_size
                    else:
                        current_words.append(word)
                        current_size += word_size
                
                if current_words:
                    chunk_text = ' '.join(current_words)
                    chunks.append(f'<p>{chunk_text}</p>')
            else:
                # Chunk is not too long after all, keep it as is
                chunks.append(chunk_html)
        
        return chunks
    
    def _extract_text_from_html(self, html: str) -> str:
        """Extract plain text from HTML for word counting."""
        soup = BeautifulSoup(html, BEAUTIFULSOUP_PARSER)
        return soup.get_text()
    
    def validate_html_chunk(self, chunk_html: str) -> bool:
        """Validate that a chunk contains valid HTML."""
        try:
            soup = BeautifulSoup(chunk_html, BEAUTIFULSOUP_PARSER)
            # Check if parsing was successful and no malformed tags
            return bool(soup)
        except Exception:
            return False
