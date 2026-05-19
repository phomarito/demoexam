(function () {
    var modal = document.getElementById('admin-status-modal');
    if (!modal) return;

    var form = document.getElementById('admin-status-form');
    var bookingInput = document.getElementById('admin-booking-id');
    var statusSelect = document.getElementById('admin-status-select');
    var info = document.getElementById('admin-modal-info');

    function openModal(bookingId, currentStatus, user, room) {
        bookingInput.value = bookingId;
        statusSelect.value = currentStatus;
        info.textContent = 'Заявка #' + bookingId + ' — ' + user + ', зал «' + room + '»';
        modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }

    document.querySelectorAll('[data-admin-modal]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            openModal(
                btn.getAttribute('data-admin-modal'),
                btn.getAttribute('data-current'),
                btn.getAttribute('data-user'),
                btn.getAttribute('data-room')
            );
        });
    });

    document.querySelectorAll('[data-close-admin-modal]').forEach(function (el) {
        el.addEventListener('click', closeModal);
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeModal();
    });
})();
