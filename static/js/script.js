"use strict";

/* ---------- shared utils ---------- */
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

  /* Persistent storage with a graceful fallback: some sandboxed preview
     environments block localStorage, so "remember me" degrades to an
     in-memory value that lasts for the current tab only in that case. */
  const memoryStore = {};
  function storageSet(key, value) {
    try { window.localStorage.setItem(key, value); }
    catch (e) { memoryStore[key] = value; }
  }
  function storageGet(key) {
    try { return window.localStorage.getItem(key); }
    catch (e) { return key in memoryStore ? memoryStore[key] : null; }
  }
  function storageRemove(key) {
    try { window.localStorage.removeItem(key); }
    catch (e) { delete memoryStore[key]; }
  }

  return { isNotEmpty, capitalize, showToast, storageSet, storageGet, storageRemove };
})();

/* ---------- role config ---------- */
const ROLE_CONFIG = {
  teacher: { label: "Teacher", idLabel: "Faculty ID", idLabelLower: "faculty ID", idPlaceholder: "e.g. F2026-0417", meta: "Faculty & staff sign-in",
    dept: "Computer Science Department",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19V5a2 2 0 0 1 2-2h11l3 3v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z"/><path d="M8 7h8M8 11h8M8 15h5"/></svg>' },
  student: { label: "Student", idLabel: "Student ID", idLabelLower: "student ID", idPlaceholder: "e.g. S2026-0417", meta: "Learner sign-in",
    dept: "Grade 11 · Section B",
    icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2 8l10 5 10-5-10-5Z"/><path d="M6 10.5V16c0 1.5 3 3 6 3s6-1.5 6-3v-5.5"/></svg>' }
};
let currentRole = "student";
let currentName = "";

/* ---------- view switching (single page, no reload) ---------- */
function showView(name) {
  document.querySelectorAll("[data-view]").forEach(el => el.classList.toggle("is-active", el.dataset.view === name));
  document.body.classList.toggle("is-app-shell", name === "dashboard");
  window.scrollTo({ top: 0, behavior: "instant" in document.documentElement.style ? "instant" : "auto" });
}

function applyRoleTheme(role) {
  const cfg = ROLE_CONFIG[role];
  currentRole = role;
  document.querySelectorAll("[data-role-label]").forEach(el => el.textContent = cfg.label);
  document.querySelectorAll("[data-role-meta]").forEach(el => el.textContent = cfg.meta);
  document.getElementById("roleIcon").innerHTML = cfg.icon;
  const idLabel = document.querySelector("[data-id-label]");
  const idLabelLower = document.querySelector("[data-id-label-lower]");
  const idInput = document.getElementById("loginId");
  if (idLabel) idLabel.textContent = cfg.idLabel;
  if (idLabelLower) idLabelLower.textContent = cfg.idLabelLower;
  if (idInput) idInput.placeholder = cfg.idPlaceholder;
  populateIdSuggestions(role);

  const authLight = document.getElementById("authLight");
  if (authLight) authLight.classList.toggle("role-teacher", role === "teacher");

  const toggleStudent = document.getElementById("toggleStudent");
  const toggleTeacher = document.getElementById("toggleTeacher");
  if (toggleStudent && toggleTeacher) {
    toggleStudent.classList.toggle("is-active", role === "student");
    toggleStudent.setAttribute("aria-selected", String(role === "student"));
    toggleTeacher.classList.toggle("is-active", role === "teacher");
    toggleTeacher.setAttribute("aria-selected", String(role === "teacher"));
  }

  document.querySelectorAll("[data-role-only]").forEach(el => {
    el.classList.toggle("is-role-active", el.getAttribute("data-role-only") === role);
  });
}

/* ---------- dashboard population ---------- */
const WEEK_DATA = {
  teacher: [78, 85, 90, 82, 88, 60, 40],
  student: [100, 100, 80, 100, 100, 0, 0]
};

const ACTIVITY = {
  teacher: [
    { present: true, text: "Section B marked present — 28 students", time: "2 min ago" },
    { present: false, text: "Kabir Singh marked absent", time: "10 min ago" },
    { present: true, text: "Section A attendance submitted", time: "1 hr ago" },
    { present: true, text: "Leave request approved · Ishita Rao", time: "3 hrs ago" }
  ],
  student: [
    { present: true, text: "Checked in to Mathematics", time: "9:02 AM" },
    { present: true, text: "Checked in to Physics", time: "10:31 AM" },
    { present: false, text: "Missed Chemistry", time: "Yesterday" },
    { present: true, text: "Checked in to English", time: "Yesterday" }
  ]
};

function renderBarChart(role) {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const values = WEEK_DATA[role];
  const chart = document.getElementById("barChart");
  chart.innerHTML = values.map((v, i) => `
    <div class="bar-chart__col">
      <div class="bar-chart__bar" style="height:${Math.max(v, 4)}%"></div>
      <span class="bar-chart__day">${days[i]}</span>
    </div>`).join("");
}

function renderActivity(role) {
  const list = document.getElementById("activityList");
  list.innerHTML = ACTIVITY[role].map(item => `
    <div class="activity-row">
      <span class="activity-row__dot ${item.present ? "present" : "absent"}"></span>
      <span class="activity-row__main">${item.text}</span>
      <span class="activity-row__meta">${item.time}</span>
    </div>`).join("");
}

function enterDashboard(role, name) {
  applyRoleTheme(role);
  currentName = name;
  document.getElementById("dashName").textContent = name || Utils.capitalize(role);
  document.getElementById("dashDate").textContent = new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });
  document.getElementById("statusChip").textContent = "STATUS · Present today";
  renderBarChart(role);
  renderActivity(role);
  populateProfile(role, name);
  populateTimetable(role);
  populateProfileChip(role, name);
  showPage("dashboard");
  showView("dashboard");
}

