const API_BASE = window.location.origin.includes("8080") ? "http://127.0.0.1:8080/api/v1" : "/api/v1";

const BOAT_PRICES = {
    "Speed Boat Express": 400,
    "Family Paddle Boat": 250,
    "Tighra Dam Scenic Cruise": 150
};

document.addEventListener("DOMContentLoaded", () => {
    showTab("home");
    checkExistingAuth();
    
    // Set default date picker to today
    const dateInput = document.getElementById("bookDate");
    if (dateInput) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.value = today;
        dateInput.min = today;
    }
    
    updatePriceCalculation();
});

function toggleMobileMenu() {
    const navMenu = document.getElementById("navMenu");
    const navActions = document.getElementById("navActions");
    if (navMenu) navMenu.classList.toggle("mobile-open");
    if (navActions) navActions.classList.toggle("mobile-open");
}

function closeMobileMenu() {
    const navMenu = document.getElementById("navMenu");
    const navActions = document.getElementById("navActions");
    if (navMenu) navMenu.classList.remove("mobile-open");
    if (navActions) navActions.classList.remove("mobile-open");
}

function showTab(tabName) {
    document.querySelectorAll(".tab-content").forEach(tab => {
        tab.classList.remove("active");
    });
    
    document.querySelectorAll(".menu-link").forEach(link => {
        link.classList.remove("active");
    });
    
    hideAlert();
    
    if (tabName === "home") {
        document.getElementById("homeView").classList.add("active");
        const homeLink = document.getElementById("navHomeLink");
        if (homeLink) homeLink.classList.add("active");
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (tabName === "login") {
        document.getElementById("loginView").classList.add("active");
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (tabName === "register") {
        document.getElementById("registerView").classList.add("active");
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } else if (tabName === "dashboard") {
        document.getElementById("dashboardView").classList.add("active");
        window.scrollTo({ top: 0, behavior: 'smooth' });
        fetchMyTickets();
    } else if (tabName === "adminPortal") {
        document.getElementById("adminPortalView").classList.add("active");
        const adminLink = document.getElementById("navAdminLink");
        if (adminLink) adminLink.classList.add("active");
        window.scrollTo({ top: 0, behavior: 'smooth' });
        fetchAdminPortalData();
    }
}

function scrollToSection(sectionId) {
    showTab("home");
    setTimeout(() => {
        const el = document.getElementById(sectionId);
        if (el) {
            el.scrollIntoView({ behavior: 'smooth' });
        }
    }, 100);
}

function selectBoat(boatName) {
    const boatSelect = document.getElementById("bookBoatName");
    if (boatSelect) {
        boatSelect.value = boatName;
        updatePriceCalculation();
    }
    scrollToSection('searchSection');
}

function updatePriceCalculation() {
    const boatName = document.getElementById("bookBoatName").value;
    const passengers = parseInt(document.getElementById("bookPassengers").value) || 1;
    const pricePerSeat = BOAT_PRICES[boatName] || 300;
    const total = pricePerSeat * passengers;

    const calcEl = document.getElementById("calcTotalAmount");
    if (calcEl) {
        calcEl.textContent = `₹${total}.00`;
    }
}

async function handleBookingSubmit(event) {
    event.preventDefault();
    hideAlert();

    const token = localStorage.getItem("access_token");
    if (!token) {
        showAlert("Please log in or register your account first to complete ticket booking & payment.", "error");
        showTab("login");
        return;
    }

    const boatName = document.getElementById("bookBoatName").value;
    const bookingDate = document.getElementById("bookDate").value;
    const timeSlot = document.getElementById("bookTimeSlot").value;
    const passengers = parseInt(document.getElementById("bookPassengers").value);
    
    const selectedPayRadio = document.querySelector('input[name="payMethod"]:checked');
    const paymentMethod = selectedPayRadio ? selectedPayRadio.value : "Razorpay (UPI / Cards)";

    const submitBtn = document.getElementById("paySubmitBtn");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Processing Secure Payment...`;

    try {
        const response = await fetch(`${API_BASE}/bookings/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                boat_name: boatName,
                booking_date: bookingDate,
                time_slot: timeSlot,
                passengers: passengers,
                payment_method: paymentMethod
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Booking failed. Please try again.");
        }

        renderTicketModal(data);

    } catch (err) {
        showAlert(err.message, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<i class="fa-solid fa-lock"></i> Pay Now & Generate Valid QR Ticket`;
    }
}

function renderTicketModal(ticket) {
    document.getElementById("modalTicketNum").textContent = ticket.ticket_number;
    document.getElementById("modalQRImage").src = ticket.qr_code_base64;
    document.getElementById("modalBoatName").textContent = ticket.boat_name;
    document.getElementById("modalDate").textContent = ticket.booking_date;
    document.getElementById("modalSlot").textContent = ticket.time_slot;
    document.getElementById("modalPassengers").textContent = `${ticket.passengers} Passenger(s)`;
    document.getElementById("modalAmount").textContent = `₹${ticket.total_amount}.00 (${ticket.payment_status})`;

    document.getElementById("ticketModal").classList.remove("hidden");
}

function closeTicketModal() {
    document.getElementById("ticketModal").classList.add("hidden");
}

async function fetchMyTickets() {
    const token = localStorage.getItem("access_token");
    const container = document.getElementById("ticketsListContainer");
    if (!token || !container) return;

    try {
        const response = await fetch(`${API_BASE}/bookings/my-tickets`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.ok) {
            const tickets = await response.json();
            if (tickets.length === 0) {
                container.innerHTML = `<p class="empty-msg">No booked tickets found. Book your first boat ride on the Home screen!</p>`;
                return;
            }

            container.innerHTML = tickets.map(t => `
                <div class="ticket-card-item">
                    <img src="${t.qr_code_base64}" alt="QR Ticket" class="ticket-qr-preview">
                    <div class="ticket-info">
                        <h4>${t.boat_name} — Pass #${t.ticket_number}</h4>
                        <p><strong>Date:</strong> ${t.booking_date} | <strong>Slot:</strong> ${t.time_slot}</p>
                        <p><strong>Passengers:</strong> ${t.passengers} Person(s) | <strong>Paid:</strong> ₹${t.total_amount}.00</p>
                        <p><strong>Status:</strong> <span class="badge-active">${t.booking_status}</span></p>
                    </div>
                </div>
            `).join("");
        }
    } catch {
        container.innerHTML = `<p class="empty-msg">Error loading tickets.</p>`;
    }
}

/* ADMIN PORTAL FUNCTIONS */
async function fetchAdminPortalData() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
        // Fetch Admin Stats
        const statsRes = await fetch(`${API_BASE}/admin/stats`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (statsRes.ok) {
            const stats = await statsRes.json();
            document.getElementById("statRevenue").textContent = `₹${stats.total_revenue}`;
            document.getElementById("statBookings").textContent = stats.total_bookings;
            document.getElementById("statUsers").textContent = stats.total_users;
            document.getElementById("statBoats").textContent = stats.total_boats;
        }

        // Fetch System Bookings
        const bookingsRes = await fetch(`${API_BASE}/admin/bookings`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (bookingsRes.ok) {
            const bookings = await bookingsRes.json();
            const tableBody = document.getElementById("adminBookingsTable");
            
            if (bookings.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="8" class="text-center">No system bookings recorded yet.</td></tr>`;
                return;
            }

            tableBody.innerHTML = bookings.map(b => `
                <tr>
                    <td><strong>${b.ticket_number}</strong></td>
                    <td>${b.boat_name}</td>
                    <td>${b.booking_date}</td>
                    <td>${b.time_slot}</td>
                    <td>${b.passengers}</td>
                    <td>₹${b.total_amount}.00</td>
                    <td><span class="badge-active">${b.booking_status}</span></td>
                    <td>
                        <button class="btn btn-outline-dark btn-sm" onclick="adminVerifyTicket('${b.ticket_number}')">
                            <i class="fa-solid fa-check"></i> Mark Used
                        </button>
                    </td>
                </tr>
            `).join("");
        }
    } catch (err) {
        showAlert("Failed to load admin portal data.", "error");
    }
}

