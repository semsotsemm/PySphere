document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('coursesGrid');
    const cards = Array.from(document.querySelectorAll('.course-card'));

    // Елементы фильтров
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const priceMinInput = document.getElementById('priceMin');
    const priceMaxInput = document.getElementById('priceMax');
    const langCheckboxes = document.querySelectorAll('input[name="language"]');
    const levelRadios = document.querySelectorAll('input[name="difficulty"]');

    // Основная функция фильтрации
    function filterCards() {
        const searchText = searchInput.value.toLowerCase();
        const minPrice = parseFloat(priceMinInput.value) || 0;
        const maxPrice = parseFloat(priceMaxInput.value) || Infinity;

        // Получаем выбранные языки
        const selectedLangs = Array.from(langCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        // Получаем выбранный уровень
        const selectedLevel = document.querySelector('input[name="difficulty"]:checked').value;

        cards.forEach(card => {
            const title = card.querySelector('.course-card__title').textContent.toLowerCase();
            const listText = card.querySelector('.course-card__list').textContent.toLowerCase();
            const price = parseFloat(card.getAttribute('data-price'));
            const lang = card.getAttribute('data-lang');
            const level = card.getAttribute('data-level');

            // Логика проверок
            const matchesSearch = title.includes(searchText) || listText.includes(searchText);
            const matchesPrice = price >= minPrice && price <= maxPrice;
            const matchesLang = selectedLangs.length === 0 || selectedLangs.includes(lang);
            const matchesLevel = selectedLevel === 'all' || selectedLevel === level;

            if (matchesSearch && matchesPrice && matchesLang && matchesLevel) {
                card.style.display = 'block'; // Или 'flex' если нужно
            } else {
                card.style.display = 'none';
            }
        });

        sortCards(); // Сортируем видимые
    }

    // Функция сортировки
    function sortCards() {
        const sortValue = sortSelect.value;

        // Берем текущие видимые карточки (или все, если сортируем DOM)
        // Но лучше просто пересортировать массив cards и перевставить в DOM

        const sortedCards = cards.sort((a, b) => {
            const priceA = parseFloat(a.getAttribute('data-price'));
            const priceB = parseFloat(b.getAttribute('data-price'));

            if (sortValue === 'price-asc') {
                return priceA - priceB;
            } else if (sortValue === 'price-desc') {
                return priceB - priceA;
            } else {
                return 0; // По умолчанию (можно по порядку в DOM)
            }
        });

        // Перерисовываем DOM
        sortedCards.forEach(card => grid.appendChild(card));
    }

    // Вешаем слушатели событий
    searchInput.addEventListener('input', filterCards);
    sortSelect.addEventListener('change', filterCards); // При смене сортировки тоже прогоняем фильтр
    priceMinInput.addEventListener('input', filterCards);
    priceMaxInput.addEventListener('input', filterCards);

    langCheckboxes.forEach(cb => cb.addEventListener('change', filterCards));
    levelRadios.forEach(radio => radio.addEventListener('change', filterCards));
});