/* ---------- topbar profile chip ---------- */
function populateProfileChip(role, name) {
  const cfg = ROLE_CONFIG[role];
  const displayName = name || cfg.label;
  document.getElementById("profileChip").classList.toggle("role-teacher", role === "teacher");
  document.getElementById("profileChipAvatar").textContent = displayName.charAt(0).toUpperCase();
  document.getElementById("profileChipName").textContent = displayName;
  document.getElementById("profileChipRole").textContent = cfg.label;
}

/* ---------- page routing within the dashboard shell ---------- */
function showPage(page) {
  document.querySelectorAll("[data-page]").forEach(el => el.classList.toggle("is-page-active", el.dataset.page === page));

  const titleEl = document.getElementById("pageTitle");
  const subtitleEl = document.getElementById("pageSubtitle");
  const roleLabel = ROLE_CONFIG[currentRole].label;

  const titles = {
    dashboard: [`Welcome back, ${currentName || roleLabel}`, `${roleLabel} sign-in · ${document.getElementById("dashDate").textContent}`],
    profile: ["My profile", "Personal and account details on file"],
    reports: ["Attendance reports", "Term summary and monthly breakdown"],
    timetable: ["Weekly timetable", "Your scheduled classes, Monday to Friday"]
  };

  const [title, subtitle] = titles[page] || titles.dashboard;
  titleEl.textContent = title;
  subtitleEl.textContent = subtitle;
}

/* ---------- profile page ---------- */
function populateProfile(role, id) {
  const cfg = ROLE_CONFIG[role];
  const name = id || cfg.label;
  document.getElementById("profileAvatar").textContent = name.charAt(0).toUpperCase();
  document.getElementById("profileName").textContent = name;
  document.getElementById("profileIdLine").textContent = `${cfg.idLabel} · ${id || "—"}`;
  document.getElementById("profileRoleChip").textContent = `ROLE · ${cfg.label}`;
  document.getElementById("profileDept").textContent = cfg.dept;
  document.getElementById("profileEmail").textContent = `${(id || "user").toLowerCase().replace(/[^a-z0-9]/g, "")}@attendai.edu`;
}

/* ---------- timetable page ---------- */
const TIMETABLE = {
  teacher: [
    ["9:00 AM", "Section A", "Section C", "Section A", "Section B", "Section C"],
    ["10:30 AM", "Section B", "Free period", "Section B", "Section A", "Free period"],
    ["12:30 PM", "Lunch", "Lunch", "Lunch", "Lunch", "Lunch"],
    ["1:30 PM", "Section C", "Section A", "Free period", "Section C", "Section B"],
    ["3:00 PM", "Staff meeting", "Section B", "Section A", "Free period", "Section A"]
  ],
  student: [
    ["9:00 AM", "Mathematics", "Physics", "Mathematics", "Chemistry", "English"],
    ["10:30 AM", "Physics", "Chemistry", "English", "Mathematics", "Physics"],
    ["12:30 PM", "Lunch", "Lunch", "Lunch", "Lunch", "Lunch"],
    ["1:30 PM", "Chemistry", "Computer Sci.", "Physics", "English", "Computer Sci."],
    ["3:00 PM", "English", "Free period", "Computer Sci.", "Free period", "Free period"]
  ]
};

function populateTimetable(role) {
  const rows = TIMETABLE[role];
  const body = document.getElementById("timetableBody");
  body.innerHTML = rows.map(row => `
    <tr>
      <td style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--color-paper-dim);">${row[0]}</td>
      ${row.slice(1).map(cell => `<td>${cell}</td>`).join("")}
    </tr>`).join("");
}

/* ---------- reports: CSV export ---------- */
function downloadReportCsv() {
  const table = document.getElementById("reportTable");
  const rows = Array.from(table.querySelectorAll("tr")).map(tr =>
    Array.from(tr.querySelectorAll("th,td")).map(cell => `"${cell.textContent.trim()}"`).join(",")
  );
  const csv = rows.join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "attendai-report.csv";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  Utils.showToast("Report downloaded.", "success");
}

