/* Advertising consent for the AbleTap marketing site.
   Meta Pixel and LinkedIn Insight load only after Accept, and only
   when the matching ID in tracking-config.js is non-empty.
   Decline is stored in localStorage and blocks those tags.
   Campaign parameters are first-party only (sessionStorage). */
(function () {
  var CONSENT_KEY = "abletap_consent";
  var UTM_KEY = "abletap_utm_v1";
  var UTM_FIELDS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "landing_path"];

  function captureFirstTouch() {
    var existing = window.abletapReadTouch();
    if (existing) return existing;
    var params;
    try { params = new URLSearchParams(window.location.search); }
    catch (e) { params = { get: function () { return ""; } }; }
    var touch = {
      utm_source: (params.get("utm_source") || "").slice(0, 500),
      utm_medium: (params.get("utm_medium") || "").slice(0, 500),
      utm_campaign: (params.get("utm_campaign") || "").slice(0, 500),
      utm_content: (params.get("utm_content") || "").slice(0, 500),
      utm_term: (params.get("utm_term") || "").slice(0, 500),
      landing_path: (window.location.pathname || "/").slice(0, 500)
    };
    try { sessionStorage.setItem(UTM_KEY, JSON.stringify(touch)); } catch (e) {}
    return touch;
  }

  window.abletapReadTouch = function () {
    try {
      var raw = sessionStorage.getItem(UTM_KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (!data || typeof data !== "object") return null;
      return data;
    } catch (e) {
      return null;
    }
  };

  window.abletapUtmFields = UTM_FIELDS;

  function consentValue() {
    try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return null; }
  }

  function setConsent(value) {
    try { localStorage.setItem(CONSENT_KEY, value); return true; }
    catch (e) { return false; }
  }

  function configuredId(name) {
    var value;
    try { value = window[name]; } catch (e) { value = ""; }
    if (value === undefined || value === null) return "";
    var text = String(value).trim();
    return text;
  }

  function loadMeta(id) {
    if (window.__abletapMetaLoaded) return;
    window.__abletapMetaLoaded = true;
    (function (f, b, e, v, n, t, s) {
      if (f.fbq) return;
      n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
      };
      if (!f._fbq) f._fbq = n;
      n.push = n;
      n.loaded = true;
      n.version = "2.0";
      n.queue = [];
      t = b.createElement(e);
      t.async = true;
      t.src = v;
      s = b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t, s);
    })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
    /* PageView only. No custom events and no health or disability parameters. */
    window.fbq("init", id);
    window.fbq("track", "PageView");
  }

  function loadLinkedIn(id) {
    if (window.__abletapLinkedInLoaded) return;
    window.__abletapLinkedInLoaded = true;
    window._linkedin_partner_id = id;
    window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
    window._linkedin_data_partner_ids.push(id);
    if (!window.lintrk) {
      window.lintrk = function (a, b) { window.lintrk.q.push([a, b]); };
      window.lintrk.q = [];
    }
    var first = document.getElementsByTagName("script")[0];
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.async = true;
    script.src = "https://snap.licdn.com/li.lms-analytics/insight.min.js";
    script.setAttribute("data-abletap-linkedin", "1");
    if (first && first.parentNode) first.parentNode.insertBefore(script, first);
    else document.head.appendChild(script);
  }

  function loadTrackers() {
    if (consentValue() !== "accepted") return;
    var meta = configuredId("META_PIXEL_ID");
    var linkedin = configuredId("LINKEDIN_PARTNER_ID");
    if (meta) loadMeta(meta);
    if (linkedin) loadLinkedIn(linkedin);
  }

  function ensureStyles() {
    if (document.getElementById("at-consent-styles")) return;
    var style = document.createElement("style");
    style.id = "at-consent-styles";
    style.textContent = [
      "#at-consent{position:fixed;left:0;right:0;bottom:0;z-index:10050;background:#160F26;color:#FAF5EF;border-top:3px solid #F4B96B;padding:20px clamp(16px,4vw,40px);box-shadow:0 -12px 40px rgba(0,0,0,.35);font-family:'Atkinson Hyperlegible',system-ui,sans-serif;}",
      "#at-consent .at-consent-in{max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;gap:18px 28px;align-items:center;justify-content:space-between;}",
      "#at-consent h2{font-family:Fraunces,Georgia,serif;font-size:1.35rem;font-weight:600;line-height:1.2;margin:0 0 8px;color:#FAF5EF;}",
      "#at-consent p{margin:0;max-width:68ch;font-size:1.05rem;line-height:1.5;color:#FAF5EF;}",
      "#at-consent a{color:#F4B96B;font-weight:700;text-decoration:underline;text-underline-offset:3px;}",
      "#at-consent .at-consent-actions{display:flex;flex-wrap:wrap;gap:12px;}",
      "#at-consent button{min-height:48px;min-width:148px;padding:14px 28px;border-radius:12px;font-family:'Atkinson Hyperlegible',system-ui,sans-serif;font-size:1.125rem;font-weight:700;line-height:1;cursor:pointer;}",
      "#at-consent-accept{background:#F4B96B;color:#1C1430;border:2px solid #F4B96B;}",
      "#at-consent-decline{background:#FAF5EF;color:#1C1430;border:2px solid #FAF5EF;}",
      "#at-consent a:focus,#at-consent button:focus{outline:3px solid #FFFFFF;outline-offset:3px;}",
      "#at-consent-status{margin-top:8px;font-size:.98rem;}",
      "html.at-consent-pad body{padding-bottom:240px;}",
      "button[data-cookie-choices]{background:transparent;border:0;padding:0;margin:0;font:inherit;color:inherit;cursor:pointer;text-decoration:underline;text-underline-offset:3px;}",
      "button[data-cookie-choices]:focus{outline:3px solid #6B4CE0;outline-offset:3px;}",
      "@media (forced-colors: active){#at-consent{background:Canvas;color:CanvasText;border:2px solid CanvasText;}#at-consent h2,#at-consent p{color:CanvasText;}#at-consent a{color:LinkText;}#at-consent button{background:ButtonFace;color:ButtonText;border:2px solid ButtonText;}}",
      "@media (prefers-reduced-motion: reduce){#at-consent{transition:none;}}"
    ].join("");
    document.head.appendChild(style);
  }

  function bannerEl() {
    return document.getElementById("at-consent");
  }

  function setPad(on) {
    document.documentElement.classList.toggle("at-consent-pad", !!on);
  }

  function statusText(choice) {
    if (choice === "declined") {
      if (window.__abletapMetaLoaded || window.__abletapLinkedInLoaded) {
        return "Declined is saved. Reload this page and the advertising tags will not load.";
      }
      return "Declined. Advertising tags will not load.";
    }
    if (choice === "accepted") {
      var meta = configuredId("META_PIXEL_ID");
      var linkedin = configuredId("LINKEDIN_PARTNER_ID");
      if (!meta && !linkedin) return "Accepted. No advertising ID is configured, so nothing extra loads.";
      return "Accepted. Advertising tags can load on this page.";
    }
    return "";
  }

  function showBanner(moveFocus) {
    var banner = bannerEl();
    if (!banner) return;
    banner.hidden = false;
    setPad(true);
    var status = document.getElementById("at-consent-status");
    var current = consentValue();
    if (status) status.textContent = current === "accepted" || current === "declined" ? "Current choice: " + current + ". " + statusText(current) : "";
    if (moveFocus) {
      var accept = document.getElementById("at-consent-accept");
      if (accept) accept.focus();
    }
  }

  function hideBanner() {
    var banner = bannerEl();
    if (banner) banner.hidden = true;
    setPad(false);
  }

  function choose(value) {
    var saved = setConsent(value);
    var status = document.getElementById("at-consent-status");
    if (!saved) {
      if (status) status.textContent = "We couldn't save that choice in this browser. Advertising tags will stay off.";
      return;
    }
    if (value === "accepted") loadTrackers();
    if (status) status.textContent = statusText(value);
    hideBanner();
  }

  function buildBanner() {
    if (bannerEl()) return;
    ensureStyles();
    var banner = document.createElement("div");
    banner.id = "at-consent";
    banner.setAttribute("role", "region");
    banner.setAttribute("aria-labelledby", "at-consent-title");
    banner.hidden = true;
    banner.innerHTML = [
      '<div class="at-consent-in">',
      '<div>',
      '<h2 id="at-consent-title">Cookies and ad measurement</h2>',
      '<p>We can count visits with the Meta Pixel and the LinkedIn Insight Tag. They stay off unless you accept. We don\'t send health or disability details. <a href="/privacy.html">Privacy policy</a></p>',
      '<p id="at-consent-status" role="status"></p>',
      "</div>",
      '<div class="at-consent-actions">',
      '<button type="button" id="at-consent-accept">Accept</button>',
      '<button type="button" id="at-consent-decline">Decline</button>',
      "</div>",
      "</div>"
    ].join("");
    document.body.insertBefore(banner, document.body.firstChild);
    document.getElementById("at-consent-accept").addEventListener("click", function () { choose("accepted"); });
    document.getElementById("at-consent-decline").addEventListener("click", function () { choose("declined"); });
  }

  function bindChoiceLinks() {
    document.querySelectorAll("[data-cookie-choices]").forEach(function (el) {
      if (el.dataset.consentBound === "1") return;
      el.dataset.consentBound = "1";
      el.addEventListener("click", function (ev) {
        ev.preventDefault();
        showBanner(true);
      });
    });
  }

  window.abletapOpenConsent = function () { showBanner(true); };

  captureFirstTouch();

  function init() {
    buildBanner();
    bindChoiceLinks();
    var choice = consentValue();
    if (choice === "accepted") {
      hideBanner();
      loadTrackers();
    } else if (choice === "declined") {
      hideBanner();
    } else {
      showBanner(false);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
