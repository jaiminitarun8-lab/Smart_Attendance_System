"use strict";

const role = window.ATTENDAI_ROLE;   // "student" ya "teacher" — HTML file me set hota hai
const params = new URLSearchParams(window.location.search);
const userId = params.get("id") || "";
const userName = params.get("name") || (role === "teacher" ? "Faculty" : "Student");

function capitalize(s){ return s ? s.charAt(0).toUpperCase() + s.slice(1) : ""; }

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

/* ---------- Leave Management (real backend se) ---------- */
async function renderLeavePage() {
  if (role === "student") {
    const historyBody = document.getElementById("leaveHistoryBody");
    if (!historyBody) return;

    const res = await fetch(`/api/leave/student/${encodeURIComponent(userId)}`);
    const data = await res.json();
    const leaves = data.leaves || [];
    const summary = data.summary || {};

    const approvedEl = document.getElementById("leaveApprovedCount");
    const pendingEl = document.getElementById("leavePendingCount");
    const rejectedEl = document.getElementById("leaveRejectedCount");
    if (approvedEl) approvedEl.textContent = summary.approved ?? 0;
    if (pendingEl) pendingEl.textContent = summary.pending ?? 0;
    if (rejectedEl) rejectedEl.textContent = summary.rejected ?? 0;

    if (leaves.length === 0) {
      historyBody.innerHTML = `<tr><td colspan="4" style="color:var(--color-paper-dim);">Koi leave request nahi hai abhi.</td></tr>`;
      return;
    }

    historyBody.innerHTML = leaves.map(lv => `
      <tr>
        <td>${lv.reason || "—"}</td>
        <td>${lv.start_date || "—"}</td>
        <td>${lv.end_date || "—"}</td>
        <td><span class="status-pill ${lv.status === "approved" ? "present" : lv.status === "rejected" ? "absent" : "pending"}">${capitalize(lv.status)}</span></td>
      </tr>`).join("");
  } else {
    const body = document.getElementById("leaveRequestsBody");
    if (!body) return;

    const res = await fetch(`/api/leave/section/B`);
    const data = await res.json();
    const leaves = data.leaves || [];
    const summary = data.summary || {};

    const pendingEl = document.getElementById("facLeavePendingCount");
    const approvedEl = document.getElementById("facLeaveApprovedCount");
    const rejectedEl = document.getElementById("facLeaveRejectedCount");
    const totalEl = document.getElementById("facLeaveTotalCount");
    if (pendingEl) pendingEl.textContent = summary.pending ?? 0;
    if (approvedEl) approvedEl.textContent = summary.approved ?? 0;
    if (rejectedEl) rejectedEl.textContent = summary.rejected ?? 0;
    if (totalEl) totalEl.textContent = summary.total ?? 0;

    if (leaves.length === 0) {
      body.innerHTML = `<tr><td colspan="7" style="color:var(--fl-text-dim);">Koi leave request nahi hai abhi.</td></tr>`;
      return;
    }

    body.innerHTML = leaves.map(lv => `
      <tr>
        <td>${lv.student_name || lv.user_id}</td>
        <td>${[lv.class_name, lv.section, lv.department].filter(Boolean).join(" / ") || "—"}</td>
        <td>${lv.reason || "—"}</td>
        <td>${lv.start_date || "—"}</td>
        <td>${lv.end_date || "—"}</td>
        <td><span class="status-pill ${lv.status === "approved" ? "present" : lv.status === "rejected" ? "absent" : "pending"}">${capitalize(lv.status)}</span></td>
        <td>${lv.status === "pending"
          ? `<button type="button" class="btn btn-primary" style="padding:.35rem .8rem;font-size:var(--fs-xs);" data-approve-leave="${lv.id}">Approve</button>
             <button type="button" style="padding:.35rem .8rem;font-size:var(--fs-xs);margin-left:.4rem;border:1px solid #e15554;color:#e15554;border-radius:8px;background:transparent;font-weight:600;cursor:pointer;" data-reject-leave="${lv.id}">Reject</button>`
          : "—"}</td>
      </tr>`).join("");

    body.querySelectorAll("[data-approve-leave]").forEach(btn => {
      btn.addEventListener("click", async () => {
        await fetch(`/api/leave/${btn.getAttribute("data-approve-leave")}/approve`, {
          method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({})
        });
        renderLeavePage();
      });
    });
    body.querySelectorAll("[data-reject-leave]").forEach(btn => {
      btn.addEventListener("click", async () => {
        await fetch(`/api/leave/${btn.getAttribute("data-reject-leave")}/reject`, {
          method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({})
        });
        renderLeavePage();
      });
    });
  }
}

