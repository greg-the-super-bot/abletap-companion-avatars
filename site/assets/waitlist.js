/* Waitlist posts to Netlify Forms (the form named "waitlist" in the static HTML).
   Success is shown only after a confirmed 2xx. Anything else keeps the email
   and shows an error with a retry. */
(function () {
  function touch() {
    if (window.abletapReadTouch) return window.abletapReadTouch() || {};
    return {};
  }

  function fields() {
    return window.abletapUtmFields || ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "landing_path"];
  }

  function applyTouch(form) {
    var data = touch();
    fields().forEach(function (name) {
      var input = form.querySelector('input[name="' + name + '"]');
      if (input) input.value = data[name] || "";
    });
  }

  function applyAll() {
    document.querySelectorAll("form[name='waitlist']").forEach(applyTouch);
  }

  function ensureStyles() {
    if (document.getElementById("at-waitlist-styles")) return;
    var style = document.createElement("style");
    style.id = "at-waitlist-styles";
    style.textContent = [
      "[data-error]{margin-top:14px;padding:16px 18px;border-radius:14px;background:#fff;border:2px solid #7F1D1D;color:#2B2236;text-align:left;font-family:'Atkinson Hyperlegible',system-ui,sans-serif;}",
      "[data-error] p{margin:0 0 8px;font-size:1.02rem;line-height:1.45;color:#2B2236;}",
      "[data-error] .at-error-title{font-weight:700;color:#7F1D1D;}",
      "[data-error] [data-retry]{min-height:48px;min-width:148px;margin-top:6px;padding:12px 22px;border-radius:12px;border:2px solid #1C1430;background:#1C1430;color:#FAF5EF;font:700 1.05rem/1 'Atkinson Hyperlegible',system-ui,sans-serif;cursor:pointer;}",
      "[data-error] [data-retry]:focus,form[name='waitlist'] button:focus,form[name='waitlist'] input:focus,[data-success]:focus{outline:3px solid #6B4CE0;outline-offset:3px;}",
      "[data-success]{margin-top:14px;font-weight:700;font-size:1.05rem;line-height:1.45;}"
    ].join("");
    document.head.appendChild(style);
  }

  function setBusy(form, busy) {
    var button = form.querySelector("button[type=submit]");
    if (!button) return;
    if (!button.dataset.label) button.dataset.label = button.textContent;
    button.disabled = busy;
    button.setAttribute("aria-busy", busy ? "true" : "false");
    if (busy) button.textContent = "Joining…";
    else button.textContent = button.dataset.label;
    if (busy) form.setAttribute("aria-busy", "true");
    else form.removeAttribute("aria-busy");
  }

  function showError(form, wrap) {
    form.style.display = "flex";
    form.hidden = false;
    var success = wrap.querySelector("[data-success]");
    if (success) {
      success.hidden = true;
      success.style.display = "none";
    }
    var error = wrap.querySelector("[data-error]");
    if (!error) return;
    error.hidden = false;
    if (error.id) form.setAttribute("aria-describedby", error.id);
    var retry = error.querySelector("[data-retry]");
    if (retry) retry.focus();
  }

  function showSuccess(form, wrap, email) {
    var error = wrap.querySelector("[data-error]");
    if (error) error.hidden = true;
    form.style.display = "none";
    var success = wrap.querySelector("[data-success]");
    if (!success) return;
    var em = success.querySelector("[data-email]");
    if (em) em.textContent = email ? " " + email : "";
    success.hidden = false;
    success.style.display = "flex";
    if (!success.hasAttribute("tabindex")) success.setAttribute("tabindex", "-1");
    success.focus();
  }

  function signupProps() {
    var data = touch();
    return {
      utm_source: data.utm_source || "",
      utm_medium: data.utm_medium || "",
      utm_campaign: data.utm_campaign || "",
      utm_content: data.utm_content || "",
      utm_term: data.utm_term || "",
      landing_path: data.landing_path || ""
    };
  }

  function captureSignup(props, tries) {
    try {
      if (window.posthog && typeof window.posthog.capture === "function") {
        window.posthog.capture("waitlist_signup", props);
        return;
      }
    } catch (e) {
      return;
    }
    if ((tries || 0) < 40) {
      window.setTimeout(function () { captureSignup(props, (tries || 0) + 1); }, 250);
    }
  }

  window.atSubmit = function (ev) {
    ev.preventDefault();
    var form = ev.target;
    if (!form || form.nodeName !== "FORM") return false;
    var wrap = form.closest("[data-formwrap]") || form.parentElement;
    var input = form.querySelector("input[type=email]");
    var email = input ? input.value : "";
    ensureStyles();
    applyTouch(form);
    setBusy(form, true);
    var body;
    try {
      body = new URLSearchParams(new FormData(form)).toString();
    } catch (e) {
      setBusy(form, false);
      showError(form, wrap);
      return false;
    }
    fetch("/", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body
    }).then(function (res) {
      if (!res || res.status < 200 || res.status >= 300) throw new Error("not-2xx");
      showSuccess(form, wrap, email);
      captureSignup(signupProps(), 0);
    }).catch(function () {
      showError(form, wrap);
    }).then(function () {
      if (form.style.display !== "none") setBusy(form, false);
      else setBusy(form, false);
    });
    return false;
  };

  window.abletapRetryWaitlist = function (button) {
    var wrap = button && button.closest ? button.closest("[data-formwrap]") : null;
    var form = wrap ? wrap.querySelector("form[name='waitlist']") : null;
    if (!form) return;
    var input = form.querySelector("input[type=email]");
    if (input) input.focus();
    if (form.requestSubmit) form.requestSubmit();
    else form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }));
  };

  function bindRetry() {
    document.querySelectorAll("[data-retry]").forEach(function (button) {
      if (button.dataset.retryBound === "1") return;
      button.dataset.retryBound = "1";
      button.addEventListener("click", function () {
        window.abletapRetryWaitlist(button);
      });
    });
  }

  function init() {
    ensureStyles();
    applyAll();
    bindRetry();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
