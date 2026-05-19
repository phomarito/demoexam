(function () {
    var INTERVAL = 3000;

    document.querySelectorAll('[data-slider]').forEach(function (container) {
        var viewport = container.querySelector('.slider-viewport');
        var track = container.querySelector('.slider-track');
        var slides = container.querySelectorAll('.slider-slide');
        var prevBtn = container.querySelector('.slider-btn-prev');
        var nextBtn = container.querySelector('.slider-btn-next');
        var dotsContainer = container.querySelector('.slider-dots');
        var counter = container.querySelector('.slider-counter');
        var progressBar = container.querySelector('.slider-progress-bar');

        var total = slides.length;
        var current = 0;
        var timer = null;
        var progressTimer = null;
        var progressStart = 0;

        if (!track || total === 0) return;

        function slideWidth() {
            return viewport ? viewport.offsetWidth : container.offsetWidth;
        }

        function goTo(index) {
            current = ((index % total) + total) % total;
            var offset = current * slideWidth();
            track.style.transform = 'translate3d(-' + offset + 'px, 0, 0)';

            if (dotsContainer) {
                dotsContainer.querySelectorAll('.slider-dot').forEach(function (dot, i) {
                    dot.classList.toggle('active', i === current);
                    dot.setAttribute('aria-selected', i === current ? 'true' : 'false');
                });
            }

            if (counter) {
                counter.textContent = (current + 1) + ' / ' + total;
            }

            resetProgress();
        }

        function next() { goTo(current + 1); }
        function prev() { goTo(current - 1); }

        function startAuto() {
            stopAuto();
            timer = setInterval(next, INTERVAL);
            resetProgress();
        }

        function stopAuto() {
            if (timer) clearInterval(timer);
            if (progressTimer) cancelAnimationFrame(progressTimer);
        }

        function resetProgress() {
            if (!progressBar) return;
            progressStart = performance.now();
            progressBar.style.width = '0%';

            function tick(now) {
                var elapsed = now - progressStart;
                var pct = Math.min((elapsed / INTERVAL) * 100, 100);
                progressBar.style.width = pct + '%';
                if (pct < 100) {
                    progressTimer = requestAnimationFrame(tick);
                }
            }

            if (progressTimer) cancelAnimationFrame(progressTimer);
            progressTimer = requestAnimationFrame(tick);
        }

        if (dotsContainer) {
            for (var i = 0; i < total; i++) {
                var dot = document.createElement('button');
                dot.type = 'button';
                dot.className = 'slider-dot' + (i === 0 ? ' active' : '');
                dot.setAttribute('role', 'tab');
                dot.setAttribute('aria-label', 'Слайд ' + (i + 1));
                dot.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
                (function (idx) {
                    dot.addEventListener('click', function () {
                        goTo(idx);
                        startAuto();
                    });
                })(i);
                dotsContainer.appendChild(dot);
            }
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', function () {
                prev();
                startAuto();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                next();
                startAuto();
            });
        }

        container.addEventListener('mouseenter', stopAuto);
        container.addEventListener('mouseleave', startAuto);

        var resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                goTo(current);
            }, 100);
        });

        goTo(0);
        startAuto();
    });
})();
