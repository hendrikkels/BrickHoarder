import socket
import flask_app

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(s.getsockname()[0])

flask_app.app.run(host=s.getsockname()[0], port='8080', debug=True)

s.close()