async function adminVerifyTicket(ticketNum) {
    const token = localStorage.getItem("access_token");
    try {
        const res = await fetch(`${API_BASE}/bookings/verify-qr`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ticket_number: ticketNum })
        });
        const data = await res.json();
        showAlert(data.message, data.status === "VERIFIED" ? "success" : "error");
        fetchAdminPortalData();
    } catch {
        showAlert("Error updating ticket status.", "error");
    }
}

async function handleVerifyQR(event) {
    event.preventDefault();
    const ticketNum = document.getElementById("verifyTicketNum").value.trim();
    const resultBox = document.getElementById("verifyResult");

    try {
        const response = await fetch(`${API_BASE}/bookings/verify-qr`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ticket_number: ticketNum })
        });

        const data = await response.json();
        resultBox.textContent = data.message;
        resultBox.className = `verify-result-box ${data.status}`;
        resultBox.classList.remove("hidden");
    } catch (err) {
        resultBox.textContent = "System verification error.";
        resultBox.className = "verify-result-box REJECTED";
        resultBox.classList.remove("hidden");
    }
}

function showAlert(message, type = "error") {
    const alertBox = document.getElementById("alertBox");
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.className = `alert-box ${type}`;
    alertBox.classList.remove("hidden");
}

function hideAlert() {
    const alertBox = document.getElementById("alertBox");
    if (alertBox) alertBox.classList.add("hidden");
}

