document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('moodboard-grid');
    const totalImages = 26;
    
    // Simulate loading
    const loadingMessage = document.createElement('div');
    loadingMessage.className = 'loading';
    loadingMessage.textContent = 'INITIALIZING ASTRO CORE...';
    grid.appendChild(loadingMessage);

    setTimeout(() => {
        grid.removeChild(loadingMessage);
        loadImages();
    }, 1200);

    function loadImages() {
        // Base name + array of numbers 2-26
        const images = ['moodimage.jpg'];
        for (let i = 2; i <= totalImages; i++) {
            images.push(`moodimage_${i}.jpg`);
        }

        // Shuffle images for a more organic feel
        for (let i = images.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [images[i], images[j]] = [images[j], images[i]];
        }

        images.forEach((imgName, index) => {
            const item = document.createElement('div');
            item.className = 'mood-item';
            
            // Stagger animations based on index
            item.style.animationDelay = `${index * 0.05 + 0.5}s`;

            const img = document.createElement('img');
            img.className = 'mood-image';
            img.src = `assets/moodboard/${imgName}`;
            img.alt = `Cosmic Orange Moodboard Image ${index + 1}`;
            img.loading = 'lazy'; // Improve performance

            const overlay = document.createElement('div');
            overlay.className = 'item-overlay';
            
            // Randomly generated hex ID for aesthetic
            const hexId = Math.random().toString(16).substring(2, 8).toUpperCase();
            
            overlay.innerHTML = `
                <span class="item-label">SEC-${String(index + 1).padStart(2, '0')}</span>
                <span class="item-data">ID: ${hexId} // STATUS: ACTIVE</span>
            `;

            item.appendChild(img);
            item.appendChild(overlay);
            grid.appendChild(item);
        });
    }

    // Add glitch sound effect on hover to title (optional aesthetic touch)
    const title = document.querySelector('.glitch');
    title.addEventListener('mouseover', () => {
        title.style.animationDuration = '0.5s';
        setTimeout(() => {
            title.style.animationDuration = '5s';
        }, 500);
    });
});
