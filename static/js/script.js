const textarea = document.querySelector("textarea");
const sendBtn = document.querySelector(".input-area button");
const chatBox = document.getElementById("chatBox");
const welcome = document.getElementById("welcome");

textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
});

textarea.addEventListener("keydown", (event) => {

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendBtn.click();
    }

});

sendBtn.addEventListener("click", async () => {

    const message = textarea.value.trim();

    if (message === "") return;

    welcome.style.display = "none";

    const userMessage = document.createElement("div");
    userMessage.className = "message user-message";
    userMessage.textContent = message;
    chatBox.appendChild(userMessage);

    textarea.value = "";
    textarea.style.height = "58px";

    const aiMessage = document.createElement("div");
    aiMessage.className = "message ai-message";
    aiMessage.textContent = "Thinking...";
    chatBox.appendChild(aiMessage);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {

        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();

        aiMessage.textContent = data.response;

    } catch (error) {
    console.error(error);
    aiMessage.textContent = error.message;
}

    chatBox.scrollTop = chatBox.scrollHeight;

});