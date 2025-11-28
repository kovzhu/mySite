// Gallery Modal JavaScript - Shared across all collections

class GalleryModal {
    constructor(deleteUrlTemplate) {
        this.modal = document.getElementById("photoModal");
        this.modalImg = document.getElementById("modalImg");
        this.modalTitle = document.getElementById("modalTitle");
        this.modalDate = document.getElementById("modalDate");
        this.modalDescriptionText = document.getElementById("modalDescriptionText");
        this.modalDescription = document.getElementById("modalDescription");
        this.prevBtn = document.getElementById("prevBtn");
        this.nextBtn = document.getElementById("nextBtn");
        this.deleteForm = document.getElementById("deleteForm");
        this.deleteUrlTemplate = deleteUrlTemplate;
        
        this.currentPhotoIndex = 0;
        this.allPhotoCards = [];
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Close modal if clicking outside the image content
        window.onclick = (event) => {
            if (event.target == this.modal) {
                this.closeModal();
            }
        };
        
        // Ensure body overflow is reset when leaving the page
        window.addEventListener('beforeunload', () => {
            document.body.style.overflow = 'auto';
        });
        
        // Keyboard Navigation
        document.addEventListener('keydown', (event) => {
            if (this.modal.style.display === "block") {
                if (event.key === "ArrowLeft") {
                    this.navigatePhoto(-1);
                } else if (event.key === "ArrowRight") {
                    this.navigatePhoto(1);
                } else if (event.key === "Escape") {
                    this.closeModal();
                }
            }
        });
    }
    
    openModal(card) {
        // Get all photo cards for navigation
        this.allPhotoCards = Array.from(document.querySelectorAll('.collection-card'));
        this.currentPhotoIndex = this.allPhotoCards.indexOf(card);
        
        // Load the photo
        this.loadPhotoAtIndex(this.currentPhotoIndex);
        
        // Show modal
        this.modal.style.display = "block";
        // Disable background scrolling
        document.body.style.overflow = "hidden";
        
        // Update navigation buttons
        this.updateNavButtons();
    }
    
    loadPhotoAtIndex(index) {
        const card = this.allPhotoCards[index];
        const fullImageSrc = card.getAttribute('data-full-image');
        const title = card.querySelector('.collection-title').innerText;
        const date = card.querySelector('.collection-description').innerText;
        const description = card.getAttribute('data-description');
        const photoId = card.getAttribute('data-photo-id');
        
        // Populate modal
        this.modalImg.src = fullImageSrc;
        this.modalTitle.innerText = title;
        this.modalDate.innerText = date;
        
        // Update delete form action
        if (this.deleteForm && this.deleteUrlTemplate) {
            this.deleteForm.action = this.deleteUrlTemplate.replace('0', photoId);
        }
        
        // Show description only if it exists
        if (description && description.trim() !== '') {
            this.modalDescriptionText.innerText = description;
            this.modalDescription.style.display = 'block';
        } else {
            this.modalDescription.style.display = 'none';
        }
    }
    
    navigatePhoto(direction) {
        this.currentPhotoIndex += direction;
        
        // Ensure we stay within bounds
        if (this.currentPhotoIndex < 0) this.currentPhotoIndex = 0;
        if (this.currentPhotoIndex >= this.allPhotoCards.length) this.currentPhotoIndex = this.allPhotoCards.length - 1;
        
        this.loadPhotoAtIndex(this.currentPhotoIndex);
        this.updateNavButtons();
    }
    
    updateNavButtons() {
        // Disable prev button if at first photo
        this.prevBtn.disabled = (this.currentPhotoIndex === 0);
        // Disable next button if at last photo
        this.nextBtn.disabled = (this.currentPhotoIndex === this.allPhotoCards.length - 1);
    }
    
    closeModal() {
        this.modal.style.display = "none";
        // Re-enable background scrolling
        document.body.style.overflow = "auto";
    }
}

// Global function to open modal (for backward compatibility)
function openModal(card) {
    if (!window.galleryModal) {
        console.error('GalleryModal not initialized. Call initGalleryModal() first.');
        return;
    }
    window.galleryModal.openModal(card);
}

// Global function to close modal
function closeModal() {
    if (!window.galleryModal) {
        console.error('GalleryModal not initialized. Call initGalleryModal() first.');
        return;
    }
    window.galleryModal.closeModal();
}

// Global function to navigate photos
function navigatePhoto(direction) {
    if (!window.galleryModal) {
        console.error('GalleryModal not initialized. Call initGalleryModal() first.');
        return;
    }
    window.galleryModal.navigatePhoto(direction);
}

// Initialize the gallery modal
function initGalleryModal(deleteUrlTemplate = null) {
    window.galleryModal = new GalleryModal(deleteUrlTemplate);
}
