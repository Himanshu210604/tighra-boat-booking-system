// Tighra Tourist App Client Logic (CarFerry & 3D Live Inspired)

let currentUser = null;
let currentToken = localStorage.getItem("tighra_token") || null;
let allBoats = [];
let selectedBoat = null;
let activePendingBookingData = null;

document.addEventListener("DOMContentLoaded", () => {
  initDateInput();
  checkAuthStatus();
  loadBoats();
  init3DParallax();
});

function toggleMobileNav() {
  const navMenu = document.getElementById("navLinksMenu");
  if (navMenu) {
    navMenu.classList.toggle("active");
  }
}

function closeMobileNav() {
  const navMenu = document.getElementById("navLinksMenu");
  if (navMenu) {
    navMenu.classList.remove("active");
  }
}

function initDateInput() {
  const today = new Date().toISOString().split("T")[0];
  const dateInput = document.getElementById("book-date");
  const heroDateInput = document.getElementById("hero-date-input");

  if (dateInput) {
    dateInput.min = today;
    dateInput.value = today;
  }
  if (heroDateInput) {
    heroDateInput.min = today;
    heroDateInput.value = today;
  }
}

// 3D Mouse Parallax & Tilt Effect
function init3DParallax() {
  const hero = document.getElementById("hero");
  const heroCard = document.getElementById("hero-card");
  const heroBg = document.getElementById("hero-bg");

  if (!hero || !heroCard) return;

  hero.addEventListener("mousemove", (e) => {
    const rect = hero.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * -6; // max 6 deg
    const rotateY = ((x - centerX) / centerX) * 6;  // max 6 deg

    heroCard.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(15px)`;
    if (heroBg) {
      heroBg.style.transform = `scale(1.05) translate(${rotateY * 1.5}px, ${-rotateX * 1.5}px)`;
    }
  });

  hero.addEventListener("mouseleave", () => {
    heroCard.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)`;
    if (heroBg) {
      heroBg.style.transform = `scale(1) translate(0px, 0px)`;
    }
  });
}

function switchHeroView(view) {
  const heroBg = document.getElementById("hero-bg");
  const btnWall = document.getElementById("btn-view-wall");
  const btnLake = document.getElementById("btn-view-lake");

  if (!heroBg) return;

  if (view === "wall") {
    heroBg.style.backgroundImage = "url('/static/images/tighra_dam_aerial_wall.png')";
    if (btnWall) btnWall.classList.add("active");
    if (btnLake) btnLake.classList.remove("active");
  } else {
    heroBg.style.backgroundImage = "url('/static/images/tighra_dam_lake_boats.png')";
    if (btnLake) btnLake.classList.add("active");
    if (btnWall) btnWall.classList.remove("active");
  }

  const heroElem = document.getElementById("hero");
  if (heroElem) {
    heroElem.scrollIntoView({ behavior: 'smooth' });
  }
}

