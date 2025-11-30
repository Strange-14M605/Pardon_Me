const input = document.getElementById("input");
const messages = document.getElementById("messages");
const sessionId = "user-session-001"; // default for now- future scope would be to generate unique session IDs per user

document.getElementById("send").onclick = async () => {
    const text = input.value.trim();
    if (!text) return;

    messages.innerHTML += `<div class="user"><b>You:</b> ${text}</div>`;  // User message
    input.value = ""; // reset input field

    const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, session_id: sessionId })   // we pass the input test (as message) and session ID
    });

    const data = await response.json();
    messages.innerHTML += `<div class="bot"><b>Pardon Me:</b> ${data.response}</div>`;  // Agent response
    messages.scrollTop = messages.scrollHeight;
};
