let SOCKET = new WebSocket('ws://localhost:6789');
let USERNAME = '';
let MESSAGES = [];

function refresh_messages() {
  // generate HTML of MESSAGES
  output_html = '';
  message = '';
  for (i = 0; i < MESSAGES.length; i++) {
    console.log(MESSAGES[i])
    message += `&gt;${MESSAGES[i]["message"]}<br />`;
    author = MESSAGES[i]["author"];
    timestamp = MESSAGES[i]["timestamp"];
    // in case of multiple messages from the same author
    if (MESSAGES[i + 1]) {
      if (MESSAGES[i + 1].author === author) {
        continue;
      }
    }
    output_html += `<div class="chat-message row"><div class="profile-pic col-2"><img src="https://via.placeholder.com/64" /></div><div class="message-info col-8"><h4 class="usename">${author}</h4><p class="message">${message}</p></div><div class="time-stamp col-2"><time>${timestamp}</time></div></div>`;
    message = '';
  }
  if (output_html === ''){
    output_html = "<h3>No messages yet...</h3>"
  }
  document.querySelector('#chat-box').innerHTML = output_html;
}

SOCKET.onopen = function (e) {
  console.log('[open] Connection established');
  USERNAME = prompt('Enter Username');
  console.log('Sending to server');
  SOCKET.send(`log in as ${USERNAME}`);
};

SOCKET.onmessage = function (event) {
  console.log(`[message] Data received from server: ${event.data}`);
  if (event.data.indexOf('MESSAGE') == '0') {
    console.log(`message: ${event.data}`);
  }
  MESSAGES = JSON.parse(event.data);
  refresh_messages();
};

SOCKET.onclose = function (event) {
  if (event.wasClean) {
    alert(`[close] Connection closed cleanly, code=${event.code}`);
  } else {
    alert('[close] Disconnected');
  }
};

SOCKET.onerror = function (error) {
  alert(`[error] ${error.message}`);
};

function send_message() {
  message = document.querySelector('#messageTextarea').value;
  console.log({message});
  SOCKET.send(message);
  // resetting the message box
  document.querySelector('#messageTextarea').value = "";
}
