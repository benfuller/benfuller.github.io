// Projects filter, in-page navigation, search palette (Ctrl/Cmd+K) and print helper.
(function () {
  var cfg = JSON.parse(document.getElementById('site-config').textContent);
  var UI = cfg.ui;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var list = document.getElementById('proj-list');
  var cards = list ? [].slice.call(list.querySelectorAll('.proj')) : [];
  var state = { company: '', skill: '' };

  function flash(node) {
    if (!node) return;
    node.classList.remove('flash'); void node.offsetWidth; node.classList.add('flash');
    setTimeout(function () { node.classList.remove('flash'); }, 1800);
  }
  function scrollTo(node) {
    if (!node) return;
    node.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  }

  // a link like #q-lead opens that answer
  (function () {
    var t = location.hash && document.getElementById(location.hash.slice(1));
    if (t && t.tagName === 'DETAILS') t.open = true;
  })();

  /* ------------------------------------------------------------ filters */
  function applyFilters(updateUrl) {
    var n = 0;
    cards.forEach(function (c) {
      var ok = (!state.company || c.dataset.company === state.company) &&
               (!state.skill || c.dataset.skills.split(' ').indexOf(state.skill) > -1);
      c.hidden = !ok; if (ok) n++;
    });
    var box = document.getElementById('filters');
    [].forEach.call(box.querySelectorAll('.chip'), function (b) {
      b.setAttribute('aria-pressed', String(state[b.dataset.kind] === b.dataset.value));
    });
    [].forEach.call(list.querySelectorAll('.tag, .co-chip'), function (b) {
      var v = b.dataset.skill || b.dataset.company, kind = b.dataset.skill ? 'skill' : 'company';
      b.classList.toggle('on', state[kind] === v);
    });
    var active = state.company || state.skill;
    var label = active ? UI.count.replace('{n}', n).replace('{total}', cards.length) : UI.total.replace('{total}', cards.length);
    document.getElementById('f-count').textContent = label;
    document.getElementById('f-clear').hidden = !active;
    if (state.skill) document.getElementById('skillfilter').open = true;
    if (updateUrl) {
      var q = [];
      if (state.company) q.push('company=' + encodeURIComponent(state.company));
      if (state.skill) q.push('skill=' + encodeURIComponent(state.skill));
      try { history.replaceState(null, '', location.pathname + (q.length ? '?' + q.join('&') : '') + location.hash); } catch (e) {}
    }
  }
  function setFilter(kind, value, toggle) {
    state[kind] = toggle && state[kind] === value ? '' : value;
    applyFilters(true);
  }
  function openCard(id) {
    state.company = state.skill = '';
    applyFilters(true);
    var card = document.getElementById('p-' + id);
    if (!card) return;
    var d = card.querySelector('details'); if (d) d.open = true;
    scrollTo(card); flash(card);
  }

  /* ------------------------------------------------- in-page navigation */
  // Returns true when the URL points at this page and was handled without a reload.
  function navigate(url) {
    var u; try { u = new URL(url, location.href); } catch (e) { return false; }
    if (u.origin !== location.origin || u.pathname !== location.pathname) return false;
    var p = u.searchParams, id = u.hash.replace('#', '');
    if (list && p.get('project')) { openCard(p.get('project')); return true; }
    if (list && (p.has('company') || p.has('skill'))) {
      state.company = p.get('company') || ''; state.skill = p.get('skill') || '';
      applyFilters(true); scrollTo(document.getElementById('projects')); return true;
    }
    var node = id && document.getElementById(id);
    if (node) {
      var group = node.closest('details'); if (group) group.open = true;
      history.pushState(null, '', u.pathname + u.hash);
      scrollTo(node); flash(node.classList.contains('job') || node.classList.contains('proj') || node.classList.contains('qa') ? node : null);
      return true;
    }
    return false;
  }

  document.addEventListener('click', function (e) {
    var n = e.target.closest('a[data-nav]');
    if (n && !e.metaKey && !e.ctrlKey && !e.shiftKey && navigate(n.href)) e.preventDefault();
  });

  /* ---------------------------------------------------------- timeline */
  var tl = document.getElementById('tl-toggles');
  if (tl) {
    tl.hidden = false;
    var items = [].slice.call(document.querySelectorAll('#vt > li'));
    var syncTl = function () {
      var on = {};
      [].forEach.call(tl.querySelectorAll('input[data-tl]'), function (i) { on[i.dataset.tl] = i.checked; });
      items.forEach(function (li) { if (li.dataset.type) li.hidden = !on[li.dataset.type]; });
      items.forEach(function (li, i) {            // hide a year label when none of its events are visible
        if (!li.classList.contains('yr')) return;
        var any = false;
        for (var k = i + 1; k < items.length && !items[k].classList.contains('yr'); k++) if (!items[k].hidden) any = true;
        li.hidden = !any;
      });
    };
    tl.addEventListener('change', syncTl);
    syncTl();
  }

  /* --------------------------------------- back to top, sticky header */
  var topBtn = document.createElement('button');
  topBtn.type = 'button'; topBtn.className = 'to-top'; topBtn.setAttribute('aria-label', UI.top); topBtn.textContent = '\u2191';
  document.body.appendChild(topBtn);
  topBtn.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); });
  var hdr = document.querySelector('header.top'), lastY = window.scrollY;
  function onScroll() {
    var y = window.scrollY;
    topBtn.classList.toggle('show', y > 700);
    if (hdr) {
      var mobile = window.matchMedia('(max-width: 700px)').matches;
      if (hdr.classList.contains('menu-open')) { lastY = y; return; }
      if (mobile && y > lastY + 6 && y > 120) hdr.classList.add('hide');
      else if (y < lastY - 6 || y < 120) hdr.classList.remove('hide');
    }
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if (list) {
    document.getElementById('filters').hidden = false;
    document.addEventListener('click', function (e) {
      var chip = e.target.closest('#filters .chip');
      if (chip) { setFilter(chip.dataset.kind, chip.dataset.value, true); return; }
      var link = e.target.closest('a[data-skill], a[data-company]');
      if (link && !e.metaKey && !e.ctrlKey && !e.shiftKey) {
        e.preventDefault();
        var kind = link.dataset.skill ? 'skill' : 'company';
        var inCards = !!link.closest('.proj');
        setFilter(kind, link.dataset.skill || link.dataset.company, inCards);
        if (!inCards) scrollTo(document.getElementById('projects'));
      }
    });
    document.getElementById('f-clear').addEventListener('click', function () { state.company = state.skill = ''; applyFilters(true); });
    var p = new URLSearchParams(location.search);
    if (p.get('project')) { applyFilters(false); openCard(p.get('project')); }
    else {
      state.company = p.get('company') || ''; state.skill = p.get('skill') || '';
      applyFilters(false);
      if (state.company || state.skill) setTimeout(function () { scrollTo(document.getElementById('projects')); }, 50);
    }
  }

  /* ------------------------------------------------------------- search */
  var idx = null, palette = null, input, listEl, results = [], active = 0, lastFocus = null;
  var ORDER = { role: 5, project: 4, faq: 3, skill: 3, section: 2, press: 1, action: 0 };
  var isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);

  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function subseq(q, s) { var i = 0; for (var j = 0; j < s.length && i < q.length; j++) if (s[j] === q[i]) i++; return i === q.length; }
  function load() {
    if (idx) return Promise.resolve(idx);
    return fetch(cfg.searchIndex).then(function (r) { return r.json(); }).then(function (d) {
      d.forEach(function (e) { e.nn = norm(e.n); e.ns = norm(e.s); e.nk = norm(e.k); });
      idx = d; return d;
    });
  }
  function score(e, tokens) {
    var total = 0;
    for (var i = 0; i < tokens.length; i++) {
      var t = tokens[i], sc = 0;
      if (e.nn.indexOf(t) === 0) sc = 100;
      else if (e.nn.indexOf(' ' + t) > -1) sc = 80;
      else if (e.nn.indexOf(t) > -1) sc = 60;
      else if (e.ns.indexOf(t) > -1) sc = 30;
      else if (e.nk.indexOf(' ' + t) > -1 || e.nk.indexOf(t) === 0) sc = 25;
      else if (e.nk.indexOf(t) > -1) sc = 15;
      else if (t.length > 2 && e.nn.length <= 32 && subseq(t, e.nn)) sc = 6;   // typo-tolerant, short names only
      else return 0;
      total += sc;
    }
    return total + (ORDER[e.t] || 0);
  }
  function search(q) {
    var tokens = norm(q).split(/\s+/).filter(Boolean);
    if (!tokens.length) return idx.filter(function (e) { return e.t === 'section' || e.t === 'action'; }).slice(0, 12);
    return idx.map(function (e) { return { e: e, s: score(e, tokens) }; })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s; })
      .slice(0, 30).map(function (r) { return r.e; });
  }
  function render() {
    listEl.innerHTML = '';
    if (!results.length) {
      var li = document.createElement('li'); li.className = 'empty'; li.textContent = UI.empty; listEl.appendChild(li);
      input.removeAttribute('aria-activedescendant'); return;
    }
    results.forEach(function (e, i) {
      var li = document.createElement('li');
      li.id = 'opt-' + i; li.setAttribute('role', 'option'); li.setAttribute('aria-selected', String(i === active));
      var badge = document.createElement('span'); badge.className = 'badge t-' + e.t; badge.textContent = UI.types[e.t] || e.t;
      var t = document.createElement('span'); t.className = 'ttl'; t.textContent = e.n;
      li.appendChild(badge); li.appendChild(t);
      if (e.s) { var s = document.createElement('span'); s.className = 'sub'; s.textContent = e.s; li.appendChild(s); }
      li.addEventListener('mousemove', function () { if (active !== i) { active = i; mark(); } });
      li.addEventListener('click', function () { choose(e); });
      listEl.appendChild(li);
    });
    input.setAttribute('aria-activedescendant', 'opt-' + active);
  }
  function mark() {
    [].forEach.call(listEl.children, function (li, i) {
      li.setAttribute('aria-selected', String(i === active));
      if (i === active) { input.setAttribute('aria-activedescendant', li.id); li.scrollIntoView({ block: 'nearest' }); }
    });
  }
  function choose(e) {
    closePalette();
    if (e.a === 'print') { setTimeout(function () { window.print(); }, 80); return; }
    if (e.x) { window.open(e.u, '_blank', 'noopener'); return; }
    if (!navigate(e.u)) location.href = e.u;
  }
  function buildPalette() {
    palette = document.createElement('div'); palette.className = 'palette'; palette.hidden = true;
    palette.innerHTML =
      '<div class="palette-backdrop" data-close></div>' +
      '<div class="palette-box" role="dialog" aria-modal="true" aria-label="' + UI.searchAria + '">' +
        '<div class="palette-input"><svg aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>' +
        '<input type="text" role="combobox" aria-expanded="true" aria-controls="palette-list" aria-autocomplete="list" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="' + UI.search + '"></div>' +
        '<ul id="palette-list" role="listbox"></ul>' +
        '<p class="palette-hint">' + UI.hint + '</p>' +
      '</div>';
    document.body.appendChild(palette);
    input = palette.querySelector('input'); listEl = palette.querySelector('ul');
    palette.addEventListener('click', function (e) { if (e.target.hasAttribute('data-close')) closePalette(); });
    input.addEventListener('input', function () { active = 0; results = search(input.value); render(); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); if (results.length) { active = (active + 1) % results.length; mark(); } }
      else if (e.key === 'ArrowUp') { e.preventDefault(); if (results.length) { active = (active - 1 + results.length) % results.length; mark(); } }
      else if (e.key === 'Enter') { e.preventDefault(); if (results[active]) choose(results[active]); }
      else if (e.key === 'Escape') { e.preventDefault(); closePalette(); }
      else if (e.key === 'Tab') { e.preventDefault(); }
    });
  }
  function openPalette() {
    if (!palette) buildPalette();
    lastFocus = document.activeElement;
    palette.hidden = false; document.documentElement.classList.add('no-scroll');
    input.value = ''; active = 0; input.focus();
    load().then(function () { results = search(''); render(); }).catch(function () { results = []; render(); });
  }
  function closePalette() {
    if (!palette || palette.hidden) return;
    palette.hidden = true; document.documentElement.classList.remove('no-scroll');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  var btn = document.getElementById('search-open');
  if (btn) {
    btn.addEventListener('click', openPalette);
    if (!isMac) { var k = btn.querySelector('kbd'); if (k) k.textContent = 'Ctrl K'; }
  }
  document.addEventListener('keydown', function (e) {
    var tag = (e.target.tagName || '').toLowerCase();
    var typing = tag === 'input' || tag === 'textarea' || tag === 'select' || e.target.isContentEditable;
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); palette && !palette.hidden ? closePalette() : openPalette(); }
    else if (e.key === '/' && !typing && !e.metaKey && !e.ctrlKey && !e.altKey) { e.preventDefault(); openPalette(); }
  });

  /* --------------------------------------------------- hamburger menu */
  var menuBtn = document.getElementById('menu-btn');
  function setMenu(open) {
    if (!hdr || !menuBtn) return;
    hdr.classList.toggle('menu-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    if (open) hdr.classList.remove('hide');
  }
  if (menuBtn) {
    menuBtn.addEventListener('click', function () { setMenu(!hdr.classList.contains('menu-open')); });
    document.getElementById('site-nav').addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('click', function (e) { if (!e.target.closest('header.top')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && hdr.classList.contains('menu-open')) { setMenu(false); menuBtn.focus(); } });
    window.matchMedia('(min-width: 701px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });
  }

  /* ------------------------------------------- role skills show/hide */
  [].forEach.call(document.querySelectorAll('.skills-toggle'), function (btn) {
    var panel = document.getElementById(btn.getAttribute('aria-controls'));
    btn.hidden = false; panel.hidden = true;           // without JS the list simply stays visible
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', String(open)); panel.hidden = !open;
    });
  });

  /* ------------------------------------------------------------- print */
  var opened = [];
  var panels = [];
  window.addEventListener('beforeprint', function () {
    opened = []; panels = [];
    [].forEach.call(document.querySelectorAll('details'), function (d) { opened.push([d, d.open]); d.open = true; });
    [].forEach.call(document.querySelectorAll('.skills-panel'), function (p) { panels.push([p, p.hidden]); p.hidden = false; });
  });
  window.addEventListener('afterprint', function () {
    opened.forEach(function (p) { p[0].open = p[1]; });
    panels.forEach(function (p) { p[0].hidden = p[1]; });
  });

  // Language links should keep a filter/hash? No: keep it simple and let the browser navigate.
  window.addEventListener('popstate', function () { if (list) { var p = new URLSearchParams(location.search); state.company = p.get('company') || ''; state.skill = p.get('skill') || ''; applyFilters(false); } });
})();
