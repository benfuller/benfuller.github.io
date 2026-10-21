// Cookie consent + PostHog loader. Generated into /consent.js by _src/build.py.
// PostHog is never requested until the visitor accepts analytics; rejecting or
// ignoring the banner means no third-party request is made at all.
(function () {
  var cfg = JSON.parse(document.getElementById('site-config').textContent);
  var T = cfg.ui.consent, PH = cfg.posthog, KEY = 'consent.v1';
  var banner = null, loaded = false;

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }
  function write(analytics) {
    try { localStorage.setItem(KEY, JSON.stringify({ analytics: analytics, ts: Date.now() })); } catch (e) {}
  }

  !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagResult isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);

  function loadAnalytics() {
    if (!PH.key) return;
    if (loaded) { if (window.posthog && window.posthog.opt_in_capturing) window.posthog.opt_in_capturing(); return; }
    loaded = true;
    window.posthog.init(PH.key, {
      api_host: PH.host,
      defaults: '2026-05-30',
      person_profiles: 'identified_only',
      persistence: 'localStorage+cookie',
      disable_session_recording: true
    });
  }

  function clearAnalytics() {
    if (loaded && window.posthog && window.posthog.opt_out_capturing) window.posthog.opt_out_capturing();
    try {
      Object.keys(localStorage).forEach(function (k) {
        if (k.indexOf('ph_') === 0 || k.indexOf('posthog') > -1) localStorage.removeItem(k);
      });
    } catch (e) {}
    var host = location.hostname.split('.');
    var domains = ['', location.hostname];
    if (host.length > 2) domains.push('.' + host.slice(-2).join('.'));
    else domains.push('.' + location.hostname);
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (name.indexOf('ph_') !== 0 && name.indexOf('posthog') === -1) return;
      domains.forEach(function (d) {
        document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (d ? '; domain=' + d : '');
      });
    });
  }

  function choose(analytics) {
    write(analytics);
    if (analytics) loadAnalytics(); else clearAnalytics();
    hide();
  }

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (html) n.innerHTML = html;
    return n;
  }

  function build() {
    banner = el('div', { class: 'consent', role: 'dialog', 'aria-labelledby': 'consent-title', 'aria-describedby': 'consent-text', hidden: '' });
    banner.innerHTML =
      '<h2 id="consent-title">' + T.title + '</h2>' +
      '<p id="consent-text">' + T.text + ' <a href="' + cfg.privacy + '">' + T.more + '</a></p>' +
      '<div class="consent-prefs" hidden>' +
        '<label><input type="checkbox" checked disabled> <span><b>' + T.necessary + '</b><small>' + T.necessary_d + '</small></span></label>' +
        '<label><input type="checkbox" id="consent-analytics"> <span><b>' + T.analytics + '</b><small>' + T.analytics_d + '</small></span></label>' +
      '</div>' +
      '<div class="consent-actions">' +
        '<button type="button" data-act="accept" class="btn primary">' + T.accept + '</button>' +
        '<button type="button" data-act="reject" class="btn">' + T.reject + '</button>' +
        '<button type="button" data-act="prefs" class="btn ghost" aria-expanded="false">' + T.prefs + '</button>' +
        '<button type="button" data-act="save" class="btn" hidden>' + T.save + '</button>' +
      '</div>';
    document.body.appendChild(banner);
    banner.addEventListener('click', function (e) {
      var b = e.target.closest('button[data-act]');
      if (!b) return;
      var act = b.getAttribute('data-act');
      if (act === 'accept') choose(true);
      else if (act === 'reject') choose(false);
      else if (act === 'save') choose(banner.querySelector('#consent-analytics').checked);
      else if (act === 'prefs') togglePrefs();
    });
    banner.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && read()) hide();
    });
  }

  function togglePrefs(force) {
    var panel = banner.querySelector('.consent-prefs');
    var open = typeof force === 'boolean' ? force : panel.hidden;
    panel.hidden = !open;
    banner.querySelector('[data-act="prefs"]').setAttribute('aria-expanded', String(open));
    banner.querySelector('[data-act="save"]').hidden = !open;
  }

  function show(userInitiated) {
    if (!banner) build();
    var saved = read();
    banner.querySelector('#consent-analytics').checked = !!(saved && saved.analytics);
    banner.hidden = false; document.body.classList.add('consent-open');
    if (userInitiated) {
      togglePrefs(true);
      banner.querySelector('#consent-analytics').focus();
    }
  }

  function hide() { if (banner) { banner.hidden = true; togglePrefs(false); } document.body.classList.remove('consent-open'); }

  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-open-cookies]')) { e.preventDefault(); show(true); }
  });

  var saved = read();
  if (saved) { if (saved.analytics) loadAnalytics(); } else show(false);
})();
