from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
from engineio.async_drivers import threading

chat = Flask(__name__)
chat.config["SECRET_KEY"] = "YOUR_SECRET_KEY_HERE"
socketio = SocketIO(chat, cors_allowed_origins="*", async_mode="threading")

usernames = {}
number_of_users = 0

@chat.route("/")
def Index():
	return render_template("index.html")

@socketio.on("new message", namespace="/chat")
def NewMessage(data):
	emit("new message",
		{"username" : session["username"],
	 	"message": data}, broadcast=True)

@socketio.on("add user", namespace="/chat")
def AddUser(data):
	global usernames
	for user in usernames:
		if user == data:
			emit("invalidNickName")
			return
	global number_of_users
	session["username"] = data
	usernames[data] = session["username"]
	number_of_users += 1
	emit("login", {"numUsers" : number_of_users})
	emit("user joined", { "username" : session["username"], "numUsers": number_of_users}, broadcast=True)

@socketio.on("typing", namespace="/chat")
def IsTyping():
	try:
		emit("typing", {"username" : session["username"]}, broadcast=True )
	except:
		pass

@socketio.on("stop typing", namespace="/chat")
def StopedTyping():
	try:
		emit("stop typing", {"username" : session["username"]}, broadcast=True)
	except:
		pass

@socketio.on("disconnect", namespace="/chat")
def Disconnect():
	global usernames
	global number_of_users
	try:
		del usernames[session["username"]]
		number_of_users -= 1
		emit("user left", {"username" : session["username"], "numUsers" : number_of_users}, broadcast=True)
	except:
		pass

if __name__ == "__main__":
	socketio.run(chat, host="0.0.0.0" port=5000)
