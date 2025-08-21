(function () {
  if (!window.CHAT || !window.CHAT.conversationId) {
    console.error("CHAT.conversationId not found");
    return;
  }

  const convId = window.CHAT.conversationId;
  const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
  const socket = new WebSocket(
    `${wsScheme}://${window.location.host}/ws/chat/${convId}/`
  );

  const messagesEl = document.getElementById("messages");
  const form = document.getElementById("sendForm");
  const input = document.getElementById("messageInput");

  // escape user text
  function escapeHtml(unsafe) {
    return unsafe.replace(/[&<>"']/g, (m) => {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      }[m];
    });
  }

  // render a message
  function render(m) {
    const me =
      document
        .querySelector(".navbar .text-secondary")
        ?.textContent?.replace("Hi, ", "")
        .trim() || "";

    const mine = m.sender === me;
    const div = document.createElement("div");
    div.className = "msg " + (mine ? "me" : "other");

    div.innerHTML =
      `<div class="meta"><strong>${escapeHtml(m.sender)}</strong> · ${m.timestamp}</div>` +
      `<div>${escapeHtml(m.text)}</div>`;

    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // load history
  fetch(`/api/history/${convId}/`)
    .then((r) => r.json())
    .then((d) => d.messages.forEach(render))
    .catch((err) => console.error("History load failed", err));

  // receive new messages
  socket.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      render(data);
    } catch (err) {
      console.error("Invalid WS message", err);
    }
  };

  socket.onclose = () => {
    console.warn("WebSocket closed");
  };

  socket.onerror = (err) => {
    console.error("WebSocket error", err);
  };

  // send message
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    socket.send(JSON.stringify({ text }));
    input.value = "";
  });
})();
