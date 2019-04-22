$(document).ready(function(){
      var socket = io.connect();
      //get message
      socket.on('home', function(msg) {
        $('#messages').prepend('<div class="contentBlock"><b>' + msg.time + ':</b> ' + msg.content + '</div>');
      });
    });
