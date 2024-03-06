var WebSocket = require('ws')
var ws = new WebSocket("ws://localhost:8889/register?userid=bordeanu");
ws.onmessage = function(event) {
    console.log(event.data);
}

