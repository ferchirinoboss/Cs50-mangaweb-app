document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.page-container img');
    const leftZone = document.querySelector('.left-zone');
    const rightZone = document.querySelector('.right-zone');
    let currentIndex = 0;

    function updateImage(index) {
        images.forEach((img, i) => {
            img.classList.toggle('active', i === index);
        });
    }

    function goToNextImage() {
        if (currentIndex < images.length - 1) {
            currentIndex++;
            updateImage(currentIndex);
        }
    }

    function goToPreviousImage() {
        if (currentIndex > 0) {
            currentIndex--;
            updateImage(currentIndex);
        }
    }

    // Handle keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight') {
            goToNextImage();
        } else if (e.key === 'ArrowLeft') {
            goToPreviousImage();
        }
    });

    // Handle click zones
    leftZone.addEventListener('click', goToPreviousImage);
    rightZone.addEventListener('click', goToNextImage);
});