/* ---------- Notifications (real backend se) ---------- */
async function renderBellCount() {
  const el = document.getElementById("notifBellCount");
  if (!el || !userId) return;
  try {
    const res = await fetch(`/api/notifications/${encodeURIComponent(userId)}`);
    const data = await res.json();
    const count = data.unread_count || 0;
    el.textContent = count;
    el.style.display = count > 0 ? "flex" : "none";
  } catch (e) { /* ignore */ }
}

async function renderNotificationsPage() {
  const list = document.getElementById("notificationsList");
  if (!list) return;

  const res = await fetch(`/api/notifications/${encodeURIComponent(userId)}`);
  const data = await res.json();
  const items = data.notifications || [];

  const countLabel = document.getElementById("notificationCountLabel");
  if (countLabel) countLabel.textContent = `${data.unread_count || 0} unread`;

  if (items.length === 0) {
    list.innerHTML = `<p style="color:var(--color-paper-dim);font-size:var(--fs-sm);padding:var(--space-3) 0;">Koi notification nahi hai abhi.</p>`;
    return;
  }

  list.innerHTML = items.map(n => `
    <div class="activity-row" data-notif-id="${n.id}" style="${n.is_read ? "opacity:.55;" : ""}cursor:pointer;">
      <span class="activity-row__dot ${n.is_read ? "" : "absent"}"></span>
      <span class="activity-row__main">${n.title}</span>
      <span class="activity-row__meta">${n.created_at ? new Date(n.created_at).toLocaleDateString() : ""}</span>
    </div>`).join("");

  list.querySelectorAll("[data-notif-id]").forEach(row => {
    row.addEventListener("click", async () => {
      await fetch(`/api/notifications/${row.getAttribute("data-notif-id")}/read`, { method: "POST" });
      renderNotificationsPage();
      renderBellCount();
    });
  });
}

/* ---------- Attendance (real backend se) ---------- */
async function renderBarChart() {
  const el = document.getElementById("barChart");
  if (!el) return;

  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  let values = [0, 0, 0, 0, 0, 0, 0];

  if (role === "student") {
    try {
      const res = await fetch(`/api/attendance/student/${encodeURIComponent(userId)}/summary`);
      const data = await res.json();
      if (data.weekly) values = data.weekly;
    } catch (e) { /* keep zeros on failure */ }
  }

  el.innerHTML = values.map((v, i) => `
    <div class="bar-chart__col">
      <div class="bar-chart__bar" style="height:${Math.max(v, 4)}%"></div>
      <span class="bar-chart__day">${days[i]}</span>
    </div>`).join("");
}

async function renderAttendanceLog() {
  const body = document.getElementById("attendanceLogBody");
  const monthPctEl = document.getElementById("monthAttendancePct");
  const monthDeltaEl = document.getElementById("monthAttendanceDelta");
  const riskValueEl = document.getElementById("riskStatusValue");
  const riskDeltaEl = document.getElementById("riskStatusDelta");
  if (!body && !monthPctEl) return;

  const res = await fetch(`/api/attendance/student/${encodeURIComponent(userId)}/summary`);
  const data = await res.json();

  if (monthPctEl) monthPctEl.textContent = `${data.percentage ?? 0}%`;
  if (monthDeltaEl) monthDeltaEl.textContent = `${data.present_days ?? 0} of ${data.total_classes ?? 0} days present`;
  if (riskValueEl) {
    const risk = data.risk_level || "green";
    riskValueEl.textContent = risk.toUpperCase();
    riskValueEl.className = "stat-card__value " + (risk === "red" ? "absent" : risk === "yellow" ? "pending" : "present");
  }
  if (riskDeltaEl) {
    const risk = data.risk_level || "green";
    if (risk === "red") riskDeltaEl.textContent = "Low attendance - please improve";
    else if (risk === "yellow") riskDeltaEl.textContent = "Attendance needs attention";
    else riskDeltaEl.textContent = "Attendance is healthy";
  }

  if (body) {
    const rows = data.recent_log || [];
    body.innerHTML = rows.length
      ? rows.map(r => `
        <tr>
          <td>${r.subject || "—"}</td>
          <td>${r.date}</td>
          <td><span class="status-pill ${r.status === "present" ? "present" : "absent"}">${capitalize(r.status)}</span></td>
        </tr>`).join("")
      : `<tr><td colspan="3" style="color:var(--color-paper-dim);">Abhi tak koi attendance record nahi hai.</td></tr>`;
  }
}

