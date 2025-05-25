let ws = null;
let messageCount = 0;
const MAX_MSG_RECIEVE = 10;

const connectButton = document.getElementById("connectButton");
const disconnectButton = document.getElementById("disconnectButton");
const messagesList = document.getElementById("messages");

function updateUIState(isConnected) {
  if (isConnected) {
    connectButton.disabled = true;
    disconnectButton.disabled = false;
  } else {
    connectButton.disabled = false;
    disconnectButton.disabled = true;
  }
}

updateUIState(false);

function connectWebSocket() {
  if (
    ws &&
    (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)
  ) {
    appendMessage("WebSocket is already connected or connecting.", "system");
    return;
  }

  messageCount = 0;
  messagesList.innerHTML = "";

  const ws_protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const ws_host = window.location.host;
  ws = new WebSocket(`${ws_protocol}//${ws_host}/chat/ws`);

  ws.onopen = function (event) {
    console.log("WebSocket connection opened:", event);
    appendMessage("Connected to WebSocket server.", "system");
    updateUIState(true);
  };

  ws.onmessage = async function (event) {
    messageCount++;
    console.log(
      `Message received (${messageCount}/${MAX_MSG_RECIEVE}):`,
      event.data
    );
    const originalMessage = event.data;
    appendMessage(originalMessage, "received");

    if (messageCount >= MAX_MSG_RECIEVE) {
      appendMessage(
        `Message limit [${MAX_MSG_RECIEVE}] reached. Disconnecting WebSocket.`,
        "system"
      );
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
      return;
    }

    try {
      const response = await fetch("http://localhost:8888/translate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          q: originalMessage,
          source: "en",
          target: "de",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const translatedText = data.translatedText;

      console.log("Translated message:", translatedText);
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(translatedText);
        appendMessage(translatedText, "sent");
        console.log("Translated message sent back to server.");
      } else {
        console.warn(
          "WebSocket not open, cannot send translated message back to server."
        );
        appendMessage(
          "WebSocket not open, translated message not sent.",
          "system"
        );
      }
    } catch (error) {
      console.error("Translation error:", error);
      appendMessage(`Error translating message: ${error.message}`, "system");
    }
  };

  ws.onclose = function (event) {
    console.log("WebSocket connection closed:", event);
    appendMessage("Disconnected from WebSocket server.", "system");
    updateUIState(false);
    ws = null;
  };

  ws.onerror = function (event) {
    console.error("WebSocket error:", event);
    appendMessage("WebSocket error occurred.", "system");
    updateUIState(false);
    ws = null;
  };
}

function disconnectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.close();
  } else {
    appendMessage("WebSocket is not connected.", "system");
  }
}

function appendMessage(message, type) {
  const listItem = document.createElement("li");
  listItem.textContent = message;

  if (type !== "system") {
    listItem.classList.add("message-bubble");
  }

  if (type === "received") {
    listItem.classList.add("received-message");
  } else if (type === "sent") {
    listItem.classList.add("sent-message");
  } else if (type === "system") {
    listItem.classList.add("system-message");
  }

  messagesList.appendChild(listItem);
  messagesList.parentElement.scrollTop =
    messagesList.parentElement.scrollHeight;
}