async function checkAuthStatus() {
  if (!currentToken) {
    updateAuthUI(null);
    return;
  }
  try {
    const res = await fetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${currentToken}` }
    });
    if (res.ok) {
      currentUser = await res.json();
      updateAuthUI(currentUser);
      document.getElementById("my-tickets-nav").style.display = "block";
    } else {
      logout();
    }
  } catch (e) {
    console.error("Auth check error", e);
  }
}

function updateAuthUI(user) {
  const authButtons = document.getElementById("auth-buttons");
  const userProfile = document.getElementById("user-profile");
  const userName = document.getElementById("user-display-name");

  if (user) {
    authButtons.style.display = "none";
    userProfile.style.display = "flex";
    userName.textContent = `👋 ${user.name}`;
  } else {
    authButtons.style.display = "flex";
    userProfile.style.display = "none";
    document.getElementById("my-tickets-nav").style.display = "none";
  }
}

async function quickFillTourist() {
  window.location.href = "/login";
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok) {
      currentToken = data.access_token;
      currentUser = data.user;
      localStorage.setItem("tighra_token", currentToken);
      updateAuthUI(currentUser);
      closeModal("login-modal");
      alert(`Welcome back, ${currentUser.name}!`);
      loadMyTickets();
    } else {
      alert(`Login Failed: ${data.detail}`);
    }
  } catch (err) {
    alert("Error logging in. Server offline?");
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById("reg-name").value;
  const email = document.getElementById("reg-email").value;
  const phone = document.getElementById("reg-phone").value;
  const password = document.getElementById("reg-password").value;

  try {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, phone, password })
    });
    const data = await res.json();
    if (res.ok) {
      currentToken = data.access_token;
      currentUser = data.user;
      localStorage.setItem("tighra_token", currentToken);
      updateAuthUI(currentUser);
      closeModal("register-modal");
      alert(`Account created successfully! Welcome ${currentUser.name}`);
    } else {
      alert(`Registration Failed: ${data.detail}`);
    }
  } catch (err) {
    alert("Error during registration.");
  }
}

function logout() {
  currentToken = null;
  currentUser = null;
  localStorage.removeItem("tighra_token");
  updateAuthUI(null);
  switchTab("fleet");
}

async function loadBoats() {
  try {
    const res = await fetch("/api/boats");
    allBoats = await res.json();
    renderBoats(allBoats);
  } catch (e) {
    console.error("Error loading boats", e);
  }
}

function renderBoats(boats) {
  const grid = document.getElementById("boats-grid");
  grid.innerHTML = "";

  const customImages = {
    "Shikara": "/static/images/tighra_dam_lake_boats.png",
    "Speed Boat": "/static/images/tighra_dam_hero.png",
    "Motor Boat": "/static/images/tighra_dam_aerial_wall.png",
    "Paddle Boat": "/static/images/tighra_dam_lake_boats.png"
  };

  boats.forEach(boat => {
    const defaultImg = customImages[boat.boat_type] || "/static/images/tighra_dam_lake_boats.png";
    const card = document.createElement("div");
    card.className = "card boat-card";
    card.innerHTML = `
      <div class="boat-image-container">
        <span class="boat-type-badge">${boat.boat_type}</span>
        <img src="${defaultImg}" class="boat-image" alt="${boat.boat_name}">
      </div>
      <div class="boat-card-body">
        <h3 class="boat-title">${boat.boat_name}</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.85rem;">${boat.description || ''}</p>
        <p style="font-size: 0.85rem; color: #e2e8f0; margin-bottom: 1rem;"><i class="fa-solid fa-users" style="color: var(--primary);"></i> Capacity: <strong>${boat.capacity} Passengers</strong></p>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 1rem; border-top: 1px solid var(--card-border);">
          <div class="boat-price">₹${boat.price_per_person}<span style="font-size: 0.8rem; color: var(--text-muted); font-weight: normal;"> / seat</span></div>
          <button class="btn btn-primary" onclick="initiateBooking(${boat.id})"><i class="fa-solid fa-ticket"></i> Book Now</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

function filterBoats(type) {
  if (type === "all") {
    renderBoats(allBoats);
  } else {
    const filtered = allBoats.filter(b => b.boat_type === type);
    renderBoats(filtered);
  }
}

function handleQuickSearch() {
  const cat = document.getElementById("hero-boat-select").value;
  const dateVal = document.getElementById("hero-date-input").value;
  const slotVal = document.getElementById("hero-slot-select").value;
  const passengers = document.getElementById("hero-passengers").value;

  filterBoats(cat);

  document.getElementById("book-date").value = dateVal;
  document.getElementById("book-passengers").value = passengers;

  const fleetSec = document.getElementById("fleet-section");
  if (fleetSec) {
    fleetSec.scrollIntoView({ behavior: 'smooth' });
  }

  const matching = cat === "all" ? allBoats : allBoats.filter(b => b.boat_type === cat);
  if (matching.length > 0) {
    setTimeout(() => {
      initiateBooking(matching[0].id);
      if (slotVal !== "all") {
        document.getElementById("book-slot-id").value = slotVal;
      }
    }, 400);
  }
}

function initiateBooking(boatId) {
  if (!currentUser) {
    alert("Please log in to book boat tickets.");
    window.location.href = "/login";
    return;
  }
  selectedBoat = allBoats.find(b => b.id === boatId);
  if (!selectedBoat) return;

  document.getElementById("book-boat-id").value = selectedBoat.id;
  document.getElementById("book-boat-name").value = `${selectedBoat.boat_name} (${selectedBoat.boat_type})`;
  document.getElementById("book-rate-display").textContent = `₹${selectedBoat.price_per_person}`;

  loadAvailableSlots();
  openModal("booking-modal");
}

async function loadAvailableSlots() {
  if (!selectedBoat) return;
  const boatId = selectedBoat.id;
  const dateStr = document.getElementById("book-date").value;
  const slotSelect = document.getElementById("book-slot-id");

  slotSelect.innerHTML = `<option value="">Loading slots...</option>`;

  try {
    const res = await fetch(`/api/slots?boat_id=${boatId}&date_str=${dateStr}`);
    const slots = await res.json();

    slotSelect.innerHTML = `<option value="">-- Select Time Slot --</option>`;
    slots.forEach(slot => {
      const remaining = Math.max(0, Math.min(selectedBoat.capacity, slot.max_capacity) - slot.booked_count);
      const option = document.createElement("option");
      option.value = slot.id;
      option.textContent = `${slot.start_time} - ${slot.end_time} (${remaining} seats left)`;
      if (remaining <= 0) {
        option.disabled = true;
        option.textContent += " [FULL]";
      }
      slotSelect.appendChild(option);
    });
  } catch (e) {
    slotSelect.innerHTML = `<option value="">Error loading slots</option>`;
  }

  calculateTotalPrice();
}

function calculateTotalPrice() {
  if (!selectedBoat) return;
  const count = parseInt(document.getElementById("book-passengers").value) || 1;
  const total = selectedBoat.price_per_person * count;
  document.getElementById("book-total-display").textContent = `₹${total}`;
}

function togglePaymentInputs() {
  const method = document.getElementById("payment-method-select").value;
  document.getElementById("pay-input-upi").style.display = method === "upi" ? "block" : "none";
  document.getElementById("pay-input-card").style.display = method === "card" ? "block" : "none";
  document.getElementById("pay-input-netbanking").style.display = method === "netbanking" ? "block" : "none";
}

function handleBookingSubmit(e) {
  e.preventDefault();
  const slotId = document.getElementById("book-slot-id").value;
  if (!slotId) {
    alert("Please select a valid time slot.");
    return;
  }

  const boatId = selectedBoat.id;
  const dateStr = document.getElementById("book-date").value;
  const passengers = parseInt(document.getElementById("book-passengers").value) || 1;
  const total = selectedBoat.price_per_person * passengers;

  activePendingBookingData = {
    boat_id: boatId,
    slot_id: parseInt(slotId),
    booking_date: dateStr,
    passenger_count: passengers
  };

  document.getElementById("pay-modal-amount").textContent = `₹${total}`;
  togglePaymentInputs();
  closeModal("booking-modal");
  openModal("payment-modal");
}

async function processPaymentSuccess() {
  if (!activePendingBookingData) return;

  try {
    const res = await fetch("/api/bookings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${currentToken}`
      },
      body: JSON.stringify(activePendingBookingData)
    });
    const data = await res.json();

    if (res.ok) {
      closeModal("payment-modal");
      showDigitalTicket(data);
      activePendingBookingData = null;
    } else {
      alert(`Booking Error: ${data.detail}`);
    }
  } catch (e) {
    alert("Error processing payment and booking.");
  }
}

