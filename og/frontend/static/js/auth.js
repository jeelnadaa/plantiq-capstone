// Auth Module
function initAuth() {
  const tabLogin = document.getElementById("tab-btn-login");
  const tabRegister = document.getElementById("tab-btn-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

  if (tabLogin && tabRegister) {
    tabLogin.onclick = () => {
      tabLogin.classList.add("active");
      tabRegister.classList.remove("active");
      formLogin.classList.remove("hidden");
      formRegister.classList.add("hidden");
    };

    tabRegister.onclick = () => {
      tabRegister.classList.add("active");
      tabLogin.classList.remove("active");
      formRegister.classList.remove("hidden");
      formLogin.classList.add("hidden");
    };
  }

  if (formLogin) {
    formLogin.onsubmit = async (e) => {
      e.preventDefault();
      const u = document.getElementById("login-username").value;
      const p = document.getElementById("login-password").value;
      try {
        const res = await apiRequest("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: u, password: p })
        });
        if (res.ok) {
          const data = await res.json();
          setAuthToken(data.access_token);
          window.location.href = "/";
        } else {
          alert("Invalid username or password.");
        }
      } catch (err) {
        alert("Login failed. Check server connection.");
      }
    };
  }

  if (formRegister) {
    formRegister.onsubmit = async (e) => {
      e.preventDefault();
      const payload = {
        username: document.getElementById("reg-username").value,
        email: document.getElementById("reg-email").value,
        full_name: document.getElementById("reg-fullname").value,
        password: document.getElementById("reg-password").value
      };
      try {
        const res = await apiRequest("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          const data = await res.json();
          setAuthToken(data.access_token);
          window.location.href = "/";
        } else {
          alert("Registration failed. Username or email may already be taken.");
        }
      } catch (err) {
        alert("Registration failed. Check server connection.");
      }
    };
  }
}

document.addEventListener("DOMContentLoaded", () => initAuth());
