const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

function addUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `<div class="bubble"></div>`;
  row.querySelector(".bubble").textContent = text;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addBotMessage(data) {
  const row = document.createElement("div");
  row.className = "msg-row bot";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = data.response;
  row.appendChild(bubble);

  if (data.intent) {
    const meta = document.createElement("div");
    meta.className = "meta";
    meta.textContent = `Intent: ${data.intent} · Confidence: ${data.confidence}`;
    row.appendChild(meta);
  }

  messagesEl.appendChild(row);

  if (data.escalated) {
    const note = document.createElement("div");
    note.className = "escalate-note";
    note.textContent = "⚠ Escalating this conversation to a human agent";
    messagesEl.appendChild(note);
  }

  if (data.interaction_id) {
    const ratingRow = document.createElement("div");
    ratingRow.className = "rating-row";
    for (let i = 1; i <= 5; i++) {
      const star = document.createElement("span");
      star.className = "star";
      star.textContent = "★";
      star.dataset.value = i;
      star.onclick = () => submitRating(data.interaction_id, i, ratingRow);
      ratingRow.appendChild(star);
    }
    messagesEl.appendChild(ratingRow);
  }

  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function submitRating(interactionId, value, ratingRow) {
  [...ratingRow.children].forEach((star, idx) => {
    star.classList.toggle("active", idx < value);
  });
  await fetch("/api/rate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ interaction_id: interactionId, rating: value }),
  });
}

async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text) return;
  addUserMessage(text);
  inputEl.value = "";

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    addBotMessage(data);
  } catch (err) {
    addBotMessage({ response: "Sorry, something went wrong. Please try again." });
  }
}

sendBtn.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});