function showDigitalTicket(booking) {
  const container = document.getElementById("ticket-modal-content");
  container.innerHTML = `
    <div class="ticket-card">
      <span class="status-badge badge-paid">VERIFIED & PAID</span>
      <h4 style="font-size: 1.25rem; font-weight: 800; margin: 0.5rem 0 0.25rem;">${booking.boat ? booking.boat.boat_name : 'Tighra Boat'}</h4>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Ref: <strong>${booking.booking_ref}</strong></p>

      <div class="ticket-qr">
        <img src="/api/bookings/${booking.id}/qr-image" alt="QR Code">
        <div style="font-family: monospace; font-size: 0.75rem; color: #334155; margin-top: 0.25rem;">${booking.qr_token}</div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; text-align: left; font-size: 0.85rem; background: rgba(255,255,255,0.05); padding: 0.75rem; border-radius: 10px;">
        <div>📅 <strong>Date:</strong> ${booking.booking_date}</div>
        <div>👥 <strong>Passengers:</strong> ${booking.passenger_count}</div>
        <div>⏰ <strong>Slot:</strong> ${booking.slot ? booking.slot.start_time : ''}</div>
        <div>💰 <strong>Amount:</strong> ₹${booking.total_amount}</div>
      </div>
      <p style="font-size: 0.75rem; color: var(--primary); margin-top: 0.75rem;"><i class="fa-solid fa-camera"></i> Show this QR code to the gate staff for entry.</p>
    </div>
  `;
  openModal("ticket-modal");
}

