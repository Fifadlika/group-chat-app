const API_BASE = "http://localhost:8000";

// == utility ==

function showError(message) {
    const el = document.getElementById("error-message");
    el.textContent = message;
    el.classList.remove("hidden");
}

function hideError() {
    document.getElementById("error-message").classList.add("hidden");
}

function setLoading(buttonId, isLoading) {
    const button = document.getElementById(buttonId);
    button.disabled = isLoading;
    button.textContent = isLoading ? "Please wait..." : button.dataset.label;
}

// == token management ==
function saveToken(token) {
    localStorage.setItem("access_token", token);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function removeToken() {
    localStorage.removeItem("access_token");
}

// == check authentication status ==

function checkAuthStatus() {
    const token = getToken();
    if (token) {
        window.location.href = "chat.html";
    }
}

// == toggle form ==

document.getElementById("show-register").addEventListener("click", (e) => {
    e.preventDefault();
    hideError();
    document.getElementById("login-form").classList.add("hidden");
    document.getElementById("show-login-text").classList.remove("hidden");
    document.getElementById("register-form").classList.remove("hidden");
    document.getElementById("show-register-text").classList.add("hidden");
    document.querySelector(".auth-subtitle").textContent = "Create new account";
});

document.getElementById("show-login").addEventListener("click", (e) => {
    e.preventDefault();
    hideError();
    document.getElementById("register-form").classList.add("hidden");
    document.getElementById("show-login-text").classList.remove("hidden");
    document.getElementById("login-form").classList.remove("hidden");
    document.getElementById("show-register-text").classList.add("hidden");
    document.querySelector(".auth-subtitle").textContent = "Log in to start chatting";
});

// == login flow ==
document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    setLoading("login-btn", true);

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        const response = await fetch(`${API_BASE}/auth/login`, {
            method:"POST",
            body: formData,
        });

        const data = await response.json();

        if(!response.ok) {
            showError(data.detail || "Login failed, please try again");
            return;
        }

        saveToken(data.access_token)

        window.location.href = "chat.html";
    } catch (error) {
        showError("Can't connect to server.");
    } finally {
        setLoading("login-btn", false);
    }
});

// == registration flow == 
document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();
    setLoading("register-btn", true);

    const username = document.getElementById("reg-username").value;
    const password = document.getElementById("reg-password").value;

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Registration failed. Please try again.");
            return;
        }

        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);

        const loginResponse = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            body: formData,
        });

        const loginData = await loginResponse.json();
        saveToken(loginData.access_token);
        window.location.href = "chat.html";

    } catch (error) {
        showError("Can't connect to server.");
    } finally {
        setLoading("register-btn", false);
    }
});

// == initialization ==
document.getElementById("login-btn").dataset.label = "Sign In";
document.getElementById("register-btn").dataset.label = "Sign Up";

checkAuthStatus();