/* ---------- Reports page: monthly breakdown (real backend se) ---------- */
async function renderReportsPage() {
  const tableBody = document.getElementById("reportTableBody");
  const termPctEl = document.getElementById("reportTermPct");
  const presentDaysEl = document.getElementById("reportPresentDays");
  const absentDaysEl = document.getElementById("reportAbsentDays");
  const bestWeekEl = document.getElementById("reportBestWeek");
  if (!tableBody && !termPctEl) return;

  const endpoint = role === "student"
    ? `/api/attendance/student/${encodeURIComponent(userId)}/monthly`
    : `/api/attendance/section/B/monthly`;

  const res = await fetch(endpoint);
  const data = await res.json();
  const months = data.months || [];

  if (termPctEl) termPctEl.textContent = `${data.overall_pct ?? 0}%`;
  if (presentDaysEl) presentDaysEl.textContent = data.present_days ?? 0;
  if (absentDaysEl) absentDaysEl.textContent = data.absent_days ?? 0;
  if (bestWeekEl) bestWeekEl.textContent = `${data.best_rate ?? 0}%`;

  if (tableBody) {
    tableBody.innerHTML = months.length
      ? months.map(m => `
        <tr>
          <td>${m.month}</td>
          <td>${m.present}</td>
          <td>${m.absent}</td>
          <td><span class="status-pill ${m.rate >= 75 ? "present" : m.rate >= 50 ? "pending" : "absent"}">${m.rate}%</span></td>
        </tr>`).join("")
      : `<tr><td colspan="4" style="color:var(--color-paper-dim);">Abhi tak koi attendance record nahi hai.</td></tr>`;
  }
}

/* ---------- Timetable (real backend se) ---------- */
async function renderTimetable() {
  const body = document.getElementById("timetableBody");
  if (!body) return;

  const res = await fetch(`/api/timetable/section/B`);
  const data = await res.json();
  const rows = data.rows || [];

  body.innerHTML = rows.length
    ? rows.map(row => `
      <tr>
        <td style="font-family:var(--font-mono);font-size:var(--fs-xs);color:var(--color-paper-dim);">${row.time}</td>
        <td>${row.Mon}</td><td>${row.Tue}</td><td>${row.Wed}</td><td>${row.Thu}</td><td>${row.Fri}</td>
      </tr>`).join("")
    : `<tr><td colspan="6" style="color:var(--color-paper-dim);">Timetable abhi set nahi hui hai.</td></tr>`;
}

/* ---------- Donut chart + stat cards (faculty dashboard only) ---------- */
async function renderDonut() {
  const donut = document.getElementById("donutChart");
  if (!donut || role !== "teacher") return;

  const res = await fetch(`/api/attendance/section/B/summary`);
  const data = await res.json();

  const total = data.total_students || 0;
  const presentCount = data.present_today || 0;
  const absentCount = data.absent_today || 0;
  const pendingCount = Math.max(total - presentCount - absentCount, 0);

  const presentPct = total ? Math.round((presentCount / total) * 100) : 0;
  const absentPct = total ? Math.round((absentCount / total) * 100) : 0;
  const latePct = Math.max(100 - presentPct - absentPct, 0);

  donut.style.setProperty("--present", presentPct);
  donut.style.setProperty("--absent", absentPct);
  donut.style.setProperty("--late", latePct);

  const pctEl = document.getElementById("donutPct");
  if (pctEl) pctEl.textContent = `${presentPct}%`;

  const presentEl = document.getElementById("donutPresentCount");
  if (presentEl) presentEl.textContent = `${presentCount} (${presentPct}%)`;

  const absentEl = document.getElementById("donutAbsentCount");
  if (absentEl) absentEl.textContent = `${absentCount} (${absentPct}%)`;

  const lateEl = document.getElementById("donutLateCount");
  if (lateEl) lateEl.textContent = `${pendingCount} not marked`;

  const presentValueEl = document.getElementById("facStudentsPresentValue");
  if (presentValueEl) presentValueEl.textContent = presentCount;
  const presentDeltaEl = document.getElementById("facStudentsPresentDelta");
  if (presentDeltaEl) presentDeltaEl.textContent = `out of ${total} enrolled`;
  const todayAttendanceEl = document.getElementById("facTodayAttendanceValue");
  if (todayAttendanceEl) todayAttendanceEl.textContent = `${data.avg_attendance_pct ?? 0}%`;
}

