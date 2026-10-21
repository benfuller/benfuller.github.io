// Projects filter: cards carry data-company and data-skills; chips are built from them.
(function () {
  var list = document.getElementById('proj-list');
  if (!list) return;
  var cards = [].slice.call(list.querySelectorAll('.proj'));
  var box = document.getElementById('filters');
  var state = { company: '', skill: '' };

  var companies = {}, skills = {};
  cards.forEach(function (c) {
    companies[c.dataset.company] = c.querySelector('.co-chip').textContent;
    [].forEach.call(c.querySelectorAll('.tag'), function (t) { skills[t.dataset.skill] = t.textContent; });
  });

  function chips(target, kind, map) {
    var host = document.getElementById(target);
    Object.keys(map).sort(function (a, b) { return map[a].localeCompare(map[b]); }).forEach(function (k) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'chip'; b.textContent = map[k]; b.dataset.kind = kind; b.dataset.value = k;
      host.appendChild(b);
    });
  }
  chips('f-company', 'company', companies);
  chips('f-skill', 'skill', skills);
  box.hidden = false;

  function apply() {
    var n = 0;
    cards.forEach(function (c) {
      var ok = (!state.company || c.dataset.company === state.company) &&
               (!state.skill || c.dataset.skills.split(' ').indexOf(state.skill) > -1);
      c.hidden = !ok; if (ok) n++;
    });
    [].forEach.call(box.querySelectorAll('.chip'), function (b) {
      b.setAttribute('aria-pressed', String(state[b.dataset.kind] === b.dataset.value));
    });
    [].forEach.call(list.querySelectorAll('.tag, .co-chip'), function (b) {
      var kind = b.classList.contains('tag') ? 'skill' : 'company';
      b.classList.toggle('on', state[kind] === (b.dataset.skill || b.dataset.company));
    });
    var active = state.company || state.skill;
    document.getElementById('f-count').textContent = active ? n + ' of ' + cards.length + ' projects' : cards.length + ' projects';
    document.getElementById('f-clear').hidden = !active;
    var q = [];
    if (state.company) q.push('company=' + encodeURIComponent(state.company));
    if (state.skill) q.push('skill=' + encodeURIComponent(state.skill));
    try { history.replaceState(null, '', location.pathname + (q.length ? '?' + q.join('&') : '') + location.hash); } catch (e) {}
  }

  function toggle(kind, value) { state[kind] = state[kind] === value ? '' : value; apply(); }

  document.addEventListener('click', function (e) {
    var b = e.target.closest('.chip, .tag, .co-chip');
    if (!b || !document.getElementById('projects').contains(b)) return;
    if (b.classList.contains('chip')) toggle(b.dataset.kind, b.dataset.value);
    else if (b.classList.contains('tag')) toggle('skill', b.dataset.skill);
    else toggle('company', b.dataset.company);
  });
  document.getElementById('f-clear').addEventListener('click', function () { state.company = state.skill = ''; apply(); });

  var p = new URLSearchParams(location.search);
  if (companies[p.get('company')]) state.company = p.get('company');
  if (skills[p.get('skill')]) state.skill = p.get('skill');
  apply();
  if ((state.company || state.skill) && !location.hash) location.hash = '#projects';
})();
