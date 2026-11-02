const form = document.getElementById("chatForm");
const textarea = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const newChatButton = document.getElementById("newChatButton");
const chatBox = document.getElementById("chatBox");
const welcome = document.getElementById("welcome");

const REQUEST_TIMEOUT_MS = 60_000;

function scrollToLatestMessage() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function resizeTextarea() {
    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 180)}px`;
}

function addMessage(content, kind) {
    const message = document.createElement("div");
    message.className = `message ${kind}-message`;
    // textContent intentionally prevents model or user text from becoming HTML.
    message.textContent = content;
    chatBox.appendChild(message);
    scrollToLatestMessage();
    return message;
}

function setSending(isSending) {
    sendButton.disabled = isSending;
    textarea.disabled = isSending;
    chatBox.setAttribute("aria-busy", String(isSending));
}

async function requestReply(message) {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
            signal: controller.signal,
        });
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || `Server error (${response.status})`);
        }
        if (typeof data.response !== "string" || !data.response.trim()) {
            throw new Error("The AI returned an empty response.");
        }

        return data.response;
    } finally {
        window.clearTimeout(timeoutId);
    }
}

textarea.addEventListener("input", resizeTextarea);

textarea.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
    }
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (sendButton.disabled) return;

    const message = textarea.value.trim();
    if (!message) return;

    welcome.hidden = true;
    addMessage(message, "user");
    textarea.value = "";
    resizeTextarea();

    const aiMessage = addMessage("Thinking…", "ai");
    setSending(true);

    try {
        aiMessage.textContent = await requestReply(message);
    } catch (error) {
        console.error("Chat request failed:", error);
        const detail = error.name === "AbortError"
            ? "The request took too long. Please try again."
            : error.message;
        aiMessage.textContent = `Unable to get a reply: ${detail}`;
        aiMessage.classList.add("error-message");
    } finally {
        setSending(false);
        textarea.focus();
        scrollToLatestMessage();
    }
});

newChatButton.addEventListener("click", () => {
    chatBox.querySelectorAll(".message").forEach((message) => message.remove());
    welcome.hidden = false;
    textarea.value = "";
    resizeTextarea();
    textarea.focus();
});
