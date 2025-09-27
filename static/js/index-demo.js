(function () {
  const $ = (sel) => document.querySelector(sel);

  const sampleEl = $("#demo-snippet");
  const outEl = $("#demo-output");
  const errEl = $("#demo-error");

  const btnEncrypt = $("#demo-encrypt");
  const btnDecrypt = $("#demo-decrypt");

  let currentText = ""; // holds last successful result shown in outEl

  function setBusy(btn, busy) {
    if (busy) {
      btn.setAttribute("aria-busy", "true");
      btn.classList.add("is-busy");
    } else {
      btn.removeAttribute("aria-busy");
      btn.classList.remove("is-busy");
    }
  }

  function disable(btn) {
    btn.classList.add("disabled");
    btn.setAttribute("aria-disabled", "true");
  }

  function showError(msg) {
    errEl.textContent = msg || "Something went wrong.";
    errEl.hidden = false;
  }

  function clearError() {
    errEl.hidden = true;
    errEl.textContent = "";
  }

  async function callApi(endpoint, text) {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.ok) {
      const msg = (data && data.error) ? data.error : `HTTP ${res.status}`;
      throw new Error(msg);
    }
    return data.result;
  }

  btnEncrypt.addEventListener("click", async (e) => {
    e.preventDefault();
    clearError();

    // prevent rerun if already disabled
    if (btnEncrypt.classList.contains("disabled")) return;

    const endpoint = btnEncrypt.dataset.endpoint;
    const sample = sampleEl.textContent.trim();

    try {
      setBusy(btnEncrypt, true);
      const result = await callApi(endpoint, sample);
      currentText = result;
      outEl.textContent = result;
      outEl.hidden = false;
      // lock this button to avoid multiple encrypts of the same sample
      disable(btnEncrypt);
    } catch (err) {
      showError(err.message);
    } finally {
      setBusy(btnEncrypt, false);
    }
  });

  btnDecrypt.addEventListener("click", async (e) => {
    e.preventDefault();
    clearError();

    if (btnDecrypt.classList.contains("disabled")) return;

    const endpoint = btnDecrypt.dataset.endpoint;

    // Prefer decrypting the current output (wordified text + notice)
    const toDecrypt = (outEl.hidden ? "" : outEl.textContent.trim());
    if (!toDecrypt) {
      showError("Encrypt the sample first, then try decrypt.");
      return;
    }

    try {
      setBusy(btnDecrypt, true);
      const result = await callApi(endpoint, toDecrypt);
      currentText = result;
      outEl.textContent = result;
      outEl.hidden = false;
      // lock this button after success
      disable(btnDecrypt);
    } catch (err) {
      showError(err.message);
    } finally {
      setBusy(btnDecrypt, false);
    }
  });
})();
