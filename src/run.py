from main import socketio as application
from main import app 

if __name__ == '__main__':
    application.run(app,host='192.168.100.46')
