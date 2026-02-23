const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8001/ws';

class WebSocketService {
  constructor() {
    this.connections = {};
    this.listeners = {};
  }

  connect(channel = 'default') {
    if (this.connections[channel]) return;

    const ws = new WebSocket(`${WS_URL}/events/${channel}`);

    ws.onopen = () => {
      console.log(`WebSocket connected: ${channel}`);
      this._emit(channel, 'connected', {});
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this._emit(channel, data.type || 'message', data);
      } catch (e) {
        console.error('WebSocket parse error:', e);
      }
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected: ${channel}`);
      delete this.connections[channel];
      setTimeout(() => this.connect(channel), 5000);
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error on ${channel}:`, error);
    };

    this.connections[channel] = ws;
  }

  disconnect(channel) {
    if (this.connections[channel]) {
      this.connections[channel].close();
      delete this.connections[channel];
    }
  }

  subscribe(channel, eventType, callback) {
    const key = `${channel}:${eventType}`;
    if (!this.listeners[key]) this.listeners[key] = [];
    this.listeners[key].push(callback);

    return () => {
      this.listeners[key] = this.listeners[key].filter((cb) => cb !== callback);
    };
  }

  send(channel, data) {
    const ws = this.connections[channel];
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }

  _emit(channel, eventType, data) {
    const key = `${channel}:${eventType}`;
    (this.listeners[key] || []).forEach((cb) => cb(data));
  }
}

const wsService = new WebSocketService();
export default wsService;