async function renderPendingApprovalsCount() {
  const el = document.getElementById("facPendingApprovalsValue");
  if (!el) return;
  const res = await fetch(`/api/leave/section/B`);
  const data = await res.json();
  el.textContent = data.summary?.pending ?? 0;
}

/* ---------- Roster + mark attendance (faculty dashboard only) ---------- */
async function renderRoster() {
  const body = document.getElementById("rosterTableBody");
  if (!body) return;

  const subjectInput = document.getElementById("rosterSubject");
  const subject = (subjectInput?.value || "General").trim() || "General";

  const res = await fetch(`/api/attendance/section/B/today?subject=${encodeURIComponent(subject)}`);
  const data = await res.json();
  const roster = data.roster || [];

  const countLabel = document.getElementById("rosterCountLabel");
  if (countLabel) countLabel.textContent = `${roster.length} students`;

  if (roster.length === 0) {
    body.innerHTML = `<tr><td colspan="4" style="color:var(--fl-text-dim);">Section me koi student nahi mila.</td></tr>`;
    return;
  }

  body.innerHTML = roster.map(s => `
    <tr>
      <td>${s.name}</td>
      <td>${s.roll_no || s.student_id}</td>
      <td><span class="status-pill ${s.status === "present" ? "present" : s.status === "absent" ? "absent" : "pending"}">${capitalize(s.status)}</span></td>
      <td>
        <button type="button" class="btn btn-primary" style="padding:.3rem .7rem;font-size:var(--fs-xs);" data-mark="${s.student_id}" data-status="present">Present</button>
        <button type="button" style="padding:.3rem .7rem;font-size:var(--fs-xs);margin-left:.3rem;border:1px solid #e15554;color:#e15554;border-radius:8px;background:transparent;font-weight:600;cursor:pointer;" data-mark="${s.student_id}" data-status="absent">Absent</button>
      </td>
    </tr>`).join("");

  body.querySelectorAll("[data-mark]").forEach(btn => {
    btn.addEventListener("click", async () => {
      await fetch("/api/attendance/mark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: btn.getAttribute("data-mark"),
          user_type: "student",
          subject,
          date: new Date().toISOString().slice(0, 10),
          status: btn.getAttribute("data-status"),
        }),
      });
      renderRoster();
      renderDonut();
    });
  });
}

function renderActivity() {
  document.getElementById("activityList").innerHTML = ACTIVITY[role].map(item => `
    <div class="activity-row">
      <span class="activity-row__dot ${item.present ? "present" : "absent"}"></span>
      <span class="activity-row__main">${item.text}</span>
      <span class="activity-row__meta">${item.time}</span>
    </div>`).join("");
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
    marks: ["Marks", role === "student" ? "Your subject-wise performance" : "Manage marks for your class"],
    leave: ["Leave management", role === "student" ? "Apply for leave and track your requests" : "Review and approve student leave requests"],
    notifications: ["Notifications", "Recent alerts and updates"],
    challenges: ["Challenges", "Launch and monitor live attendance challenges"],
    students: ["Students", "Section B student list and attendance"],
    settings: ["Settings", "Account and notification preferences"]
  };
  const [title, subtitle] = titles[page] || titles.dashboard;
  const titleEl = document.getElementById("pageTitle");
  const subtitleEl = document.getElementById("pageSubtitle");
  if (titleEl) titleEl.textContent = title;
  if (subtitleEl) subtitleEl.textContent = subtitle;
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
  renderDonut();
  renderActivity();
  renderTimetable();
  renderReportsPage();
  renderTasks();
  renderActivitiesPage();
  renderMarksPage();
  renderLeavePage();
  renderNotificationsPage();
  renderBellCount();
  renderAttendanceLog();
  renderRoster();
  renderPendingApprovalsCount();
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

  const rosterSubject = document.getElementById("rosterSubject");
  if (rosterSubject) rosterSubject.addEventListener("change", renderRoster);

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

  const leaveApplyForm = document.getElementById("leaveApplyForm");
  if (leaveApplyForm) {
    leaveApplyForm.addEventListener("submit", async e => {
      e.preventDefault();
      const startDate = document.getElementById("leaveFromDate").value;
      const endDate = document.getElementById("leaveToDate").value;
      const reason = document.getElementById("leaveReason").value.trim();
      if (!startDate || !endDate || !reason) return;

      await fetch("/api/leave", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, user_type: "student", start_date: startDate, end_date: endDate, reason })
      });
      renderLeavePage();
      leaveApplyForm.reset();
    });
  }
});
