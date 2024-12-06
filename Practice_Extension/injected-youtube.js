var videoPlayer = null;
var player = null;
var editorExtensionId = "pcmngjiogdapgmdbcfegloonelminlpp";
var port = chrome.runtime.connect(editorExtensionId, { name: "webpage-youtube" });

window.addEventListener("load", async () => {
    player = document.querySelector("video");
    await throttledCheck(() => {
        return player?.isConnected ? true : false
    })
    console.log(player, player.currentTime);
    port.postMessage({ message: "Connection Established!", status: player.paused });
    window.addEventListener(
        "message",
        (event) => {
            console.log("injected", event, player, player.paused);
            if (!player.paused) {
                player.pause();
            } else {
                player.play();
            }
        },
        false
    );

    player.onpause = (e) => {
        console.log(player.paused, "Paused", e);
        port.postMessage({ message: "Status Changed", status: player.paused });
    }

    player.onplay = (e) => {
        console.log(player.paused, "Played", e);
        port.postMessage({ message: "Status Changed", status: player.paused });
    }
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function throttledCheck(callback) {
    for (let i = 0; i < 5; i++) {
        if (callback()) return;
        await sleep(i * 500);
    }
    console.log('Done');
}