function fillDemo(email, password) {
    document.getElementById("loginEmail").value = email;
    document.getElementById("loginPassword").value = password;
    hideAlert();
}

async function handleLogin(event) {
    event.preventDefault();
    hideAlert();
    
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value;
    const submitBtn = document.getElementById("loginSubmitBtn");
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Logging in...`;

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Authentication failed. Please check your credentials.");
        }

        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user_info", JSON.stringify(data.user));

        showAlert("Login successful! Welcome back.", "success");
        setTimeout(() => {
            renderDashboard(data.user);
            if (data.user.role === "admin") {
                showTab("adminPortal");
            } else {
                showTab("dashboard");
            }
        }, 500);

    } catch (err) {
        showAlert(err.message, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>Login to Account</span> <i class="fa-solid fa-arrow-right"></i>`;
    }
}

async function handleRegister(event) {
    event.preventDefault();
    hideAlert();

    const fullName = document.getElementById("regFullName").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const phone = document.getElementById("regPhone").value.trim();
    const password = document.getElementById("regPassword").value;
    const submitBtn = document.getElementById("regSubmitBtn");

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...`;

    try {
        const response = await fetch(`${API_BASE}/auth/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name: fullName,
                email: email,
                phone: phone,
                password: password,
                role: "tourist"
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Registration failed.");
        }

        showAlert("Account created successfully! Please log in with your credentials.", "success");
        setTimeout(() => {
            fillDemo(email, password);
            showTab("login");
        }, 1200);

    } catch (err) {
        showAlert(err.message, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>Create Account</span> <i class="fa-solid fa-check"></i>`;
    }
}

async function checkExistingAuth() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.ok) {
            const user = await response.json();
            renderDashboard(user);
        } else {
            handleLogoutSilently();
        }
    } catch {
        // keep current view
    }
}

function renderDashboard(user) {
    document.getElementById("navLoginBtn").classList.add("hidden");
    document.getElementById("navRegisterBtn").classList.add("hidden");
    
    const userBadge = document.getElementById("userBadge");
    userBadge.classList.remove("hidden");
    document.getElementById("badgeUserName").textContent = user.full_name;

    document.getElementById("dashName").textContent = user.full_name;
    document.getElementById("dashEmail").textContent = user.email;
    document.getElementById("dashRole").textContent = user.role.toUpperCase();
    document.getElementById("dashAvatar").textContent = user.full_name.charAt(0).toUpperCase();

    const adminLink = document.getElementById("navAdminLink");
    if (user.role === "admin") {
        if (adminLink) adminLink.classList.remove("hidden");
    } else {
        if (adminLink) adminLink.classList.add("hidden");
    }
}

function handleLogoutSilently() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_info");
    document.getElementById("userBadge").classList.add("hidden");
    document.getElementById("navLoginBtn").classList.remove("hidden");
    document.getElementById("navRegisterBtn").classList.remove("hidden");
    const adminLink = document.getElementById("navAdminLink");
    if (adminLink) adminLink.classList.add("hidden");
}

function handleLogout() {
    handleLogoutSilently();
    showAlert("Logged out successfully.", "success");
    showTab("home");
}
