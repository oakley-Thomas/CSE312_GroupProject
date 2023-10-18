from flask import Flask
from flask import Response
from flask import render_template
from flask import send_file
from flask import request
from flask import make_response
import os
from pymongo import MongoClient

# starter code found here: https://blog.logrocket.com/build-deploy-flask-app-using-docker/
# directs '/' requests to index.html
app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017/")
db = client["CSE312ProjectDB"]
registered_users = db["users"]

registered_users.insert_one({"id": 1, "username": "user1", "password": "1234"})   # test data

# the route for below may be changed and more methods could be added once we implement the webpages and buttons, etc
@app.route('/', methods=['POST'])
def insert():
    data = request.json
    registered_users.insert_one(data)
    return

@app.route('/')
def home():
    print("Serving index.html", flush=True)
    return render_template('index.html')

@app.route('/login')
def login():
    print("Redirecting to Login Page")
    return render_template("login.html")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
    print("Listening on port: " + str(port), flush=True)


