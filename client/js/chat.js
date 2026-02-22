const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

let socket = null;
let currentUsername = null;

// ===== token =====

function getToken() {
    return localStorage.getItem("access_token");
}

function removeToken() {
    localStorage.removeItem("access_token");
}

function checkAuth() {
    if (!getToken()) {
        window.location.href = "index.html";
        return false;
    }
    return true;
}

function getUsernameFromToken() {
    try {
        const payload = getToken().split(".")[1];
        return JSON.parse(atob(payload)).sub;
    } catch (e) {
        return null;
    }
}

// ===== ui helpers =====

function updateConnectionStatus(isConnected) {
    const el = document.getElementById("connection-status");
    if (isConnected) {
        el.textContent = "● Connected";
        el.className = "status-connected";
        document.getElementById("message-input").disabled = false;
        document.getElementById("send-btn").disabled = false;
    } else {
        el.textContent = "● Disconnected";
        el.className = "status-disconnected";
        document.getElementById("message-input").disabled = true;
        document.getElementById("send-btn").disabled = true;
    }
}

function updateOnlineUsers(users) {
    const list = document.getElementById("online-users-list");
    list.innerHTML = "";
    users.forEach((username) => {
        const li = document.createElement("li");
        li.textContent = username === currentUsername
            ? `${username} (You)`
            : username;
        list.appendChild(li);
    });
}

function scrollToBottom() {
    const container = document.getElementById("messages-container");
    container.scrollTop = container.scrollHeight;
}

// ===== render message =====

function renderMessage(data) {
    const container = document.getElementById("messages-container");
    
    const placeholder = container.querySelector(".messages-placeholder");
    if (placeholder) placeholder.remove();

    if (data.type === "system") {
        const div = document.createElement("div");
        div.className = "system-message";
        div.textContent = data.message;
        container.appendChild(div);

    } else if (data.type === "message") {
        const isOwn = data.username === currentUsername;

        const bubble = document.createElement("div");
        bubble.className = `message-bubble ${isOwn ? "own" : "other"}`;

        // Meta: sender + timestamp
        const meta = document.createElement("div");
        meta.className = "message-meta";
        meta.innerHTML = isOwn
            ? `<span>${data.timestamp}</span>`
            : `<span>${data.username}</span><span>${data.timestamp}</span>`;

        // content
        const content = document.createElement("div");
        content.className = "message-content";
        content.textContent = data.message;

        bubble.appendChild(meta);
        bubble.appendChild(content);
        container.appendChild(bubble);
    }

    scrollToBottom();
}

// ===== ws =====

function connectWebSocket() {
    const token = getToken();
    socket = new WebSocket(`${WS_BASE}/ws/chat?token=${token}`);

    socket.onopen = () => {
        console.log("WebSocket connected.");
        updateConnectionStatus(true);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "online_users") {
            updateOnlineUsers(data.users);
            return;
        }

        renderMessage(data);
    };

    socket.onclose = (event) => {
        updateConnectionStatus(false);
        if (event.code === 1008) {
            logout();
            return;
        }
        if (event.code !== 1000) {
            setTimeout(connectWebSocket, 3000);
        }
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

// ===== send =====

function sendMessage() {
    const input = document.getElementById("message-input");
    const text = input.value.trim();

    if (!text || !socket || socket.readyState !== WebSocket.OPEN) return;

    socket.send(JSON.stringify({ message: text }));
    input.value = ""; 
    input.focus();
}

// ===== event listeners =====

document.getElementById("send-btn").addEventListener("click", sendMessage);

// send by enter
document.getElementById("message-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.getElementById("logout-btn").addEventListener("click", logout);

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
            console.error("Logout request failed:", e);
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

    document.getElementById("current-user").textContent = currentUsername;

    connectWebSocket();
}

init();