/* ---------- remember me: persisted credentials ---------- */
const REMEMBER_KEY = "attendai_remembered";
function saveRemembered(role, id, password) {
  Utils.storageSet(REMEMBER_KEY, JSON.stringify({ role, id, password }));
}
function getRemembered() {
  const raw = Utils.storageGet(REMEMBER_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (e) { return null; }
}
function clearRemembered() {
  Utils.storageRemove(REMEMBER_KEY);
}

/* ---------- recent logins: id suggestions + password auto-fill ----------
   Separate from "remember me": this always keeps a short list of recently
   used IDs per role so the ID field can suggest them, and auto-fills the
   matching password when a suggested ID is picked — no checkbox needed. */
const RECENT_LOGINS_KEY = "attendai_recent_logins";
function getRecentLogins() {
  const raw = Utils.storageGet(RECENT_LOGINS_KEY);
  if (!raw) return [];
  try { return JSON.parse(raw); } catch (e) { return []; }
}
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

function selectRole(role, card) {
  card.classList.add("is-stamped");
  Utils.showToast(`${Utils.capitalize(role)} selected — opening login…`, "success");
  setTimeout(() => {
    card.classList.remove("is-stamped");
    applyRoleTheme(role);
    showView("login");

    const remembered = getRemembered();
    if (remembered && remembered.role === role) {
      document.getElementById("loginId").value = remembered.id;
      document.getElementById("loginPassword").value = remembered.password;
      document.getElementById("rememberMe").checked = true;
    }
  }, 420);
}

/* ---------- form helpers ---------- */
function setFieldError(input, errorEl, message) {
  if (message) { input.classList.add("is-invalid"); errorEl.textContent = message; errorEl.classList.add("is-visible"); }
  else { input.classList.remove("is-invalid"); errorEl.classList.remove("is-visible"); errorEl.textContent = ""; }
}
function setFormMessage(el, message, type) {
  el.textContent = message; el.className = "form-message";
  if (message) el.classList.add("is-visible", `form-message--${type}`);
}

/* ---------- init ---------- */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-role]").forEach(card => {
    const role = card.getAttribute("data-role");
    card.addEventListener("click", () => selectRole(role, card));
    card.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selectRole(role, card); } });
  });

  document.querySelectorAll("[data-nav-home]").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      showView("login");
      const target = link.getAttribute("href");
      if (target && target !== "#login") document.querySelector(target)?.scrollIntoView({ behavior: "smooth" });
    });
  });

  document.querySelectorAll("[data-role-switch]").forEach(btn => {
    btn.addEventListener("click", () => applyRoleTheme(btn.getAttribute("data-role-switch")));
  });

  document.getElementById("logoutBtn").addEventListener("click", e => {
    e.preventDefault();
    document.getElementById("loginForm").reset();
    setFormMessage(document.getElementById("formMessage"), "", null);
    clearRemembered();
    Utils.showToast("Logged out.", "success");
    showView("login");
  });

  document.querySelectorAll("[data-nav-link]").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      document.querySelectorAll("[data-nav-link]").forEach(l => l.classList.remove("is-active"));
      link.classList.add("is-active");
      const page = link.getAttribute("data-page");
      if (page) {
        showPage(page);
      } else {
        const label = link.textContent.trim().replace("Soon", "").trim();
        Utils.showToast(`${label} module — coming soon.`, "success");
      }
    });
  });

  const downloadBtn = document.getElementById("downloadReportBtn");
  if (downloadBtn) downloadBtn.addEventListener("click", downloadReportCsv);

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

  /* ---------- real login: backend ko call karta hai ---------- */
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
      setFieldError(idInput, idError, "");
      setFormMessage(formMessage, result.message || "Incorrect ID or password. Please try again.", "error");
      Utils.showToast("Login failed — check your ID and password.", "error");
      return;
    }

    const rememberChecked = document.getElementById("rememberMe").checked;
    if (rememberChecked) {
      saveRemembered(currentRole, enteredId, enteredPassword);
    } else {
      clearRemembered();
    }
    saveRecentLogin(currentRole, enteredId, enteredPassword);

    setFormMessage(formMessage, `Welcome back! Signed in as ${Utils.capitalize(currentRole)} (${result.name}).`, "success");
    Utils.showToast("Login successful.", "success");
    setTimeout(() => enterDashboard(currentRole, result.name), 700);
  });

  /* ---------- auto sign-in if credentials were remembered ---------- */
  const rememberedOnLoad = getRemembered();
  if (rememberedOnLoad) {
    Utils.showToast(`Welcome back — signed in automatically as ${Utils.capitalize(rememberedOnLoad.role)}.`, "success");
    enterDashboard(rememberedOnLoad.role, rememberedOnLoad.id);
  }
});
