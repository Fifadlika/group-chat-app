const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

// ===== state =====
let socket = null;
let currentUsername = null;

// ===== token management =====

function getToken() {
    return localStorage.getItem("access_token");
}

function removeToken() {
    localStorage.removeItem("access_token");
}

// ===== check for auth via token =====

function checkAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = "index.html";
        return false;
    }
    return true;
}

// ===== decode uname from token =====
// JWT consists of header.payload.signature


function getUsernameFromToken() {
    const token = getToken();
    if (!token) return null;

    try {
        const payload = token.split(".")[1];

        const decoded = JSON.parse(atob(payload));

        return decoded.sub;
    } catch (e) {
        console.error("Gagal decode token:", e);
        return null;
    }
}

// ===== ws connection =====

function connectWebSocket() {
    const token = getToken();

    socket = new WebSocket(`${WS_BASE}/ws/chat?token=${token}`);

    socket.onopen = () => {
        console.log("WebSocket terhubung!");
        updateConnectionStatus(true);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleIncomingMessage(data);
    };

    socket.onclose = (event) => {
        console.log("WebSocket terputus, kode:", event.code);
        updateConnectionStatus(false);

        if (event.code === 1008) {
            logout();
            return;
        }

        if (event.code !== 1000) {
            console.log("Mencoba reconnect dalam 3 detik...");
            setTimeout(connectWebSocket, 3000);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

// ===== message handler =====

function handleIncomingMessage(data) {
    switch (data.type) {
        case "message":
            // implemented later
            console.log(`[${data.timestamp}] ${data.username}: ${data.message}`);
            break;

        case "system":
            // implemented later
            console.log(`[${data.timestamp}] *** ${data.message} ***`);
            break;

        case "online_users":
            // implemented later
            console.log("Online:", data.users);
            break;

        default:
            console.log("Tipe pesan tidak dikenal:", data);
    }
}

// ===== sending message =====

function sendMessage(messageText) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket tidak terhubung");
        return false;
    }

    if (!messageText.trim()) {
        return false;
    }

    socket.send(JSON.stringify({ message: messageText }));
    return true;
}

// ===== conn status update =====
// implemented later

function updateConnectionStatus(isConnected) {
    console.log("Status koneksi:", isConnected ? "Terhubung" : "Terputus");
}

// ===== logout =====

async function logout() {
    const token = getToken();

    if (token) {
        try {
            await fetch(`${API_BASE}/auth/logout`, {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
            });
        } catch (e) {
            console.error("Logout request gagal:", e);
        }
    }

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close(1000);
    }

    removeToken();
    window.location.href = "index.html";
}

// ===== init =====

function init() {
    if (!checkAuth()) return;

    currentUsername = getUsernameFromToken();
    if (!currentUsername) {
        logout();
        return;
    }

    console.log("Login sebagai:", currentUsername);
    connectWebSocket();
}

init();