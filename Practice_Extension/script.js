document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("testButton");

    if (button) {
        button.addEventListener("click", () => {
            console.log("Clicked button");
        });
    } else {
        console.error("Button with ID 'testButton' not found.");
    }
});