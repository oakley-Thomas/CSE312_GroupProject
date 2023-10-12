from flask import Flask, Response, send_file, request, make_response
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
    return send_file("../public/index.html")

@app.route('/public/style.css')
def css():
    return send_file("../public/style.css")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
    print("Listening on port: " + str(port), flush=True)


