"use strict";

const role = window.ATTENDAI_ROLE;   // "student" ya "teacher" — HTML file me set hota hai
const params = new URLSearchParams(window.location.search);
const userId = params.get("id") || "";
const userName = params.get("name") || (role === "teacher" ? "Faculty" : "Student");

function capitalize(s){ return s ? s.charAt(0).toUpperCase() + s.slice(1) : ""; }

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

/* ---------- Tasks (real backend se data aata hai) ---------- */
async function fetchTasks() {
  if (role === "student") {
    const res = await fetch(`/api/tasks/student/${encodeURIComponent(userId)}`);
    const data = await res.json();
    return data.tasks || [];
  } else {
    const res = await fetch(`/api/tasks/faculty/${encodeURIComponent(userId)}`);
    const data = await res.json();
    return data.tasks || [];
  }
}

async function completeTask(taskId) {
  await fetch(`/api/tasks/${taskId}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: userId })
  });
}

async function renderTasks() {
  const list = document.getElementById("taskList");
  const countLabel = document.getElementById("taskCountLabel");
  if (!list) return;

  const tasks = await fetchTasks();

  if (role === "student") {
    const pending = tasks.filter(t => !t.completed).length;
    if (countLabel) countLabel.textContent = `${pending} pending · ${tasks.length} total`;
  } else {
    const totalCompletions = tasks.reduce((s, t) => s + t.completed_count, 0);
    if (countLabel) countLabel.textContent = `${tasks.length} tasks assigned`;
  }

  if (tasks.length === 0) {
    list.innerHTML = `<p style="color:var(--color-paper-dim);font-size:var(--fs-sm);padding:var(--space-3) 0;">Koi task assign nahi hua abhi.</p>`;
    return;
  }

  list.innerHTML = tasks.map(task => `
    <div class="quick-action" style="cursor:default;">
      <div>
        <div style="font-weight:600;${task.completed ? "text-decoration:line-through;color:var(--color-paper-dim);" : ""}">${task.title}</div>
        <div style="font-family:var(--font-mono);font-size:.7rem;color:var(--color-paper-dim);margin-top:.25rem;">${task.subject || ""} · Due ${task.due_date || "—"}</div>
      </div>
      ${role === "student"
        ? (task.completed
            ? `<span class="status-pill present">Completed</span>`
            : `<button type="button" class="btn btn-primary" style="padding:.4rem .9rem;font-size:var(--fs-xs);" data-complete-task="${task.id}">Mark complete</button>`)
        : `<span class="status-pill ${task.completed_count > 0 ? "present" : "pending"}">${task.completed_count} completed</span>`
      }
    </div>`).join("");

  if (role === "student") {
    list.querySelectorAll("[data-complete-task]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = Number(btn.getAttribute("data-complete-task"));
        await completeTask(id);
        renderTasks();
      });
    });
  }
}

/* ---------- Other Activities (real backend se) ---------- */
async function renderActivitiesPage() {
  const announcementsEl = document.getElementById("announcementsList");
  const extraEl = document.getElementById("extracurricularList");
  if (!announcementsEl && !extraEl) return;

  const res = await fetch("/api/activities");
  const data = await res.json();
  const announcements = data.announcements || [];
  const extracurricular = data.extracurricular || [];

  if (announcementsEl) {
    announcementsEl.innerHTML = announcements.map(item => `
      <div class="activity-row">
        <span class="activity-row__dot present"></span>
        <span class="activity-row__main">${item.title}${item.description ? " — " + item.description : ""}</span>
        <span class="activity-row__meta">${item.event_date || ""}</span>
      </div>`).join("") || `<p style="color:var(--color-paper-dim);font-size:var(--fs-sm);">Koi announcement nahi hai abhi.</p>`;
  }
  if (extraEl) {
    extraEl.innerHTML = extracurricular.map(item => `
      <div class="activity-row">
        <span class="activity-row__dot present"></span>
        <span class="activity-row__main">${item.title}${item.description ? " — " + item.description : ""}</span>
        <span class="activity-row__meta">${item.event_date || ""}</span>
      </div>`).join("") || `<p style="color:var(--color-paper-dim);font-size:var(--fs-sm);">Koi activity nahi hai abhi.</p>`;
  }
}

/* ---------- Marks Management (real backend se) ---------- */
async function renderMarksPage() {
  const body = document.getElementById("marksTableBody");
  if (!body) return;

  if (role === "student") {
    const res = await fetch(`/api/marks/student/${encodeURIComponent(userId)}`);
    const data = await res.json();
    const marks = data.marks || [];

    body.innerHTML = marks.map(m => {
      return `<tr><td>${m.subject}</td><td>${m.obtained}</td><td>${m.max_marks}</td><td>${m.percentage}%</td><td><span class="status-pill ${m.percentage >= 75 ? "present" : m.percentage >= 50 ? "pending" : "absent"}">${m.grade}</span></td></tr>`;
    }).join("");

    if (marks.length > 0) {
      document.getElementById("marksOverallPct").textContent = `${data.overall_pct}%`;
      document.getElementById("marksOverallGrade").textContent = data.overall_grade;
      document.getElementById("marksBestSubject").textContent = data.best_subject;
      document.getElementById("marksBestScore").textContent = `${data.best_pct}%`;
      document.getElementById("marksWorstSubject").textContent = data.worst_subject;
      document.getElementById("marksWorstScore").textContent = `${data.worst_pct}%`;
    }
  } else {
    const res = await fetch(`/api/marks/section/B`);
    const data = await res.json();
    const marks = data.marks || [];

    body.innerHTML = marks.map(m => {
      return `<tr><td>${m.student_name}</td><td>${m.obtained}</td><td>${m.max_marks}</td><td>${m.percentage}%</td><td><span class="status-pill ${m.percentage >= 75 ? "present" : m.percentage >= 50 ? "pending" : "absent"}">${m.grade}</span></td></tr>`;
    }).join("");
  }
}

function renderBarChart() {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const values = WEEK_DATA[role];
  document.getElementById("barChart").innerHTML = values.map((v, i) => `
    <div class="bar-chart__col">
      <div class="bar-chart__bar" style="height:${Math.max(v, 4)}%"></div>
      <span class="bar-chart__day">${days[i]}</span>
    </div>`).join("");
}

function renderActivity() {
  document.getElementById("activityList").innerHTML = ACTIVITY[role].map(item => `
    <div class="activity-row">
      <span class="activity-row__dot ${item.present ? "present" : "absent"}"></span>
      <span class="activity-row__main">${item.text}</span>
      <span class="activity-row__meta">${item.time}</span>
    </div>`).join("");
}

function renderTimetable() {
  const body = document.getElementById("timetableBody");
  body.innerHTML = TIMETABLE[role].map(row => `
    <tr>
      <td style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--color-paper-dim);">${row[0]}</td>
      ${row.slice(1).map(cell => `<td>${cell}</td>`).join("")}
    </tr>`).join("");
}

function populateProfile() {
  document.getElementById("profileAvatar").textContent = userName.charAt(0).toUpperCase();
  document.getElementById("profileName").textContent = userName;
  document.getElementById("profileIdLine").textContent = `ID · ${userId || "—"}`;
  document.getElementById("profileEmail").textContent = `${userId.toLowerCase().replace(/[^a-z0-9]/g, "")}@attendai.edu`;
}

function populateTopbar() {
  document.getElementById("dashName").textContent = userName;
  document.getElementById("dashDate").textContent = new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });
  document.getElementById("profileChipAvatar").textContent = userName.charAt(0).toUpperCase();
  document.getElementById("profileChipName").textContent = userName;
}

function showPage(page) {
  document.querySelectorAll("[data-page]").forEach(el => el.classList.toggle("is-page-active", el.dataset.page === page));
  const titles = {
    dashboard: [`Welcome back, ${userName}`, `${capitalize(role)} sign-in · ${document.getElementById("dashDate").textContent}`],
    profile: ["My profile", "Personal and account details on file"],
    reports: ["Attendance reports", "Term summary and monthly breakdown"],
    timetable: ["Weekly timetable", "Your scheduled classes, Monday to Friday"],
    tasks: ["Tasks", role === "student" ? "Tasks assigned by your faculty" : "Tasks you've assigned to your class"],
    activities: ["Other activities", "Announcements, events, and extra-curriculars"],
    marks: ["Marks", role === "student" ? "Your subject-wise performance" : "Manage marks for your class"]
  };
  const [title, subtitle] = titles[page] || titles.dashboard;
  document.getElementById("pageTitle").textContent = title;
  document.getElementById("pageSubtitle").textContent = subtitle;
}

function downloadReportCsv() {
  const table = document.getElementById("reportTable");
  const rows = Array.from(table.querySelectorAll("tr")).map(tr =>
    Array.from(tr.querySelectorAll("th,td")).map(cell => `"${cell.textContent.trim()}"`).join(",")
  );
  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "attendai-report.csv";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

document.addEventListener("DOMContentLoaded", () => {
  populateTopbar();
  populateProfile();
  renderBarChart();
  renderActivity();
  renderTimetable();
  renderTasks();
  renderActivitiesPage();
  renderMarksPage();
  showPage("dashboard");

  document.querySelectorAll("[data-nav-link]").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      document.querySelectorAll("[data-nav-link]").forEach(l => l.classList.remove("is-active"));
      link.classList.add("is-active");
      const page = link.getAttribute("data-page");
      if (page) showPage(page);
    });
  });

  const downloadBtn = document.getElementById("downloadReportBtn");
  if (downloadBtn) downloadBtn.addEventListener("click", downloadReportCsv);

  const assignTaskForm = document.getElementById("assignTaskForm");
  if (assignTaskForm) {
    assignTaskForm.addEventListener("submit", async e => {
      e.preventDefault();
      const title = document.getElementById("taskTitle").value.trim();
      const subject = document.getElementById("taskSubject").value.trim();
      const dueDate = document.getElementById("taskDueDate").value;
      if (!title || !subject || !dueDate) return;

      await fetch("/api/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, subject, due_date: dueDate, section: "B", assigned_by: userId })
      });
      renderTasks();
      assignTaskForm.reset();
    });
  }
});
