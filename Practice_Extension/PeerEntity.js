class PeerEntity {
    PEER_LIMIT = 4;
    #peerId = null;
    peerConnection = null;
    connections = [];
    offers = [];
    answers = [];
    session = null;
    constructor(isPrimary = false, primaryPeer = null) {}

    instantiate = async () => {
        this.#peerId = Date.now(); //Todo: Change to random hash code
        if (window.location.origin.includes('app')){ //Todo: Change 'app' to domain name of the hosted app
            this.AnswerSessionRequest(window.location.pathname.slice(1))
        } 
    }

    InstantiateSession = async () => {
        this.session = new ExperienceSession();
        // await SignallingServer.EstablishSocketConnection();
    }

    CreateSessionRequest = async () => {
        await this.InstantiateSession();
        for(let i = 0; i < PEER_LIMIT; i++){
            this.CreateConnectionEntity(true);
        }
        // await SignallingServer.Send({
        //     session: this.session,
        //     offers: this.offers,
        //     answers: this.answers,
        //     connections: this.connections
        // })
    }

    
    AnswerSessionRequest = async (sessionId, offer) => {
        // let connectionAssets = await SignallingServer.Get(sessionId);
        this.session = new ExperienceSession(JSON.parse(connectionAssets).sessionId);
        this.offers.push()
        
    }

    CreateConnectionRequest = (isPrimary = false) => {
        let connectionEntity = new PeerConnectionEntity(isPrimary);
        this.offers.push(connectionEntity.Offer(this.#peerId, this.offers.length));
        connections.push(connectionEntity)
    }

    CreateConnectionResponse = (isPrimary = false) => {
        let connectionEntity = new PeerConnectionEntity(isPrimary);
        this.answers.push(connectionEntity.Offer(this.#peerId, this.offers.length));
        connections.push(connectionEntity)
    }

    discoverDataChannel = async() => {
        
    }

}