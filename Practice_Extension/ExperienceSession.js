class ExperienceSession {
  sessionId = null;
  primaryPeer = null;

  constructor(sessionId = null) {
    sessionId = sessionId ?? Date.now(); //Todo: Change to a random hash code
  }

  SetPrimaryPeer = peer => {
    this.primaryPeer = peer;
  };
}