async function loadMyTickets() {
  if (!currentToken) return;
  const grid = document.getElementById("my-tickets-grid");
  grid.innerHTML = `<p>Loading tickets...</p>`;

  try {
    const res = await fetch("/api/bookings/my", {
      headers: { Authorization: `Bearer ${currentToken}` }
    });
    const bookings = await res.json();
    grid.innerHTML = "";

    if (bookings.length === 0) {
      grid.innerHTML = `<p style="color: var(--text-muted);">You have no active or past bookings yet.</p>`;
      return;
    }

    bookings.forEach(b => {
      let badgeClass = "badge-paid";
      if (b.booking_status === "USED") badgeClass = "badge-used";
      if (b.booking_status === "CANCELLED") badgeClass = "badge-cancelled";

      const card = document.createElement("div");
      card.className = "card";
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <span class="status-badge ${badgeClass}">${b.booking_status}</span>
          <span style="font-family: monospace; font-size: 0.8rem; color: var(--text-muted);">${b.booking_ref}</span>
        </div>
        <h3 style="font-size: 1.15rem; font-weight: 700;">${b.boat ? b.boat.boat_name : 'Boat'}</h3>
        <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;">
          📅 ${b.booking_date} | ⏰ ${b.slot ? b.slot.start_time : ''} | 👥 ${b.passenger_count} Seats
        </p>

        ${b.booking_status === "CONFIRMED" ? `
          <div style="text-align: center; background: #fff; padding: 0.5rem; border-radius: 8px; margin-bottom: 0.75rem;">
            <img src="/api/bookings/${b.id}/qr-image" style="width: 140px; height: 140px;" alt="QR Code">
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <button class="btn btn-outline btn-block" onclick="viewTicketDirect(${b.id})"><i class="fa-solid fa-expand"></i> View Pass</button>
            <button class="btn btn-danger btn-block" onclick="cancelTicket(${b.id})">Cancel</button>
          </div>
        ` : `
          <div style="padding: 0.5rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
            ${b.booking_status === 'USED' ? '✅ Ticket Scanned & Entry Granted' : '❌ Ticket Cancelled & Refunded'}
          </div>
        `}
      `;
      grid.appendChild(card);
    });
  } catch (e) {
    grid.innerHTML = `<p>Error loading tickets.</p>`;
  }
}

async function viewTicketDirect(bookingId) {
  try {
    const res = await fetch(`/api/bookings/${bookingId}`, {
      headers: { Authorization: `Bearer ${currentToken}` }
    });
    const booking = await res.json();
    showDigitalTicket(booking);
  } catch (e) {
    alert("Could not load ticket.");
  }
}

async function cancelTicket(bookingId) {
  if (!confirm("Are you sure you want to cancel this ticket? A refund will be initiated.")) return;

  try {
    const res = await fetch(`/api/bookings/${bookingId}/cancel`, {
      method: "POST",
      headers: { Authorization: `Bearer ${currentToken}` }
    });
    const data = await res.json();
    if (res.ok) {
      alert("Ticket cancelled successfully. Refund initiated.");
      loadMyTickets();
    } else {
      alert(`Cancellation failed: ${data.detail}`);
    }
  } catch (e) {
    alert("Error cancelling ticket.");
  }
}

function switchTab(tab) {
  document.getElementById("tab-fleet").style.display = tab === "fleet" ? "block" : "none";
  document.getElementById("tab-tickets").style.display = tab === "tickets" ? "block" : "none";

  if (tab === "tickets") {
    loadMyTickets();
  }
}

function openModal(id) {
  document.getElementById(id).classList.add("active");
}

function closeModal(id) {
  document.getElementById(id).classList.remove("active");
}
