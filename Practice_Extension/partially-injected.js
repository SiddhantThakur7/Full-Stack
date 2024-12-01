var port = chrome.runtime.connect({ name: "content-script" });
port.postMessage({ message: "Connection Established!" });
port.onMessage.addListener(function (msg) {
    console.log(msg);
    window.postMessage("play/pause");
});

window.addEventListener(
    "message",
    (event) => {
        console.log("partially-injected", event);
    },
    false
);

