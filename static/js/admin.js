// Admin Dashboard Client Logic

let adminToken = localStorage.getItem("tighra_admin_token") || null;
let adminUser = null;

document.addEventListener("DOMContentLoaded", () => {
  checkAdminAuth();
});

async function checkAdminAuth() {
  if (!adminToken) {
    showAdminLoginPrompt();
    return;
  }
  try {
    const res = await fetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${adminToken}` }
    });
    if (res.ok) {
      adminUser = await res.json();
      if (adminUser.role !== "admin") {
        alert("Access Denied: Requires Administrator role.");
        logoutAdmin();
        return;
      }
      showAdminDashboard();
      loadAnalytics();
      loadAdminBoats();
      loadAdminBookings();
    } else {
      logoutAdmin();
    }
  } catch (e) {
    showAdminLoginPrompt();
  }
}

function showAdminLoginPrompt() {
  document.getElementById("adm-login-prompt").style.display = "block";
  document.getElementById("adm-dashboard-area").style.display = "none";
  document.getElementById("adm-auth-btn").style.display = "block";
  document.getElementById("adm-user-profile").style.display = "none";
}

function showAdminDashboard() {
  document.getElementById("adm-login-prompt").style.display = "none";
  document.getElementById("adm-dashboard-area").style.display = "block";
  document.getElementById("adm-auth-btn").style.display = "none";
  document.getElementById("adm-user-profile").style.display = "flex";
  document.getElementById("adm-name").textContent = `⚡ ${adminUser.name}`;
}

async function quickLoginAdmin() {
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "admin@tighra.gov.in", password: "Admin@123" })
    });
    const data = await res.json();
    if (res.ok) {
      adminToken = data.access_token;
      adminUser = data.user;
      localStorage.setItem("tighra_admin_token", adminToken);
      showAdminDashboard();
      loadAnalytics();
      loadAdminBoats();
      loadAdminBookings();
    } else {
      alert(`Admin Login Failed: ${data.detail}`);
    }
  } catch (e) {
    alert("Login error");
  }
}

function logoutAdmin() {
  adminToken = null;
  adminUser = null;
  localStorage.removeItem("tighra_admin_token");
  showAdminLoginPrompt();
}

async function loadAnalytics() {
  if (!adminToken) return;
  try {
    const res = await fetch("/api/admin/analytics", {
      headers: { Authorization: `Bearer ${adminToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      document.getElementById("kpi-total-revenue").textContent = `₹${data.total_revenue.toLocaleString('en-IN')}`;
      document.getElementById("kpi-total-bookings").textContent = data.total_bookings;
      document.getElementById("kpi-active-boats").textContent = data.active_boats;
      document.getElementById("kpi-today-passengers").textContent = data.today_passengers;
    }
  } catch (e) {
    console.error("Analytics error", e);
  }
}

async function loadAdminBoats() {
  if (!adminToken) return;
  const grid = document.getElementById("admin-boats-grid");
  grid.innerHTML = `<p>Loading fleet...</p>`;

  try {
    const res = await fetch("/api/boats");
    const boats = await res.json();
    grid.innerHTML = "";

    boats.forEach(b => {
      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
          <span class="boat-type-badge">${b.boat_type}</span>
          <span class="status-badge ${b.status === 'active' ? 'badge-paid' : 'badge-cancelled'}">${b.status.toUpperCase()}</span>
        </div>
        <h3 style="font-size: 1.15rem; font-weight: 700;">${b.boat_name}</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Capacity: <strong>${b.capacity} Persons</strong></p>
        <p style="font-size: 1.1rem; font-weight: 800; color: var(--success); margin-bottom: 1rem;">₹${b.price_per_person} / seat</p>
        <button class="btn ${b.status === 'active' ? 'btn-danger' : 'btn-success'} btn-block" onclick="toggleBoatStatus(${b.id}, '${b.status === 'active' ? 'maintenance' : 'active'}')">
          ${b.status === 'active' ? 'Set to Maintenance' : 'Set to Active'}
        </button>
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    grid.innerHTML = `<p>Error loading fleet</p>`;
  }
}

async function toggleBoatStatus(boatId, newStatus) {
  try {
    const res = await fetch(`/api/admin/boats/${boatId}/status?status_val=${newStatus}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${adminToken}` }
    });
    if (res.ok) {
      loadAdminBoats();
      loadAnalytics();
    } else {
      alert("Error toggling boat status.");
    }
  } catch (e) {
    alert("Server error.");
  }
}

async function handleCreateBoat(e) {
  e.preventDefault();
  const boat_name = document.getElementById("add-boat-name").value;
  const boat_type = document.getElementById("add-boat-type").value;
  const capacity = parseInt(document.getElementById("add-boat-capacity").value);
  const price_per_person = parseFloat(document.getElementById("add-boat-price").value);
  const description = document.getElementById("add-boat-desc").value;

  try {
    const res = await fetch("/api/boats", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${adminToken}`
      },
      body: JSON.stringify({ boat_name, boat_type, capacity, price_per_person, description })
    });

    if (res.ok) {
      closeModal("add-boat-modal");
      loadAdminBoats();
      loadAnalytics();
      alert(`Boat '${boat_name}' created successfully!`);
    } else {
      const data = await res.json();
      alert(`Error creating boat: ${data.detail}`);
    }
  } catch (e) {
    alert("Error creating boat.");
  }
}

async function loadAdminBookings() {
  if (!adminToken) return;
  const tbody = document.getElementById("admin-bookings-tbody");
  const searchVal = document.getElementById("adm-search-input").value.trim();
  const statusVal = document.getElementById("adm-status-filter").value;

  let url = `/api/admin/bookings?`;
  if (searchVal) url += `search=${encodeURIComponent(searchVal)}&`;
  if (statusVal) url += `status=${encodeURIComponent(statusVal)}`;

  try {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${adminToken}` }
    });
    const bookings = await res.json();
    tbody.innerHTML = "";

    if (bookings.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" style="padding: 1.5rem; text-align: center; color: var(--text-muted);">No booking records found.</td></tr>`;
      return;
    }

    bookings.forEach(b => {
      let badgeClass = "badge-paid";
      if (b.booking_status === "USED") badgeClass = "badge-used";
      if (b.booking_status === "CANCELLED") badgeClass = "badge-cancelled";

      const tr = document.createElement("tr");
      tr.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
      tr.innerHTML = `
        <td style="padding: 0.85rem; font-family: monospace; font-weight: 700; color: #38bdf8;">${b.booking_ref}</td>
        <td style="padding: 0.85rem;">${b.user ? b.user.name : 'Tourist'}</td>
        <td style="padding: 0.85rem;">${b.boat ? b.boat.boat_name : 'Boat'}</td>
        <td style="padding: 0.85rem; font-size: 0.85rem;">${b.booking_date}<br><span style="color: var(--text-muted);">${b.slot ? b.slot.start_time : ''}</span></td>
        <td style="padding: 0.85rem;">${b.passenger_count}</td>
        <td style="padding: 0.85rem; font-weight: 700; color: var(--success);">₹${b.total_amount}</td>
        <td style="padding: 0.85rem;"><span class="status-badge ${badgeClass}">${b.booking_status}</span></td>
        <td style="padding: 0.85rem; font-family: monospace; font-size: 0.75rem; color: var(--text-muted);">${b.qr_token}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error("Bookings load error", e);
  }
}

function openModal(id) {
  document.getElementById(id).classList.add("active");
}

function closeModal(id) {
  document.getElementById(id).classList.remove("active");
}
