async function api(url, method = "GET", body = null) {
  const options = { method: method, headers: { "Content-Type": "application/json" } };
  if (body) options.body = JSON.stringify(body);
  const response = await fetch(url, options);
  if (response.status === 204) return null;
  const data = await response.json().catch(() => ({ detail: "Ошибка сервера" }));
  if (!response.ok) {
    const error = new Error(errorText(data));
    error.status = response.status;
    throw error;
  }
  return data;
}

const FIELDS = {
  username: "Логин",
  password: "Пароль",
  name: "Название",
  phone: "Телефон",
  email: "E-mail",
  birthday: "День рождения",
  group_id: "Группа",
};

function errorText(data) {
  if (typeof data.detail === "string") return data.detail;
  return data.detail
    .map((d) => {
      const field = d.loc[d.loc.length - 1];
      let text = "некорректное значение";
      if (d.type === "missing") text = "обязательное поле";
      if (d.type === "string_too_short") text = "минимум символов: " + d.ctx.min_length;
      if (d.type === "string_too_long") text = "максимум символов: " + d.ctx.max_length;
       if (d.type === "value_error") text = d.msg.replace("Value error, ", "");
      return (FIELDS[field] || field) + ": " + text;
    })
    .join("; ");
}

function showError(box, text) {
  box.textContent = text;
  box.hidden = !text;
}
