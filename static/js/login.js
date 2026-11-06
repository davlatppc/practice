const errorBox = document.getElementById("error");

document.getElementById("form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError(errorBox, "");
  try {
    await api("/api/auth/login", "POST", {
      username: document.getElementById("username").value.trim(),
      password: document.getElementById("password").value,
    });
    location.href = "/";
  } catch (err) {
    showError(errorBox, err.message);
  }
});
