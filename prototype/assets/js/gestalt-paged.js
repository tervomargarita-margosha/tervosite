(() => {
  const story = document.querySelector('.gestalt-story');
  const header = document.querySelector('.site-header');
  const pages = [...story.querySelectorAll('.gs-page')];
  const segments = [...story.querySelectorAll('.gs-seg')];
  const progress = story.querySelector('#prog');
  const label = story.querySelector('#progLabel');
  const map = story.querySelector('#mapov');
  const mapButton = story.querySelector('#mapBtn');
  const narrow = matchMedia('(max-width: 900px)');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let current = -1;
  let frame = 0;

  const unitInterval = (value) => Math.min(1, Math.max(0, value));

  function updateProgress() {
    frame = 0;
    const page = pages[current];
    const remaining = page.offsetHeight - innerHeight + header.offsetHeight + progress.offsetHeight;
    const fraction = remaining > 0
      ? Math.max(0, Math.min(1, -page.getBoundingClientRect().top / remaining))
      : 1;

    segments.forEach((segment, index) => {
      segment.style.setProperty('--f', index < current ? 1 : index === current ? fraction : 0);
    });

    if (motion.matches) return;
    const top = header.offsetHeight + progress.offsetHeight;
    page.querySelectorAll('[data-swap]').forEach((figure) => {
      const section = figure.closest('.gs-split--inline-art');
      const rail = section.querySelector('.gs-split__grid').getBoundingClientRect();
      const available = innerHeight - top;
      const distance = Math.max(rail.height - available, 1);
      const amount = unitInterval((top - rail.top) / distance);
      section.style.setProperty('--gs-reading-top', top + 'px');
      figure.style.setProperty('--swap', amount);
      const travel = narrow.matches ? 0 : Math.max(available - figure.offsetHeight, 0);
      figure.style.setProperty('--swap-travel', (travel * amount) + 'px');
    });

    const flower = page.querySelector('[data-bloom]');
    if (flower && !narrow.matches) {
      const bounds = flower.closest('.gs-fin').getBoundingClientRect();
      const journey = Math.max(bounds.height - innerHeight * .5, 180);
      flower.style.setProperty('--bloom', unitInterval((top - bounds.top) / journey));
    }
  }

  function scheduleProgress() {
    if (!frame) frame = requestAnimationFrame(updateProgress);
  }

  const reveal = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('is-in');
      reveal.unobserve(entry.target);
    }
  }, { threshold: .1 });
  story.querySelectorAll('.gs-wc-breathe, .gs-fan__item, .gs-replicas li, .gs-ways').forEach((element) => {
    reveal.observe(element);
  });

  function showPage(index, target, moveFocus = false) {
    const page = pages[index];
    if (current !== index) {
      pages.forEach((item, position) => { item.hidden = position !== index; });
      current = index;
      label.textContent = page.dataset.label;
      progress.hidden = index === 0;
      document.title = (index === 0 ? '' : page.dataset.label + ' – ') + 'Гештальт простыми словами – Маргарита Терво';
    }

    if (moveFocus) {
      const heading = target?.querySelector('h1, h2, h3') || page.querySelector('h1, h2, h3');
      heading.tabIndex = -1;
      heading.focus({ preventScroll: true });
    }

    if (target && target !== page) target.scrollIntoView({ block: 'start', behavior: 'instant' });
    else window.scrollTo({ top: 0, behavior: 'instant' });
    scheduleProgress();
  }

  function readHash() {
    const id = location.hash.slice(1);
    const target = document.getElementById(id);
    const index = pages.indexOf(target?.closest('.gs-page'));
    if (index >= 0) showPage(index, target);
    else if (!id || current < 0) showPage(0);
  }

  function followPage(index, target) {
    const hash = '#' + target.id;
    if (location.hash !== hash) history.pushState(null, '', hash);
    showPage(index, target, true);
  }

  story.addEventListener('click', (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || event.defaultPrevented || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = document.getElementById(link.hash.slice(1));
    const index = pages.indexOf(target?.closest('.gs-page'));
    if (index < 0) return;

    event.preventDefault();
    if (map.open) map.close();
    followPage(index, target);
  });

  mapButton.addEventListener('click', () => {
    map.showModal();
    mapButton.setAttribute('aria-expanded', 'true');
  });
  story.querySelector('#mapClose').addEventListener('click', () => map.close());
  map.addEventListener('close', () => mapButton.setAttribute('aria-expanded', 'false'));

  window.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || map.open) return;
    if (event.target.closest?.('input, textarea, select, [contenteditable], .site-header')) return;
    const direction = event.key === 'ArrowLeft' ? -1 : event.key === 'ArrowRight' ? 1 : 0;
    const adjacent = pages[current + direction];
    if (!direction || !adjacent) return;
    event.preventDefault();
    followPage(current + direction, adjacent);
  });

  new ResizeObserver(() => {
    document.documentElement.style.setProperty('--gestalt-header-height', header.offsetHeight + 'px');
    scheduleProgress();
  }).observe(header);
  window.addEventListener('scroll', scheduleProgress, { passive: true });
  window.addEventListener('resize', scheduleProgress);
  window.addEventListener('hashchange', readHash);
  readHash();
})();
