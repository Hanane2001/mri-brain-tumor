/* ═══════════════════════════════════════════════════════════
   Interactions & animations légères (pas de surcharge)
   ═══════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // 1. Compteur animé sur les KPI (easeOutExpo)
    function animateCounters() {
        const els = document.querySelectorAll('[data-counter]');
        els.forEach((el) => {
            if (el.dataset.animated === 'true') return;
            const target = parseFloat(el.dataset.counter);
            const suffix = el.dataset.suffix || '';
            const decimals = parseInt(el.dataset.decimals || '0', 10);
            if (isNaN(target)) return;
            el.dataset.animated = 'true';

            const duration = 900;
            const start = performance.now();

            function tick(now) {
                const t = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(2, -10 * t);  // easeOutExpo
                const value = target * eased;
                el.textContent = value.toFixed(decimals) + suffix;
                if (t < 1) requestAnimationFrame(tick);
                else el.textContent = target.toFixed(decimals) + suffix;
            }
            requestAnimationFrame(tick);
        });
    }

    // 2. Reveal progressif au scroll
    function setupReveal() {
        const io = new IntersectionObserver(
            (entries) => {
                entries.forEach((e) => {
                    if (e.isIntersecting) {
                        e.target.classList.add('nv-reveal');
                        io.unobserve(e.target);
                    }
                });
            },
            { threshold: 0.08 }
        );
        document.querySelectorAll('.nv-kpi, .nv-panel').forEach((el) => io.observe(el));
    }

    // 3. Légère parallaxe sur les KPI (subtile)
    function setupParallax() {
        document.addEventListener('mousemove', (e) => {
            const cards = document.querySelectorAll('.nv-kpi');
            const cx = window.innerWidth / 2;
            const cy = window.innerHeight / 2;
            const dx = (e.clientX - cx) / cx;
            const dy = (e.clientY - cy) / cy;
            cards.forEach((card, i) => {
                const depth = (i % 4) * 0.4 + 0.6;
                card.style.transform =
                    `translateY(-2px) rotateX(${dy * -1.5 * depth}deg) rotateY(${dx * 1.5 * depth}deg)`;
            });
        });
    }

    // 4. Nettoyage : retirer transform au mouseleave
    function setupReset() {
        document.addEventListener('mouseleave', () => {
            document.querySelectorAll('.nv-kpi').forEach((c) => {
                c.style.transform = '';
            });
        });
    }

    // 5. Observation DOM (Streamlit re-render)
    function init() {
        animateCounters();
        setupReveal();
    }

    // Ré-initialiser à chaque re-render Streamlit
    const mo = new MutationObserver(() => {
        animateCounters();
    });
    mo.observe(document.body, { childList: true, subtree: true });

    document.addEventListener('DOMContentLoaded', () => {
        init();
        setupParallax();
        setupReset();
    });
})();