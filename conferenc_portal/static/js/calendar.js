(function () {
    var app = document.getElementById('calendar-app');
    if (!app) return;

    var roomId = app.dataset.roomId;
    var availabilityUrl = app.dataset.availabilityUrl;
    var calBody = document.getElementById('cal-body');
    var calTitle = document.getElementById('cal-title');
    var slotsPanel = document.getElementById('slots-panel');
    var slotsList = document.getElementById('slots-list');
    var dateLabel = document.getElementById('selected-date-label');
    var bookingLink = document.getElementById('booking-link');

    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth();
    var occupied = {};
    var selectedDate = null;
    var selectedTime = null;

    var MONTHS = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ];

    var DEFAULT_SLOTS = ['09:00', '11:00', '14:00', '16:00', '18:00'];

    function pad(n) { return n < 10 ? '0' + n : '' + n; }

    function formatDateKey(y, m, d) {
        return y + '-' + pad(m + 1) + '-' + pad(d);
    }

    function formatDisplayDate(key) {
        var p = key.split('-');
        return pad(parseInt(p[2], 10)) + '.' + pad(parseInt(p[1], 10)) + '.' + p[0];
    }

    function fetchAvailability() {
        return fetch(availabilityUrl + '?year=' + year + '&month=' + (month + 1))
            .then(function (r) { return r.json(); })
            .then(function (data) {
                occupied = data.occupied || {};
                renderCalendar();
            });
    }

    function renderCalendar() {
        calTitle.textContent = MONTHS[month] + ' ' + year;
        calBody.innerHTML = '';
        var first = new Date(year, month, 1);
        var startDay = (first.getDay() + 6) % 7;
        var daysInMonth = new Date(year, month + 1, 0).getDate();
        var row = document.createElement('tr');
        var cell = 0;

        for (var i = 0; i < startDay; i++) {
            row.appendChild(emptyCell());
            cell++;
        }

        for (var d = 1; d <= daysInMonth; d++) {
            if (cell === 7) {
                calBody.appendChild(row);
                row = document.createElement('tr');
                cell = 0;
            }
            var key = formatDateKey(year, month, d);
            var td = document.createElement('td');
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'cal-day w-full';
            btn.textContent = d;

            var dayDate = new Date(year, month, d);
            var today = new Date();
            today.setHours(0, 0, 0, 0);

            if (dayDate < today) {
                btn.classList.add('cal-past');
            } else {
                if (occupied[key] && occupied[key].length > 0) {
                    btn.classList.add('cal-has-busy');
                }
                if (selectedDate === key) {
                    btn.classList.add('cal-selected');
                }
                (function (dateKey) {
                    btn.addEventListener('click', function () {
                        selectDate(dateKey);
                    });
                })(key);
            }
            td.appendChild(btn);
            row.appendChild(td);
            cell++;
        }

        while (cell < 7) {
            row.appendChild(emptyCell());
            cell++;
        }
        calBody.appendChild(row);
    }

    function emptyCell() {
        var td = document.createElement('td');
        td.className = 'cal-empty';
        return td;
    }

    function selectDate(dateKey) {
        selectedDate = dateKey;
        selectedTime = null;
        renderCalendar();
        renderSlots(dateKey);
    }

    function renderSlots(dateKey) {
        slotsPanel.classList.remove('hidden');
        dateLabel.textContent = formatDisplayDate(dateKey);
        slotsList.innerHTML = '';
        bookingLink.classList.add('hidden');

        var busy = occupied[dateKey] || [];

        DEFAULT_SLOTS.forEach(function (time) {
            var li = document.createElement('li');
            if (busy.indexOf(time) !== -1) {
                li.className = 'slot-busy';
                li.textContent = time + ' — занято';
            } else {
                var btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'slot-free';
                btn.textContent = time;
                (function (t) {
                    btn.addEventListener('click', function () {
                        slotsList.querySelectorAll('.slot-free').forEach(function (el) {
                            el.classList.remove('selected');
                        });
                        btn.classList.add('selected');
                        selectedTime = t;
                        bookingLink.href = '/booking/new/?room=' + roomId +
                            '&date=' + encodeURIComponent(formatDisplayDate(dateKey)) +
                            '&time=' + encodeURIComponent(t);
                        bookingLink.classList.remove('hidden');
                    });
                })(time);
                li.appendChild(btn);
            }
            slotsList.appendChild(li);
        });
    }

    document.getElementById('cal-prev').addEventListener('click', function () {
        month--;
        if (month < 0) { month = 11; year--; }
        fetchAvailability();
    });

    document.getElementById('cal-next').addEventListener('click', function () {
        month++;
        if (month > 11) { month = 0; year++; }
        fetchAvailability();
    });

    fetchAvailability();
})();
