"use strict";

const Utils = (() => {
  function isNotEmpty(v){ return typeof v === "string" && v.trim().length > 0; }
  function capitalize(s){ return s ? s.charAt(0).toUpperCase() + s.slice(1) : ""; }
  function showToast(message, type = "success") {
    let toast = document.querySelector(".toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "toast";
      toast.innerHTML = '<span class="toast__dot"></span><span class="toast__text"></span>';
      document.body.appendChild(toast);
    }
    toast.classList.remove("toast--success", "toast--error");
    toast.classList.add(type === "error" ? "toast--error" : "toast--success");
    toast.querySelector(".toast__text").textContent = message;
    toast.classList.remove("is-visible");
    void toast.offsetWidth;
    toast.classList.add("is-visible");
    clearTimeout(toast._hideTimer);
    toast._hideTimer = setTimeout(() => toast.classList.remove("is-visible"), 3200);
  }
  const memoryStore = {};
  function storageSet(key, value) { try { window.localStorage.setItem(key, value); } catch (e) { memoryStore[key] = value; } }
  function storageGet(key) { try { return window.localStorage.getItem(key); } catch (e) { return key in memoryStore ? memoryStore[key] : null; } }
  function storageRemove(key) { try { window.localStorage.removeItem(key); } catch (e) { delete memoryStore[key]; } }
  return { isNotEmpty, capitalize, showToast, storageSet, storageGet, storageRemove };
})();

