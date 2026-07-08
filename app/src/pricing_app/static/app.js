// --- Combobox (materiau / profile) ---------------------------------------

function initCombobox(root) {
  const trigger = root.querySelector(".combobox-trigger");
  const valueLabel = root.querySelector(".combobox-value");
  const panel = root.querySelector(".combobox-panel");
  const search = root.querySelector(".combobox-search");
  const list = root.querySelector(".combobox-list");
  const hiddenInput = root.querySelector('input[type="hidden"]');

  let options = [];

  function renderList(filter) {
    const term = (filter || "").trim().toLowerCase();
    const filtered = options.filter((o) => o.toLowerCase().includes(term));

    list.innerHTML = "";
    if (filtered.length === 0) {
      const empty = document.createElement("li");
      empty.className = "combobox-empty";
      empty.textContent = "Aucun resultat";
      list.appendChild(empty);
      return;
    }

    for (const option of filtered) {
      const item = document.createElement("li");
      item.textContent = option;
      item.setAttribute("role", "option");
      if (option === hiddenInput.value) {
        item.classList.add("selected");
      }
      item.addEventListener("click", () => {
        hiddenInput.value = option;
        valueLabel.textContent = option;
        valueLabel.classList.remove("placeholder");
        close();
        hiddenInput.dispatchEvent(new Event("change", { bubbles: true }));
      });
      list.appendChild(item);
    }
  }

  function open() {
    root.classList.add("open");
    panel.classList.remove("hidden");
    search.value = "";
    renderList("");
    search.focus();
  }

  function close() {
    root.classList.remove("open");
    panel.classList.add("hidden");
  }

  trigger.addEventListener("click", () => {
    if (root.classList.contains("open")) {
      close();
    } else {
      open();
    }
  });

  search.addEventListener("input", () => renderList(search.value));

  document.addEventListener("click", (event) => {
    if (!root.contains(event.target)) {
      close();
    }
  });

  return {
    setOptions(newOptions) {
      options = newOptions;
    },
  };
}

const materiauBox = initCombobox(document.querySelector('.combobox[data-name="materiau"]'));
const profileBox = initCombobox(document.querySelector('.combobox[data-name="profile"]'));

async function loadCatalogue() {
  const resp = await fetch("/api/catalogue");
  const data = await resp.json();
  materiauBox.setOptions(data.materiaux);
  profileBox.setOptions(data.profiles);
}

// --- Predict form ----------------------------------------------------------

function showResult(html, isError) {
  const result = document.getElementById("result");
  result.classList.remove("hidden");
  result.classList.toggle("error", Boolean(isError));
  result.innerHTML = html;
}

async function handleSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const submitBtn = form.querySelector(".submit-btn");
  const payload = {
    largeur_mm: Number(form.largeur_mm.value),
    hauteur_mm: Number(form.hauteur_mm.value),
    materiau: form.materiau.value,
    profile: form.profile.value,
    code_spp: form.code_spp.value,
    complexity_factor: Number(form.complexity_factor.value),
    logistics_cost: Number(form.logistics_cost.value),
  };

  if (!payload.materiau || !payload.profile) {
    showResult("Choisis un materiau et un profile.", true);
    return;
  }

  submitBtn.classList.add("loading");
  submitBtn.disabled = true;

  try {
    const resp = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();

    if (!resp.ok) {
      const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
      showResult(`<strong>Erreur ${resp.status}</strong> : ${detail}`, true);
      return;
    }

    showResult(
      `<div class="price">${data.prix_predit} EUR</div>` +
        `<div>Modele : ${data.nom_modele} (version ${data.version})</div>` +
        `<div>Latence : ${data.latence_ms} ms</div>`,
      false
    );
  } finally {
    submitBtn.classList.remove("loading");
    submitBtn.disabled = false;
  }
}

document.getElementById("predict-form").addEventListener("submit", handleSubmit);
loadCatalogue();
