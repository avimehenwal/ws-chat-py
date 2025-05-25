let ws = null;

const connectButton = document.getElementById("connectButton");
const disconnectButton = document.getElementById("disconnectButton");
const messageInput = document.getElementById("messageText");
const sendMessageButton = document.getElementById("sendMessageButton");
const messagesList = document.getElementById("messages");

function updateUIState(isConnected) {
  if (isConnected) {
    connectButton.disabled = true;
    disconnectButton.disabled = false;
    messageInput.disabled = false;
    sendMessageButton.disabled = false;
    messageInput.focus();
  } else {
    connectButton.disabled = false;
    disconnectButton.disabled = true;
    messageInput.disabled = true;
    sendMessageButton.disabled = true;
  }
}

updateUIState(false);

function connectWebSocket() {
  if (
    ws &&
    (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)
  ) {
    appendMessage("WebSocket is already connected or connecting.");
    return;
  }

  const ws_protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws_host = window.location.host;
  ws = new WebSocket(`${ws_protocol}//${ws_host}/chat/ws`);

  ws.onopen = function (event) {
    console.log("WebSocket connection opened:", event);
    appendMessage("Connected to WebSocket server.");
    updateUIState(true);
  };

  ws.onmessage = function (event) {
    console.log("Message received:", event.data);
    appendMessage(event.data);
  };

  ws.onclose = function (event) {
    console.log("WebSocket connection closed:", event);
    appendMessage("Disconnected from WebSocket server.");
    updateUIState(false);
    ws = null;
  };

  ws.onerror = function (event) {
    console.error("WebSocket error:", event);
    appendMessage("WebSocket error occurred.");
    updateUIState(false);
    ws = null;
  };
}

function disconnectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  } else {
    appendMessage("WebSocket is not connected.");
  }
}

function sendMessage(event) {
  const message = messageInput.value;
  if (message.trim() !== "" && ws && ws.readyState === WebSocket.OPEN) {
    ws.send(message);
    messageInput.value = "";
  } else if (!ws || ws.readyState !== WebSocket.OPEN) {
    appendMessage("Not connected to WebSocket server. Please connect first.");
  }
  event.preventDefault();
}

function appendMessage(message) {
  const listItem = document.createElement("li");
  listItem.textContent = message;
  messagesList.appendChild(listItem);
  messagesList.scrollTop = messagesList.scrollHeight;
}

messageInput.addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    sendMessage(event);
  }
});
