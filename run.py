import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])

from flask_app import app

app.run(host=s.getsockname()[0], port='8080', debug=True)

s.close()