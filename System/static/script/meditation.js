document.addEventListener("DOMContentLoaded", function () {
    const boxes = document.querySelectorAll('.rectangle-box');
    const itemsPerPage = 8;
    let currentPage = 1;

    function showPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;

        boxes.forEach((box, index) => {
            if (index >= start && index < end) {
                box.style.display = 'block';
            } else {
                box.style.display = 'none';
            }
        });
    }

    function setupPagination() {
        const totalPages = Math.ceil(boxes.length / itemsPerPage);
        const paginationElement = document.getElementById('pagination');

        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.innerText = i;
            li.addEventListener('click', () => {
                currentPage = i;
                showPage(currentPage);
                updatePaginationStyles();
            });
            paginationElement.appendChild(li);
        }

        updatePaginationStyles();
    }

    function updatePaginationStyles() {
        const paginationItems = document.querySelectorAll('.pagination li');
        paginationItems.forEach((item, index) => {
            if (index + 1 === currentPage) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }

    // Initialize pagination
    showPage(currentPage);
    setupPagination();
});