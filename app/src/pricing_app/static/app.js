async function loadCatalogue() {
  const resp = await fetch("/api/catalogue");
  const data = await resp.json();

  const materiauSelect = document.getElementById("materiau");
  const profileSelect = document.getElementById("profile");

  for (const nom of data.materiaux) {
    const option = document.createElement("option");
    option.value = nom;
    option.textContent = nom;
    materiauSelect.appendChild(option);
  }

  for (const nom of data.profiles) {
    const option = document.createElement("option");
    option.value = nom;
    option.textContent = nom;
    profileSelect.appendChild(option);
  }
}

function showResult(html, isError) {
  const result = document.getElementById("result");
  result.classList.remove("hidden");
  result.classList.toggle("error", Boolean(isError));
  result.innerHTML = html;
}

async function handleSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const payload = {
    largeur_mm: Number(form.largeur_mm.value),
    hauteur_mm: Number(form.hauteur_mm.value),
    materiau: form.materiau.value,
    profile: form.profile.value,
    code_spp: form.code_spp.value,
    complexity_factor: Number(form.complexity_factor.value),
    logistics_cost: Number(form.logistics_cost.value),
  };

  const resp = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await resp.json();

  if (!resp.ok) {
    const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    showResult(`<strong>Erreur ${resp.status}</strong> — ${detail}`, true);
    return;
  }

  showResult(
    `<strong>Prix predit : ${data.prix_predit} EUR</strong>` +
      `<br>Modele : ${data.nom_modele} (version ${data.version})` +
      `<br>Latence : ${data.latence_ms} ms`,
    false
  );
}

document.getElementById("predict-form").addEventListener("submit", handleSubmit);
loadCatalogue();
