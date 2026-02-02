const getCourses = async () => {
    courses = await fetch("http://127.0.0.1:8000/api/courses");
}

document.addEventListener('DOMContentLoaded', () => {
    getCourses();
    const featureData = {
        1: {
            title: "Большой выбор направлений",
            desc: "Открой для себя мир Python: Django, FastAPI, Data Science и Machine Learning. — Масштабируйся в смежные сферы: JS/Frontend, системный C++, SQL и работа с Docker. — Всё в одном месте: база данных PostgreSQL и основы DevOps для создания готовых продуктов.",
            img: "images/image1.png"
        },
        2: {
            title: "Круглосуточная поддержка",
            desc: "Возник вопрос? Напиши преподавателю прямо в интерактивном окне на сайте и получи быстрый разбор задачи. Тебе не нужно ждать часами на форумах экспертная помощь доступна в процессе написания кода. Живое общение с профи помогает избежать ошибок и в 1.6 раза ускоряет прохождение сложных тем.",
            img: "images/image2.png"
        },
        3: {
            title: "Когнитивная психология в коде",
            desc: "Наша методика задействует три вида памяти: визуальную (чтение), механическую (код) и вербальную (решение). Учтена «кривая забывания» Эббингауза: система напомнит о теме именно тогда, когда это нужно для закрепления. Мы строим нейронные связи, а не просто заставляем копировать код из видеоуроков.",
            img: "images/image3.png"
        },
        4: {
            title: "Инвестиция в твое будущее",
            desc: "Стартуй с уверенной отметки: средняя зарплата Junior-выпускника начинается от 100 000 ₽. Мы готовим тебя к росту: с каждым годом стажа твой доход будет расти экспоненциально. Владение широким стеком (Python + БД + Docker) делает тебя незаменимым и дорогим специалистом.",
            img: "images/image4.png"
        }
    };

    /* =========================================
       2. МОБИЛЬНОЕ МЕНЮ (БУРГЕР)
       ========================================= */
    const burgerBtn = document.querySelector('.header__burger');
    const nav = document.querySelector('.nav');

    if (burgerBtn) {
        burgerBtn.addEventListener('click', () => {
            burgerBtn.classList.toggle('active');
            nav.classList.toggle('active');
            document.body.classList.toggle('no-scroll');
        });
    }

    /* =========================================
       3. МОДАЛЬНОЕ ОКНО
       ========================================= */
    const modal = document.getElementById('courseModal');
    const infoView = document.getElementById('infoView');
    const paymentView = document.getElementById('paymentView');
    const closeBtn = document.querySelector('.modal__close');
    const backBtn = document.querySelector('.modal__back-link');
    const buyActionBtn = document.querySelector('.modal__action-btn');
    const modalPriceBox = document.querySelector('.modal__price-box');

    // Элементы внутри модалки
    const domModalTitle = document.getElementById('modalTitle');
    const domModalDesc = document.getElementById('modalDesc');
    const domModalOldPrice = document.getElementById('modalOldPrice');
    const domModalNewPrice = document.getElementById('modalNewPrice');
    const domModalIcon = document.getElementById('modalIcon');
    const domPaymentName = document.getElementById('paymentCourseName');
    const domFinalPrice = document.getElementById('finalPrice');

    function openModal() {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        setTimeout(() => showInfoView(), 300); // Сброс вида после анимации
    }

    function showInfoView() {
        infoView.style.display = 'flex';
        paymentView.style.display = 'none';
    }

    function showPaymentView() {
        infoView.style.display = 'none';
        paymentView.style.display = 'flex';
    }

    // Обработчик закрытия
    closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    if (backBtn) backBtn.addEventListener('click', showInfoView);
    if (buyActionBtn) buyActionBtn.addEventListener('click', showPaymentView);


    // 3.1 КЛИК ПО КАРТОЧКАМ КУРСОВ (Динамический контент)
    document.querySelectorAll('.course-card').forEach(card => {
        // Кнопка "Подробнее"
        const detailsBtn = card.querySelector('.js-details-btn');
        // Кнопка "Записаться"
        const buyBtn = card.querySelector('.js-buy-btn');

        const fillModalData = () => {
            const title = card.querySelector('.course-card__title').innerText;
            const desc = "ddddd";
            const oldP = card.querySelector('.price-box__old').innerText;
            const newP = card.querySelector('.price-box__new').innerText;
            const iconSrc = card.querySelector('.course-card__icon').src;

            domModalTitle.innerText = title;
            domModalDesc.innerText = desc;
            domModalOldPrice.innerText = oldP;
            domModalNewPrice.innerText = newP;
            domModalIcon.src = iconSrc;
            domPaymentName.innerText = title;
            domFinalPrice.innerText = newP;

            // Показываем цену и кнопку покупки (для курсов они нужны)
            modalPriceBox.style.display = 'flex';
            if (buyActionBtn) buyActionBtn.style.display = 'block';
        };

        if (detailsBtn) {
            detailsBtn.addEventListener('click', () => {
                fillModalData();
                showInfoView();
                openModal();
            });
        }

        if (buyBtn) {
            buyBtn.addEventListener('click', () => {
                fillModalData();
                showPaymentView();
                openModal();
            });
        }
    });

    // 3.2 КЛИК ПО ИНФО-БЛОКАМ (Feature Buttons)
    document.querySelectorAll('.js-feature-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            const data = featureData[id];

            if (data) {
                domModalTitle.innerText = data.title;
                domModalDesc.innerText = data.desc;
                domModalIcon.src = data.img;

                // Скрываем цену и кнопку покупки (для инфо-блоков не нужны)
                modalPriceBox.style.display = 'none';
                if (buyActionBtn) buyActionBtn.style.display = 'none';

                showInfoView();
                openModal();
            }
        });
    });


    const sliderTrack = document.getElementById('effSlider');
    const dots = document.querySelectorAll('.slider-dot');
    const sliderContainer = document.querySelector('.slider-wrapper');

    if (sliderTrack && dots.length > 0) {
        let startX = 0;

        function goToSlide(index) {
            sliderTrack.style.transform = `translateX(-${index * 50}%)`;
            dots.forEach(d => d.classList.remove('active'));
            dots[index].classList.add('active');
        }

        dots.forEach((dot, i) => dot.addEventListener('click', () => goToSlide(i)));

        // Универсальный обработчик начала касания/клика
        const handleStart = (e) => {
            startX = e.type.includes('mouse') ? e.pageX : e.touches[0].clientX;
        };

        // Универсальный обработчик конца
        const handleEnd = (e) => {
            const endX = e.type.includes('mouse') ? e.pageX : e.changedTouches[0].clientX;
            const diff = startX - endX;

            if (Math.abs(diff) > 50) {
                diff > 0 ? goToSlide(1) : goToSlide(0);
            }
        };

        sliderContainer.addEventListener('mousedown', handleStart);
        sliderContainer.addEventListener('mouseup', handleEnd);
        sliderContainer.addEventListener('touchstart', handleStart, { passive: true });
        sliderContainer.addEventListener('touchend', handleEnd);
    }
});