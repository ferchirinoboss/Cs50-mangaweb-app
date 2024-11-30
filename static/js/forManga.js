document.addEventListener('DOMContentLoaded', () => {
    const volumeHeaders = document.querySelectorAll('.volume-header');

    volumeHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const chapters = header.nextElementSibling; // Find the chapters div
            if (chapters.style.height === '0px' || chapters.style.height === '') {
                chapters.style.height = 'auto'; // Show chapters
            } else {
                chapters.style.height = '0px'; // Hide chapters
            }
        });
   });
}); 