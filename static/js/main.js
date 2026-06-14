(() => {
  const $ = (id) => document.getElementById(id);

  // Elements
  const fileInput    = $("fileInput");
  const dropZone     = $("dropZone");
  const previewBox   = $("previewBox");
  const previewImg   = $("previewImg");
  const previewName  = $("previewName");
  const removeBtn    = $("removeBtn");
  const analyseBtn   = $("analyseBtn");
  const btnText      = $("btnText");
  const btnIcon      = $("btnIcon");

  const uploadSection = $("uploadSection");
  const loadingSection = $("loadingSection");
  const resultSection  = $("resultSection");
  const errorSection   = $("errorSection");

  let selectedFile = null;

  // ── File selection ──────────────────────────────────────────────────────
  fileInput.addEventListener("change", () => handleFile(fileInput.files[0]));

  function handleFile(file) {
    if (!file || !file.type.startsWith("image/")) return;
    selectedFile = file;
    const url = URL.createObjectURL(file);
    previewImg.src = url;
    previewName.textContent = `${file.name}  (${(file.size / 1024).toFixed(1)} KB)`;
    previewBox.classList.remove("hidden");
    analyseBtn.disabled = false;
  }

  removeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    selectedFile = null;
    fileInput.value = "";
    previewBox.classList.add("hidden");
    analyseBtn.disabled = true;
  });

  // ── Drag & Drop ─────────────────────────────────────────────────────────
  ["dragenter", "dragover"].forEach((ev) =>
    dropZone.addEventListener(ev, (e) => { e.preventDefault(); dropZone.classList.add("drop-zone-active"); })
  );
  ["dragleave", "drop"].forEach((ev) =>
    dropZone.addEventListener(ev, (e) => { e.preventDefault(); dropZone.classList.remove("drop-zone-active"); })
  );
  dropZone.addEventListener("drop", (e) => handleFile(e.dataTransfer.files[0]));

  // ── Analyse ─────────────────────────────────────────────────────────────
  analyseBtn.addEventListener("click", async () => {
    if (!selectedFile) return;
    showLoading();

    const form = new FormData();
    form.append("file", selectedFile);

    try {
      const res = await fetch("/predict", { method: "POST", body: form });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Gagal memproses gambar.");
      showResult(data);
    } catch (err) {
      showError(err.message);
    }
  });

  // ── Reset ────────────────────────────────────────────────────────────────
  [$("resetBtn"), $("errorResetBtn")].forEach((btn) =>
    btn.addEventListener("click", resetAll)
  );

  function resetAll() {
    selectedFile = null;
    fileInput.value = "";
    previewImg.src = "";
    previewBox.classList.add("hidden");
    analyseBtn.disabled = true;
    show("uploadSection");
  }

  // ── UI State helpers ─────────────────────────────────────────────────────
  const SECTIONS = ["uploadSection", "loadingSection", "resultSection", "errorSection"];

  function show(id) {
    SECTIONS.forEach((s) => $(s).classList.toggle("hidden", s !== id));
  }

  function showLoading() { show("loadingSection"); }

  function showError(msg) {
    $("errorMsg").textContent = msg;
    show("errorSection");
  }

  function showResult(data) {
    const isLangka = data.status === "Langka";

    // Image
    $("resultImg").src = data.image_url;

    // Status badge
    $("statusIcon").textContent = isLangka ? "🔴" : "🟢";
    const statusText = $("statusText");
    statusText.textContent = isLangka ? "Hewan Langka / Terancam Punah" : "Populasi Normal";
    statusText.className = `text-base font-bold px-4 py-1.5 rounded-full ${
      isLangka
        ? "bg-danger-100/10 text-danger-400 ring-1 ring-danger-500/30"
        : "bg-forest-100/10 text-forest-400 ring-1 ring-forest-500/30"
    }`;

    // Animal label
    $("animalLabel").textContent = data.label;

    // Confidence bar
    $("confidencePct").textContent = `${data.confidence}%`;
    const bar = $("confidenceBar");
    const barColor = data.confidence >= 80
      ? "bg-forest-500"
      : data.confidence >= 50
        ? "bg-yellow-500"
        : "bg-danger-500";
    bar.className = `h-full rounded-full bar-fill ${barColor}`;
    // Animate after paint
    requestAnimationFrame(() => {
      requestAnimationFrame(() => { bar.style.width = `${data.confidence}%`; });
    });

    show("resultSection");
  }
})();
