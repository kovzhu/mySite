/**
 * Text Rotation Script
 * Handles fade-in/fade-out transitions for rotating hero text paragraphs
 */

class TextRotator {
    constructor(elementId, configPath) {
        this.textElement = document.getElementById(elementId);
        if (!this.textElement) {
            console.error(`Element with id "${elementId}" not found`);
            return;
        }

        this.paragraphs = [];
        this.currentIndex = 0;
        this.rotationInterval = 5000; // default 5 seconds
        this.fadeTransitionDuration = 800; // default 800ms
        this.intervalId = null;

        // Load configuration and start rotation
        this.loadConfig(configPath);
    }

    async loadConfig(configPath) {
        try {
            const response = await fetch(configPath);
            const config = await response.json();

            this.paragraphs = config.paragraphs || [];
            this.rotationInterval = config.rotationInterval || 5000;
            this.fadeTransitionDuration = config.fadeTransitionDuration || 800;

            if (this.paragraphs.length > 0) {
                // Set the first paragraph immediately
                this.showParagraph(0);

                // Start rotation if there's more than one paragraph
                if (this.paragraphs.length > 1) {
                    this.startRotation();
                }
            } else {
                console.warn('No paragraphs found in configuration');
            }
        } catch (error) {
            console.error('Error loading rotation config:', error);
            // Fallback to default text if loading fails
            this.textElement.style.opacity = '1';
        }
    }

    showParagraph(index) {
        if (index < 0 || index >= this.paragraphs.length) return;

        const paragraph = this.paragraphs[index];
        this.textElement.textContent = paragraph.text;

        // Optional: You can also display the author if needed
        // For now, we're just showing the text
    }

    fadeOut() {
        return new Promise((resolve) => {
            this.textElement.style.transition = `opacity ${this.fadeTransitionDuration}ms ease-in-out`;
            this.textElement.style.opacity = '0';
            setTimeout(resolve, this.fadeTransitionDuration);
        });
    }

    fadeIn() {
        return new Promise((resolve) => {
            this.textElement.style.transition = `opacity ${this.fadeTransitionDuration}ms ease-in-out`;
            this.textElement.style.opacity = '1';
            setTimeout(resolve, this.fadeTransitionDuration);
        });
    }

    async rotateParagraph() {
        // Fade out current text
        await this.fadeOut();

        // Update to next paragraph
        this.currentIndex = (this.currentIndex + 1) % this.paragraphs.length;
        this.showParagraph(this.currentIndex);

        // Fade in new text
        await this.fadeIn();
    }

    startRotation() {
        // Clear any existing interval
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }

        // Start new rotation interval
        this.intervalId = setInterval(() => {
            this.rotateParagraph();
        }, this.rotationInterval);
    }

    stopRotation() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    // Public method to manually change paragraph
    goToParagraph(index) {
        if (index >= 0 && index < this.paragraphs.length) {
            this.currentIndex = index;
            this.fadeOut().then(() => {
                this.showParagraph(this.currentIndex);
                this.fadeIn();
            });
        }
    }
}

// Initialize the text rotator when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    // Initialize with the hero-text element
    const rotator = new TextRotator(
        'hero-rotating-text',
        '/static/rotating_texts.json'
    );

    // Make it globally accessible if needed
    window.textRotator = rotator;
});
