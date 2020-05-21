import socket
print(socket.gethostbyname(socket.gethostname()))

from app import app

app.run(host=socket.gethostbyname(socket.gethostname()), port='8080', debug=True)
