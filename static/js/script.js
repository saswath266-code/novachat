const textarea = document.querySelector("textarea");

textarea.addEventListener("input", () => {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
});

textarea.addEventListener("keydown", (event) => {

    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();

        document.querySelector(".input-area button").click();
    }

});