const ROLE_CONFIG = {
  teacher: { label: "Teacher", idLabel: "Faculty ID", idLabelLower: "faculty ID", idPlaceholder: "e.g. F2026-0417",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5a2 2 0 0 1 2-2h11l3 3v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z"/><path d="M8 7h8M8 11h8M8 15h5"/></svg>' },
  student: { label: "Student", idLabel: "Student ID", idLabelLower: "student ID", idPlaceholder: "e.g. S2026-0417",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2 8l10 5 10-5-10-5Z"/><path d="M6 10.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-5.5"/></svg>' }
};
let currentRole = "student";

function applyRoleTheme(role) {
  const cfg = ROLE_CONFIG[role];
  currentRole = role;
  document.querySelectorAll("[data-role-label]").forEach(el => el.textContent = cfg.label);
  document.getElementById("roleIcon").innerHTML = cfg.icon;
  document.querySelector("[data-id-label]").textContent = cfg.idLabel;
  document.querySelector("[data-id-label-lower]").textContent = cfg.idLabelLower;
  document.getElementById("loginId").placeholder = cfg.idPlaceholder;
  populateIdSuggestions(role);

  document.getElementById("authLight").classList.toggle("role-teacher", role === "teacher");
  document.getElementById("toggleStudent").classList.toggle("is-active", role === "student");
  document.getElementById("toggleStudent").setAttribute("aria-selected", String(role === "student"));
  document.getElementById("toggleTeacher").classList.toggle("is-active", role === "teacher");
  document.getElementById("toggleTeacher").setAttribute("aria-selected", String(role === "teacher"));
}

const REMEMBER_KEY = "attendai_remembered";
function saveRemembered(role, id, password) { Utils.storageSet(REMEMBER_KEY, JSON.stringify({ role, id, password })); }
function getRemembered() { const raw = Utils.storageGet(REMEMBER_KEY); if (!raw) return null; try { return JSON.parse(raw); } catch (e) { return null; } }
function clearRemembered() { Utils.storageRemove(REMEMBER_KEY); }

const RECENT_LOGINS_KEY = "attendai_recent_logins";
function getRecentLogins() { const raw = Utils.storageGet(RECENT_LOGINS_KEY); if (!raw) return []; try { return JSON.parse(raw); } catch (e) { return []; } }
function saveRecentLogin(role, id, password) {
  const list = getRecentLogins().filter(entry => !(entry.role === role && entry.id.toLowerCase() === id.toLowerCase()));
  list.unshift({ role, id, password });
  Utils.storageSet(RECENT_LOGINS_KEY, JSON.stringify(list.slice(0, 5)));
}
function populateIdSuggestions(role) {
  const datalist = document.getElementById("idSuggestions");
  if (!datalist) return;
  const entries = getRecentLogins().filter(entry => entry.role === role);
  datalist.innerHTML = entries.map(entry => `<option value="${entry.id}"></option>`).join("");
}
function autofillPasswordForId(role, id) {
  const match = getRecentLogins().find(entry => entry.role === role && entry.id.toLowerCase() === id.toLowerCase());
  if (match) document.getElementById("loginPassword").value = match.password;
}

function setFieldError(input, errorEl, message) {
  if (message) { input.classList.add("is-invalid"); errorEl.textContent = message; errorEl.classList.add("is-visible"); }
  else { input.classList.remove("is-invalid"); errorEl.classList.remove("is-visible"); errorEl.textContent = ""; }
}
function setFormMessage(el, message, type) {
  el.textContent = message; el.className = "form-message";
  if (message) el.classList.add("is-visible", `form-message--${type}`);
}

/* Login ke baad sahi dashboard page pe le jaata hai */
function goToDashboard(role, id, name) {
  const path = role === "teacher" ? "/faculty/dashboard" : "/student/dashboard";
  const params = new URLSearchParams({ id, name });
  window.location.href = `${path}?${params.toString()}`;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-role-switch]").forEach(btn => {
    btn.addEventListener("click", () => applyRoleTheme(btn.getAttribute("data-role-switch")));
  });

  document.getElementById("togglePassword").addEventListener("click", () => {
    const input = document.getElementById("loginPassword");
    const btn = document.getElementById("togglePassword");
    const show = input.type === "password";
    input.type = show ? "text" : "password";
    btn.textContent = show ? "Hide" : "Show";
    btn.setAttribute("aria-pressed", String(show));
  });

  document.getElementById("loginId").addEventListener("input", e => {
    autofillPasswordForId(currentRole, e.target.value.trim());
  });

  document.getElementById("loginForm").addEventListener("submit", async e => {
    e.preventDefault();
    const idInput = document.getElementById("loginId");
    const passwordInput = document.getElementById("loginPassword");
    const idError = document.getElementById("loginIdError");
    const passwordError = document.getElementById("loginPasswordError");
    const formMessage = document.getElementById("formMessage");
    const submitBtn = document.getElementById("loginSubmit");

    setFormMessage(formMessage, "", null);
    const idValid = Utils.isNotEmpty(idInput.value);
    const passwordValid = Utils.isNotEmpty(passwordInput.value);
    setFieldError(idInput, idError, idValid ? "" : "This field can't be empty.");
    setFieldError(passwordInput, passwordError, passwordValid ? "" : "Enter your password to continue.");
    if (!idValid || !passwordValid) { Utils.showToast("Please fix the highlighted fields.", "error"); return; }

    const enteredId = idInput.value.trim();
    const enteredPassword = passwordInput.value;
    const roleForApi = currentRole === "teacher" ? "faculty" : currentRole;

    submitBtn.classList.add("is-loading");
    let result;
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: roleForApi, user_id: enteredId, password: enteredPassword })
      });
      result = await response.json();
    } catch (err) {
      submitBtn.classList.remove("is-loading");
      setFormMessage(formMessage, "Server se connect nahi ho pa raha. Kya server chal raha hai?", "error");
      Utils.showToast("Connection failed.", "error");
      return;
    }
    submitBtn.classList.remove("is-loading");

    if (!result.success) {
      setFormMessage(formMessage, result.message || "Incorrect ID or password.", "error");
      Utils.showToast("Login failed — check your ID and password.", "error");
      return;
    }

    const rememberChecked = document.getElementById("rememberMe").checked;
    if (rememberChecked) saveRemembered(currentRole, enteredId, enteredPassword);
    else clearRemembered();
    saveRecentLogin(currentRole, enteredId, enteredPassword);

    setFormMessage(formMessage, `Welcome back! Signed in as ${Utils.capitalize(currentRole)} (${result.name}).`, "success");
    localStorage.setItem("user_id", enteredId);
    localStorage.setItem("user_role", currentRole);
    localStorage.setItem("user_name", result.name);
    Utils.showToast("Login successful.", "success");
    setTimeout(() => goToDashboard(currentRole, enteredId, result.name), 700);
  });

  const rememberedOnLoad = getRemembered();
  if (rememberedOnLoad) {
    applyRoleTheme(rememberedOnLoad.role);
    document.getElementById("loginId").value = rememberedOnLoad.id;
    document.getElementById("loginPassword").value = rememberedOnLoad.password;
    document.getElementById("rememberMe").checked = true;
  } else {
    applyRoleTheme("student");
  }
});
