// Gate Operator QR Scanner Client Logic

let opToken = localStorage.getItem("tighra_op_token") || null;
let opUser = null;
let html5QrCode = null;

document.addEventListener("DOMContentLoaded", () => {
  checkOpAuth();
});

async function checkOpAuth() {
  if (!opToken) {
    showOpLoginPrompt();
    return;
  }
  try {
    const res = await fetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${opToken}` }
    });
    if (res.ok) {
      opUser = await res.json();
      if (opUser.role !== "operator" && opUser.role !== "admin") {
        alert("Access Denied: Requires Gate Operator or Admin role.");
        logoutOperator();
        return;
      }
      showScannerArea();
      loadOperatorSummary();
    } else {
      logoutOperator();
    }
  } catch (e) {
    showOpLoginPrompt();
  }
}

function showOpLoginPrompt() {
  document.getElementById("op-login-prompt").style.display = "block";
  document.getElementById("op-scanner-area").style.display = "none";
  document.getElementById("op-auth-btn").style.display = "block";
  document.getElementById("op-user-profile").style.display = "none";
}

function showScannerArea() {
  document.getElementById("op-login-prompt").style.display = "none";
  document.getElementById("op-scanner-area").style.display = "block";
  document.getElementById("op-auth-btn").style.display = "none";
  document.getElementById("op-user-profile").style.display = "flex";
  document.getElementById("op-name").textContent = `👮 ${opUser.name}`;
}

async function quickLoginOperator() {
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "operator@tighra.gov.in", password: "Operator@123" })
    });
    const data = await res.json();
    if (res.ok) {
      opToken = data.access_token;
      opUser = data.user;
      localStorage.setItem("tighra_op_token", opToken);
      showScannerArea();
      loadOperatorSummary();
    } else {
      alert(`Operator Login Failed: ${data.detail}`);
    }
  } catch (e) {
    alert("Login error");
  }
}

function logoutOperator() {
  opToken = null;
  opUser = null;
  localStorage.removeItem("tighra_op_token");
  stopScanner();
  showOpLoginPrompt();
}

async function loadOperatorSummary() {
  if (!opToken) return;
  try {
    const res = await fetch("/api/verify-qr/summary", {
      headers: { Authorization: `Bearer ${opToken}` }
    });
    if (res.ok) {
      const summary = await res.json();
      document.getElementById("kpi-scanned-count").textContent = summary.total_tickets_scanned;
      document.getElementById("kpi-passengers-count").textContent = summary.total_passengers_boarded;
    }
  } catch (e) {
    console.error("Summary load error", e);
  }
}

function startScanner() {
  if (html5QrCode && html5QrCode.isScanning) {
    return;
  }
  html5QrCode = new Html5Qrcode("reader");
  const config = { fps: 10, qrbox: { width: 250, height: 250 } };

  html5QrCode.start(
    { facingMode: "environment" },
    config,
    onScanSuccess,
    onScanFailure
  ).catch(err => {
    console.log("Camera start error, falling back to manual entry mode.", err);
    alert("Camera access unavailable or blocked. Please use manual QR code entry below.");
  });
}

function stopScanner() {
  if (html5QrCode && html5QrCode.isScanning) {
    html5QrCode.stop().then(() => {
      console.log("Scanner stopped.");
    }).catch(err => console.error(err));
  }
}

function onScanSuccess(decodedText, decodedResult) {
  stopScanner();
  verifyQRCode(decodedText);
}

function onScanFailure(error) {
  // Silent scan failure polling
}

function verifyManualQR() {
  const token = document.getElementById("manual-qr-input").value.trim();
  if (!token) {
    alert("Please enter a QR token or Booking Ref code.");
    return;
  }
  verifyQRCode(token);
}

async function verifyQRCode(token) {
  if (!opToken) {
    alert("Operator authorization missing.");
    return;
  }

  try {
    const res = await fetch("/api/verify-qr", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${opToken}`
      },
      body: JSON.stringify({ qr_token: token })
    });
    const data = await res.json();

    showVerificationResult(data);
    loadOperatorSummary();
    document.getElementById("manual-qr-input").value = "";
  } catch (e) {
    alert("Error verifying QR code.");
  }
}

function showVerificationResult(data) {
  const modalIcon = document.getElementById("result-icon");
  const modalTitle = document.getElementById("result-title");
  const modalMsg = document.getElementById("result-message");
  const modalDetails = document.getElementById("result-details");

  if (data.success) {
    modalIcon.innerHTML = "✅";
    modalTitle.textContent = "BOARDING GRANTED";
    modalTitle.style.color = "#10b981";
    modalMsg.textContent = data.message;

    if (data.booking) {
      modalDetails.style.display = "block";
      modalDetails.innerHTML = `
        <div style="margin-bottom: 0.25rem;">🚢 <strong>Boat:</strong> ${data.booking.boat ? data.booking.boat.boat_name : ''}</div>
        <div style="margin-bottom: 0.25rem;">⏰ <strong>Slot:</strong> ${data.booking.slot ? data.booking.slot.start_time : ''} - ${data.booking.slot ? data.booking.slot.end_time : ''}</div>
        <div style="margin-bottom: 0.25rem;">👥 <strong>Passengers:</strong> ${data.booking.passenger_count} Person(s)</div>
        <div style="margin-bottom: 0.25rem;">👤 <strong>Tourist Name:</strong> ${data.booking.user ? data.booking.user.name : ''} (${data.booking.user ? data.booking.user.phone : ''})</div>
        <div>🎟️ <strong>Booking Ref:</strong> ${data.booking.booking_ref}</div>
      `;
    }
  } else {
    modalIcon.innerHTML = data.message.includes("DUPLICATE") ? "⚠️" : "❌";
    modalTitle.textContent = data.message.includes("DUPLICATE") ? "DUPLICATE TICKET" : "ENTRY REJECTED";
    modalTitle.style.color = data.message.includes("DUPLICATE") ? "#f59e0b" : "#ef4444";
    modalMsg.textContent = data.message;
    modalDetails.style.display = "none";
  }

  openModal("result-modal");
}

function openModal(id) {
  document.getElementById(id).classList.add("active");
}

function closeModal(id) {
  document.getElementById(id).classList.remove("active");
}
