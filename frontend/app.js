const API_URL = "/api/generate-session";

const form = document.getElementById("sessionForm");
const generateBtn = document.getElementById("generateBtn");
const statusText = document.getElementById("status");
const resultSection = document.getElementById("result");
const resultTitle = document.getElementById("resultTitle");
const transcript = document.getElementById("transcript");
const audioPlayer = document.getElementById("audioPlayer");
const transcriptToggle = document.getElementById("transcriptToggle");
const createAnother = document.getElementById("createAnother");

let sessionType = "Meditation";

document.querySelectorAll(".type-card").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".type-card").forEach((card) => {
      card.classList.remove("selected");
    });
    button.classList.add("selected");
    sessionType = button.dataset.type;
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  generateBtn.disabled = true;
  generateBtn.querySelector("span").textContent = "Creating your session…";
  statusText.className = "status";
  statusText.textContent = "Gemini is preparing your guide, then Murf AI will create the audio. This may take a little while.";

  const payload = {
    sessionType,
    focus: document.getElementById("focus").value.trim(),
    duration: document.getElementById("duration").value,
    level: document.getElementById("level").value,
    language: document.getElementById("language").value
  };

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || `Request failed (${response.status})`);
    }

    transcript.textContent = data.script;
    resultTitle.textContent = `${data.sessionType} · ${data.duration}`;
    audioPlayer.src = `data:audio/mpeg;base64,${data.audioBase64}`;
    audioPlayer.load();
    resultSection.classList.remove("hidden");
    statusText.textContent = "Your session is ready. Take a comfortable seat and begin when you feel ready.";
    resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    console.error(error);
    statusText.className = "status error";
    statusText.textContent = error.message || "Could not generate the session. Check that the backend is running.";
  } finally {
    generateBtn.disabled = false;
    generateBtn.querySelector("span").textContent = "Generate my session";
  }
});

transcriptToggle.addEventListener("click", () => {
  const isCollapsed = transcript.classList.toggle("collapsed");
  transcriptToggle.textContent = isCollapsed ? "Show transcript +" : "Hide transcript −";
  transcriptToggle.setAttribute("aria-expanded", String(!isCollapsed));
});

createAnother.addEventListener("click", () => {
  resultSection.classList.add("hidden");
  audioPlayer.pause();
  audioPlayer.removeAttribute("src");
  audioPlayer.load();
  document.getElementById("create").scrollIntoView({ behavior: "smooth" });
});
