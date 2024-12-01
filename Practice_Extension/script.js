var tabId = null;
var contentScriptConnection = null;
var webpageConnection = null;
var statusDisplay = null;


chrome.runtime.onConnect.addListener(function (port) {
  contentScriptConnection = port
  port.onMessage.addListener(function (msg) {
    console.log('Content-Script: ', msg);
  });
});

chrome.runtime.onConnectExternal.addListener(function (port) {
  webpageConnection = port
  port.onMessage.addListener(function (msg) {
    console.log('Webpage: ', msg);
    statusDisplay.innerHTML = `Status: ${msg.status ? "Paused" : "Playing"}`
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("testButton");
  statusDisplay = document.getElementById("status")
  if (button) {
    button.addEventListener("click", () => {
      console.log("Button Clicked 1", contentScriptConnection, statusDisplay);
      contentScriptConnection.postMessage("play/pause");
    });
  } else {
    console.error("Button with ID 'testButton' not found.");
  }
});
