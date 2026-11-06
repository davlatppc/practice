const errorBox = document.getElementById("error");

document.getElementById("form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError(errorBox, "");
  const password = document.getElementById("password").value;
  if (password !== document.getElementById("password2").value) {
    showError(errorBox, "Пароли не совпадают");
    return;
  }
  try {
    await api("/api/auth/register", "POST", {
      username: document.getElementById("username").value.trim(),
      password: password,
    });
    location.href = "/";
  } catch (err) {
    showError(errorBox, err.message);
  }
});
