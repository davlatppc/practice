const PAGE_SIZE = 10;
const $ = (id) => document.getElementById(id);

let groups = [];
let editingId = null;
let offset = 0;

function fail(err, box = $("error")) {
  if (err.status === 401) {
    location.href = "/login.html";
    return;
  }
  showError(box, err.message);
}

async function start() {
  try {
    const me = await api("/api/auth/me");
    $("username").textContent = me.username;
  } catch (err) {
    location.href = "/login.html";
    return;
  }
  $("app").hidden = false;
  await loadGroups();
  await loadContacts(true);
}

$("logout").addEventListener("click", async () => {
  await api("/api/auth/logout", "POST");
  location.href = "/login.html";
});

function fillSelect(select, firstText) {
  const value = select.value;
  select.replaceChildren(new Option(firstText, ""));
  for (const g of groups) select.append(new Option(g.name, g.id));
  select.value = value;
  if (select.selectedIndex < 0) select.selectedIndex = 0;
}

async function loadGroups() {
  try {
    groups = await api("/api/groups");
  } catch (err) {
    fail(err);
    return;
  }
  const box = $("groups");
  box.replaceChildren();
  if (groups.length === 0) box.textContent = "Групп пока нет";
  for (const g of groups) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = g.name + " (" + g.contacts_count + ")";
    const button = document.createElement("button");
    button.textContent = "×";
    button.addEventListener("click", () => deleteGroup(g));
    chip.append(button);
    box.append(chip);
  }
  fillSelect($("filter-group"), "Все группы");
  fillSelect($("group_id"), "Без группы");
}

$("group-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError($("error"), "");
  try {
    await api("/api/groups", "POST", { name: $("group-name").value.trim() });
    $("group-name").value = "";
    await loadGroups();
  } catch (err) {
    fail(err);
  }
});

async function deleteGroup(group) {
  if (!confirm("Удалить группу " + group.name + "?")) return;
  try {
    await api("/api/groups/" + group.id, "DELETE");
    await loadGroups();
    await loadContacts(true);
  } catch (err) {
    fail(err);
  }
}

function contactItem(c) {
  const li = document.createElement("li");

  const text = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = (c.is_favorite ? "★ " : "") + c.name;
  const group = groups.find((g) => g.id === c.group_id);
  const info = document.createElement("div");
  info.className = "info";
  info.textContent = [c.phone, c.email, c.birthday && "ДР: " + c.birthday, group && group.name]
    .filter(Boolean)
    .join(" · ");
  text.append(title, info);

  const buttons = document.createElement("div");
  const edit = document.createElement("button");
  edit.textContent = "Изменить";
  edit.addEventListener("click", () => startEdit(c));
  const del = document.createElement("button");
  del.className = "red";
  del.textContent = "Удалить";
  del.addEventListener("click", () => deleteContact(c));
  buttons.append(edit, " ", del);

  li.append(text, buttons);
  return li;
}

async function loadContacts(reset) {
  if (reset) {
    offset = 0;
    $("contacts").replaceChildren();
  }
  showError($("error"), "");
  $("more").hidden = true;
  $("status").textContent = "Загрузка...";

  const params = new URLSearchParams({ sort: $("sort").value, limit: PAGE_SIZE, offset: offset });
  if ($("q").value.trim()) params.set("q", $("q").value.trim());
  if ($("filter-group").value) params.set("group_id", $("filter-group").value);
  if ($("filter-birthday").checked) params.set("birthday_this_month", "true");

  try {
    const items = await api("/api/contacts?" + params);
    for (const c of items) $("contacts").append(contactItem(c));
    offset += items.length;
    $("more").hidden = items.length < PAGE_SIZE;
    $("status").textContent = offset === 0 ? "Контактов нет" : "";
  } catch (err) {
    $("status").textContent = "";
    fail(err);
  }
}

$("more").addEventListener("click", () => loadContacts(false));
$("filters").addEventListener("submit", (event) => {
  event.preventDefault();
  loadContacts(true);
});
for (const id of ["filter-group", "sort", "filter-birthday"]) {
  $(id).addEventListener("change", () => loadContacts(true));
}

function resetForm() {
  editingId = null;
  $("contact-form").reset();
  $("form-title").textContent = "Новый контакт";
  $("cancel").hidden = true;
  showError($("form-error"), "");
}

function startEdit(c) {
  editingId = c.id;
  $("name").value = c.name;
  $("phone").value = c.phone;
  $("email").value = c.email || "";
  $("birthday").value = c.birthday || "";
  $("group_id").value = c.group_id || "";
  $("is_favorite").checked = c.is_favorite;
  $("form-title").textContent = "Изменение контакта";
  $("cancel").hidden = false;
  showError($("form-error"), "");
  $("contact-form").scrollIntoView();
}

$("cancel").addEventListener("click", resetForm);

$("contact-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  showError($("form-error"), "");
  const body = {
    name: $("name").value.trim(),
    phone: $("phone").value.trim(),
    email: $("email").value.trim() || null,
    birthday: $("birthday").value || null,
    group_id: $("group_id").value ? Number($("group_id").value) : null,
    is_favorite: $("is_favorite").checked,
  };
  try {
    if (editingId) {
      await api("/api/contacts/" + editingId, "PATCH", body);
    } else {
      await api("/api/contacts", "POST", body);
    }
    resetForm();
    await loadGroups();
    await loadContacts(true);
  } catch (err) {
    fail(err, $("form-error"));
  }
});

async function deleteContact(c) {
  if (!confirm("Удалить контакт " + c.name + "?")) return;
  try {
    await api("/api/contacts/" + c.id, "DELETE");
    if (editingId === c.id) resetForm();
    await loadGroups();
    await loadContacts(true);
  } catch (err) {
    fail(err);
  }
}

start();
