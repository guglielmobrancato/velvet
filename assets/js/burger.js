document.addEventListener('DOMContentLoaded', () => {
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');

    if (burger && nav) {
        burger.addEventListener('click', () => {
            // Toggle Navigation Menu
            nav.classList.toggle('nav-active');
            // Toggle Burger Animation
            burger.classList.toggle('toggle');
        });
    }
});
