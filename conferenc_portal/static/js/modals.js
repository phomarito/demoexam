(function () {
    function getModal(name) {
        return document.getElementById('modal-' + name);
    }

    window.openModal = function (name) {
        document.querySelectorAll('.modal-overlay').forEach(function (el) {
            el.classList.add('hidden');
        });
        var modal = getModal(name);
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    };

    function closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(function (el) {
            el.classList.add('hidden');
        });
        document.body.style.overflow = '';
    }

    document.addEventListener('click', function (e) {
        var openBtn = e.target.closest('[data-open-modal]');
        if (openBtn) {
            e.preventDefault();
            openModal(openBtn.getAttribute('data-open-modal'));
            return;
        }

        if (e.target.closest('[data-close-modal]') || e.target.classList.contains('modal-backdrop')) {
            closeAllModals();
            return;
        }

        var switchBtn = e.target.closest('[data-switch-modal]');
        if (switchBtn) {
            e.preventDefault();
            openModal(switchBtn.getAttribute('data-switch-modal'));
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });
})();
