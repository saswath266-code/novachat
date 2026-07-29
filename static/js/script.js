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

sendBtn.addEventListener("click", () => {

    const message = textarea.value.trim();

    if (message === "") return;

    welcome.style.display = "none";

    const userMessage = document.createElement("div");

    userMessage.className = "message user-message";

    userMessage.textContent = message;

    chatBox.appendChild(userMessage);

    textarea.value = "";

    textarea.style.height = "58px";

    chatBox.scrollTop = chatBox.scrollHeight;

});