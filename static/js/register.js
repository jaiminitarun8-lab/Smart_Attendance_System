"use strict";

let currentRole = "student"; // "student" ya "teacher"

const roleLabels = document.querySelectorAll("[data-role-label]");
const idLabelsLower = document.querySelectorAll("[data-id-label-lower]");
const groupLabel = document.querySelector("[data-group-label]");
const regGroupInput = document.getElementById("regGroup");
const toggleStudent = document.getElementById("toggleStudent");
const toggleTeacher = document.getElementById("toggleTeacher");
const registerSubmit = document.getElementById("registerSubmit");

function setRole(role) {
  currentRole = role;

  toggleStudent.classList.toggle("is-active", role === "student");
  toggleStudent.setAttribute("aria-selected", role === "student");
  toggleTeacher.classList.toggle("is-active", role === "teacher");
  toggleTeacher.setAttribute("aria-selected", role === "teacher");

  roleLabels.forEach(el => { el.textContent = role === "student" ? "student" : "faculty"; });
  idLabelsLower.forEach(el => { el.textContent = role === "student" ? "student ID" : "faculty ID"; });

  if (groupLabel) groupLabel.textContent = role === "student" ? "College ID" : "Department";
  if (regGroupInput) regGroupInput.placeholder = role === "student" ? "e.g. CLG-2026-045" : "e.g. Computer Science";

  registerSubmit.innerHTML = `Create <span data-role-label>${role === "student" ? "student" : "faculty"}</span> account`;
}

toggleStudent.addEventListener("click", () => setRole("student"));
toggleTeacher.addEventListener("click", () => setRole("teacher"));

const togglePasswordBtn = document.getElementById("togglePassword");
const passwordInput = document.getElementById("regPassword");
togglePasswordBtn.addEventListener("click", () => {
  const isPassword = passwordInput.type === "password";
  passwordInput.type = isPassword ? "text" : "password";
  togglePasswordBtn.textContent = isPassword ? "Hide" : "Show";
  togglePasswordBtn.setAttribute("aria-pressed", String(isPassword));
});

function clearErrors() {
  document.querySelectorAll(".field-error").forEach(el => { el.textContent = ""; el.classList.remove("is-visible"); });
  const formMessage = document.getElementById("formMessage");
  formMessage.classList.remove("is-visible", "form-message--error");
  formMessage.textContent = "";
}

function showFieldError(id, message) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = message;
  el.classList.add("is-visible");
}

function showFormError(message) {
  const formMessage = document.getElementById("formMessage");
  formMessage.textContent = message;
  formMessage.classList.add("is-visible", "form-message--error");
}

document.getElementById("registerForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearErrors();

  const name = document.getElementById("regName").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const group = document.getElementById("regGroup").value.trim();   // section (student) ya department (faculty)
  const password = document.getElementById("regPassword").value;

  let hasError = false;
  if (!name) { showFieldError("regNameError", "Naam likhna zaroori hai."); hasError = true; }
  if (!email) { showFieldError("regEmailError", "Email likhna zaroori hai."); hasError = true; }
  if (!group) { showFieldError("regGroupError", currentRole === "student" ? "College ID likhna zaroori hai." : "Department likhna zaroori hai."); hasError = true; }
  if (!password || password.length < 6) { showFieldError("regPasswordError", "Password kam se kam 6 characters ka hona chahiye."); hasError = true; }
  if (hasError) return;

  const payload = currentRole === "student"
    ? { name, email, password, college_id: group }
    : { name, email, password, department: group };

  const endpoint = currentRole === "student" ? "/api/register/student" : "/api/register/faculty";

  registerSubmit.disabled = true;
  registerSubmit.classList.add("is-loading");

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (!data.success) {
      showFormError(data.message || "Registration fail ho gayi. Dobara try karo.");
      return;
    }

    document.getElementById("registerForm").style.display = "none";
    document.querySelector(".auth-toggle").style.display = "none";
    document.querySelector(".auth-banner").style.display = "none";
    document.getElementById("generatedIdText").textContent = data.id;
    document.getElementById("successMessage").style.display = "flex";
  } catch (err) {
    showFormError("Server se connect nahi ho paya. Backend chal raha hai check karo.");
  } finally {
    registerSubmit.disabled = false;
    registerSubmit.classList.remove("is-loading");
  }
});

setRole("student");
