// static/js/index-demo.js
(function () {
  const $ = (sel) => document.querySelector(sel);

  const sampleEl   = $("#demo-snippet");
  const outEl      = $("#demo-output");
  const errEl      = $("#demo-error");

  const btnEncrypt = $("#demo-encrypt");
  const btnDecrypt = $("#demo-decrypt");

  // --- helpers ---
  function setBusy(btn, busy) {
    if (busy) {
      btn.setAttribute("aria-busy", "true");
      btn.classList.add("is-busy");
    } else {
      btn.removeAttribute("aria-busy");
      btn.classList.remove("is-busy");
    }
  }

  function disableLink(btn) {
    btn.classList.add("disabled");
    btn.setAttribute("aria-disabled", "true");
  }

  function enableLink(btn) {
    btn.classList.remove("disabled");
    btn.removeAttribute("aria-disabled");
  }

  function isDisabled(btn) {
    return btn.classList.contains("disabled");
  }

  function showError(msg) {
    errEl.textContent = msg || "Something went wrong.";
    errEl.hidden = false;
  }

  function clearError() {
    errEl.hidden = true;
    errEl.textContent = "";
  }

  function scrollToBottom() {
    // Smooth scroll to bottom so new/updated output is visible
    window.scrollTo({
      top: document.documentElement.scrollHeight || document.body.scrollHeight,
      behavior: "smooth",
    });
  }

  async function callApi(endpoint, text) {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.ok) {
      const msg = (data && data.error) ? data.error : `HTTP ${res.status}`;
      throw new Error(msg);
    }
    return data.result;
  }

  // --- button handlers ---
  btnEncrypt.addEventListener("click", async (e) => {
    e.preventDefault();
    if (isDisabled(btnEncrypt)) return;

    clearError();

    const endpoint = btnEncrypt.dataset.endpoint;
    const sample   = sampleEl.textContent.trim();

    try {
      setBusy(btnEncrypt, true);
      const result = await callApi(endpoint, sample);

      outEl.textContent = result;   // show encrypted text in the SAME box
      outEl.hidden = false;

      // Toggle states: Encrypt off, Decrypt on
      disableLink(btnEncrypt);
      enableLink(btnDecrypt);

      // Ensure user sees the updated output
      scrollToBottom();
    } catch (err) {
      showError(err.message);
    } finally {
      setBusy(btnEncrypt, false);
    }
  });

  btnDecrypt.addEventListener("click", async (e) => {
    e.preventDefault();
    if (isDisabled(btnDecrypt)) return;

    clearError();

    const endpoint  = btnDecrypt.dataset.endpoint;
    const toDecrypt = outEl.hidden ? "" : outEl.textContent.trim();
    if (!toDecrypt) {
      showError("Encrypt the sample first, then try decrypt.");
      return;
    }

    try {
      setBusy(btnDecrypt, true);
      const result = await callApi(endpoint, toDecrypt);

      outEl.textContent = result;   // replace with decrypted/plain text

      // Toggle states: Decrypt off, Encrypt on (cycle can run again)
      disableLink(btnDecrypt);
      enableLink(btnEncrypt);

      // Ensure user sees the updated output
      scrollToBottom();
    } catch (err) {
      showError(err.message);
    } finally {
      setBusy(btnDecrypt, false);
    }
  });

  // --- initial state on load ---
  enableLink(btnEncrypt);  // can start by encrypting the sample
  disableLink(btnDecrypt); // decrypt becomes available after encrypt succeeds
})();
