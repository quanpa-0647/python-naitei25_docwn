class ChapterReader {
    constructor() {
        const data = window.chapterData;

        this.chapterId = data.chapterId;
        this.totalChunks = data.totalChunks;
        this.loadedChunks = data.loadedChunks;
        this.isAuthenticated = data.isAuthenticated;

        this.currentChunk = 1;
        this.startTime = Date.now();
        this.isLoading = false;
        this.scrollThreshold = 0.7;
        this.fontSize = 'medium';
        this.isDarkMode = false;
        this.isFullscreen = false;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupIntersectionObserver();
        this.loadSettings();
        this.updateStats();
    }

    setupEventListeners() {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        });

        document.getElementById('sidebarToggle')?.addEventListener('click', () => {
            this.toggleSidebar();
        });

        document.getElementById('fontSizeBtn')?.addEventListener('click', () => {
            this.cycleFontSize();
        });

        document.getElementById('darkModeBtn')?.addEventListener('click', () => {
            this.toggleDarkMode();
        });

        document.getElementById('bookmarkBtn')?.addEventListener('click', () => {
            this.toggleBookmark();
        });

        document.getElementById('fullscreenBtn')?.addEventListener('click', () => {
            this.toggleFullscreen();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft' && e.ctrlKey) {
                this.goToPrevChapter?.();
            } else if (e.key === 'ArrowRight' && e.ctrlKey) {
                this.goToNextChapter?.();
            } else if (e.key === 's' && e.ctrlKey) {
                e.preventDefault();
                this.toggleSidebar();
            }
        });
    }

    setupIntersectionObserver() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const position = parseInt(entry.target.dataset.position);
                    this.currentChunk = Math.max(this.currentChunk, position);
                    this.updateStats();
                    this.saveProgress(position);
                }
            });
        }, { threshold: 0.5 });

        document.querySelectorAll('.chunk').forEach(chunk => {
            observer.observe(chunk);
        });

        this.observer = observer;
    }

    handleScroll() {
        const scrollPercent = this.getScrollPercentage();
        document.getElementById('progressBar').style.width = scrollPercent + '%';

        if (scrollPercent > this.scrollThreshold * 100 && !this.isLoading) {
            this.loadMoreChunks();
        }
    }

    getScrollPercentage() {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        return Math.min((scrollTop / docHeight) * 100, 100);
    }

    async loadMoreChunks() {
        if (this.loadedChunks >= this.totalChunks || this.isLoading) return;

        this.isLoading = true;
        document.getElementById('loadingIndicator').style.display = 'block';

        try {
            const response = await fetch(
                `/novels/ajax/load-chunks/${this.chapterId}/?start=${this.loadedChunks}&limit=5`
            );
            const data = await response.json();

            const container = document.getElementById('chunksContainer');
            data.chunks.forEach(chunkData => {
                const chunkElement = this.createChunkElement(chunkData);
                container.appendChild(chunkElement);
                this.observer.observe(chunkElement);
            });

            this.loadedChunks += data.chunks.length;

        } catch (error) {
            console.error('Error loading chunks:', error);
        } finally {
            this.isLoading = false;
            document.getElementById('loadingIndicator').style.display = 'none';
        }
    }

    createChunkElement(chunkData) {
        const div = document.createElement('div');
        div.className = 'chunk';
        div.dataset.position = chunkData.position;
        // Content is already HTML, so set innerHTML directly without replacing newlines
        div.innerHTML = chunkData.content;
        return div;
    }

    updateStats() {
        document.getElementById('currentChunk').textContent = this.currentChunk;
        document.getElementById('totalChunks').textContent = this.totalChunks;

        const progress = Math.round((this.currentChunk / this.totalChunks) * 100);
        document.getElementById('readingProgress').textContent = progress + '%';
    }

    async saveProgress(chunkPosition) {
        if (!this.isAuthenticated) return;

        try {
            await fetch('/novels/ajax/save-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    chapter_id: this.chapterId,
                    chunk_position: chunkPosition,
                    reading_progress: (chunkPosition) / this.totalChunks
                })
            });
        } catch (error) {
            console.error('Error saving progress:', error);
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        const toggleBtn = document.getElementById('sidebarToggle');

        sidebar.classList.toggle('active');
        mainContent.classList.toggle('with-sidebar');
        toggleBtn.classList.toggle('with-sidebar');
    }

    cycleFontSize() {
        const sizes = ['small', 'medium', 'large', 'xlarge'];
        const currentIndex = sizes.indexOf(this.fontSize);
        const nextIndex = (currentIndex + 1) % sizes.length;

        document.body.className = document.body.className.replace(/font-\w+/, '');
        this.fontSize = sizes[nextIndex];
        document.body.classList.add(`font-${this.fontSize}`);

        this.saveSettings();
    }

    toggleDarkMode() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.isDarkMode = newTheme === 'dark';
        
        const btn = document.getElementById('darkModeBtn');
        btn.classList.toggle('active', this.isDarkMode);

        this.saveSettings();
    }

    toggleBookmark() {
        const btn = document.getElementById('bookmarkBtn');
        btn.classList.toggle('active');
    }

    toggleFullscreen() {
        const doc = document.documentElement;

        if (!document.fullscreenElement) {
            if (doc.requestFullscreen) {
                doc.requestFullscreen();
            } else if (doc.webkitRequestFullscreen) {
                doc.webkitRequestFullscreen();
            } else if (doc.msRequestFullscreen) {
                doc.msRequestFullscreen();
            }
            this.isFullscreen = true;
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
            this.isFullscreen = false;
        }

        // Cập nhật icon hoặc trạng thái nếu muốn
        const btn = document.getElementById('fullscreenBtn');
        btn.classList.toggle('active', this.isFullscreen);
    }

    saveSettings() {
        localStorage.setItem('readerSettings', JSON.stringify({
            fontSize: this.fontSize,
            isDarkMode: this.isDarkMode
        }));
    }

    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('readerSettings') || '{}');

        if (settings.fontSize) {
            this.fontSize = settings.fontSize;
            document.body.classList.add(`font-${this.fontSize}`);
        }

        // Load theme from localStorage (shared with main theme system)
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.isDarkMode = savedTheme === 'dark';
            document.documentElement.setAttribute('data-bs-theme', savedTheme);
            document.getElementById('darkModeBtn')?.classList.toggle('active', this.isDarkMode);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.chapterReader = new ChapterReader();
});
