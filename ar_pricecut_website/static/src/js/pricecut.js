/** Hero enhancement only; Odoo owns search, accounts, cart and checkout. */
(() => {
    function init() {
        document.querySelectorAll('.pc-website .pc-hero').forEach((hero) => {
            if (hero.dataset.pcReady) return;
            hero.dataset.pcReady = 'true';
            const slides = [...hero.querySelectorAll('.pc-slide')];
            const dots = [...hero.querySelectorAll('[data-pc-slide]')];
            const pause = hero.querySelector('[data-pc-pause]');
            if (!slides.length || !pause) return;
            const media = window.matchMedia('(prefers-reduced-motion: reduce)');
            let current = 0, paused = media.matches, timer;
            const show = (index) => {
                current = index;
                slides.forEach((slide, i) => {
                    slide.classList.toggle('is-active', i === current);
                    slide.setAttribute('aria-hidden', String(i !== current));
                });
                dots.forEach((dot, i) => {
                    dot.classList.toggle('is-active', i === current);
                    dot.setAttribute('aria-pressed', String(i === current));
                });
            };
            const sync = () => {
                window.clearInterval(timer);
                pause.setAttribute('aria-label', paused ? 'Play photo rotation' : 'Pause photo rotation');
                pause.innerHTML = `<i class="fa fa-${paused ? 'play' : 'pause'}" aria-hidden="true"></i>`;
                if (!paused && !media.matches && !document.hidden && !hero.matches(':hover') && !hero.contains(document.activeElement)) {
                    timer = window.setInterval(() => {
                        if (!document.contains(hero)) { window.clearInterval(timer); return; }
                        show((current + 1) % slides.length);
                    }, 6500);
                }
            };
            dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); sync(); }));
            pause.addEventListener('click', () => { paused = !paused; sync(); });
            hero.addEventListener('mouseenter', sync);
            hero.addEventListener('mouseleave', sync);
            hero.addEventListener('focusin', sync);
            hero.addEventListener('focusout', () => window.setTimeout(sync, 0));
            document.addEventListener('visibilitychange', sync);
            media.addEventListener('change', () => { paused = media.matches; sync(); });
            show(0);
            sync();
        });
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, {once: true});
    else init();
})();
