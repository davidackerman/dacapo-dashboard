from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from dashboard import create_app, socketio
app = create_app()

if __name__ == '__main__':
    socketio.run(app)