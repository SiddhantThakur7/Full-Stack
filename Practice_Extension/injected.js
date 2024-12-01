var videoPlayer = null;
var player = null;
var editorExtensionId = "pcmngjiogdapgmdbcfegloonelminlpp";
var port = chrome.runtime.connect(editorExtensionId, { name: "webpage" });

window.addEventListener("load", async () => {
  videoPlayer = window.netflix.appContext.state.playerApp.getAPI().videoPlayer;
  await throttledCheck(() => {
    console.log(videoPlayer.getAllPlayerSessionIds(), player?.getReady())
    player = videoPlayer.getVideoPlayerBySessionId(
      videoPlayer.getAllPlayerSessionIds()[0]
    );
    return player?.getReady() ? true : false
  })

  console.log(
    "DOM fully loaded and parsed",
    window,
    window.netflix,
    chrome,
    chrome.runtime,
    videoPlayer,
    videoPlayer.getAllPlayerSessionIds(),
    player
  );
  port.postMessage({message: "Connection Established!", status: player.isPaused() });
  // window.postMessage("message");
  window.addEventListener(
    "message",
    (event) => {
      if (!player) {
        player = videoPlayer.getVideoPlayerBySessionId(
          videoPlayer.getAllPlayerSessionIds()[0]
        );
      }
      console.log("injected", event, player);
      if (player.isPlaying()) {
        player.pause();
      } else {
        player.play();
      }
    },
    false
  );

  player.addEventListener('pausedchanged', () => {
    console.log(player.isPaused());
    port.postMessage({ message: "Status Changed", status: player.isPaused() });
  })
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