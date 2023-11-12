from flask import Flask
from flask import Response
from flask import render_template
from flask import send_file
from flask import request
from flask import send_from_directory
from flask import make_response
from flask_socketio import SocketIO, emit
from threading import Thread
from flask import session
import os, bcrypt
from pymongo import MongoClient
import json
from flask import redirect
import html
import hashlib
import time
import base64

# starter code found here: https://blog.logrocket.com/build-deploy-flask-app-using-docker/
# directs '/' requests to index.html
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", transports='websocket')

client = MongoClient("mongodb://mongo:27017/")
db = client["CSE312ProjectDB"]
registered_users = db["users"]
posts_collection = db["posts"]
quiz_collection = db["quizzes"]
timers = {}


# @app.route('/', methods=['POST'])
# def insert():
#     data = request.json
#     registered_users.insert_one(data)
#     return

def hash_function(stringToHash):
    return bcrypt.hashpw(stringToHash.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, hash):
    return bcrypt.checkpw(password.encode('utf-8'), hash)

def countdown_timer(url, duration):
    while duration:
        hours, remainder = divmod(duration, 3600)
        mins, secs = divmod(remainder, 60)
        timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        duration -= 1
        timers[url] = timer  # Update the timer for this quiz
        socketio.emit('timer', {'url': url, 'data': timer})

@app.route('/')
def home():
    if request.cookies != None and request.cookies.get("auth-token") != None:
        token = request.cookies.get("auth-token")
        user = db["users"].find_one({"auth-token": token})
        response = make_response(render_template('index.html'))
        if user is None:
            response.set_cookie('username', "inv-token")
        if user is not None:
            nametest = user["username"]
            response.set_cookie('username', nametest)
        return response
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    url = request.args.get('url')
    if url is not None:
        session['url'] = url
    print(f"Client connected with url {url}")

@app.route('/start-quiz', methods=['POST'])
def start_quiz():
    # Get the URL and duration from the request body
    url = request.json.get('url')
    duration_in_hours = request.json.get('duration')
    if url is None or duration_in_hours is None:
        return "URL or duration not provided", 400

    # Convert the duration to seconds
    duration_in_seconds = int(duration_in_hours) * 60 * 60

    # Start the timer for this quiz
    thread = Thread(target=countdown_timer, args=(url, duration_in_seconds))
    thread.start()
    return "Quiz started", 200

@app.route('/test')
def test_page():
    return send_from_directory('templates', 'test.html')

@app.route('/login')
def login():
    print("Redirecting to Login Page")
    return render_template("login.html")

@app.route("/logout")
def logout():
    resp = make_response()
    resp.set_cookie('auth-token', 'unauth')
    return resp

@app.route('/login-request', methods=['POST'])
def loginRequest():
    username = request.form["username"]
    password = request.form["password"]

    if username and password:
        user_data = registered_users.find_one({'username': username})
        if user_data and verify_password(password, user_data['password_hash']):
            # authtoken = hash_function(user_data['username'])
            authtoken = hashlib.sha256(user_data['username'].encode()).hexdigest()
            registered_users.update_one({'username': username}, {'$set': {'auth-token': authtoken}})
            response = make_response(redirect('/'))
            response.set_cookie('auth-token', authtoken, httponly=True, max_age=3600)
            return response


    print("Authentication failed", flush=True)
    return render_template('login.html')

@app.route('/posts')
def posts():
    print("Redirecting to Posts Page")
    return render_template("posts.html")

@app.route('/quizzes')
def load_quiz_creator():
    return render_template("quizzes.html")

@app.route('/quiz-history')
def quiz_history():
    all_posts = list(quiz_collection.find({},{"_id": 0}))
    return all_posts

@app.route('/images/<name_of_image>')
def respond_image(name_of_image):
    name_of_image = name_of_image.replace('/', '')
    file = open('./static/uploaded-images/' + name_of_image, 'rb')
    respond = file.read()
    file.close()
    return respond

#TODO this needs to be deleted before pushing to production... clears quiz database
@app.route('/clear')
def clear_quizzes():
    quiz_collection.delete_many({})
    print("Cleared DB", flush=True)
    jsonResponse = json.dumps("Cleared Database")
    return jsonResponse

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    token = request.cookies.get("auth-token") 
    if token is None or token == 'unauth':
        response = "Unauthenticated"
        return json.dumps(response)
    
    user = registered_users.find_one({"auth-token": token})["username"]
    if user is None:
        response = "Unauthenticated"
        return json.dumps(response)
    print("Username: " + str(user), flush=True)
    

    post = request.get_json(force=True)

    # Escape HTML
    post["title"] = html.escape(post["title"])
    post["correct"] = html.escape(post["correct"])
    post["duration"] = html.escape(post["duration"])
    post["category"] = html.escape(post["category"])

    # make sure not a duplicate question
    if (quiz_collection.find_one({"title": post["title"]})):
        print("Duplicate!", flush=True)
        response = "Duplicate"
        return json.dumps(response)
        
    # Input Checks
    # Make sure a valid duration is given (default to 1 hour)
    if (int(post["duration"]) > 24 or int(post["duration"]) < 1):
        post["duration"] = 1
    
    #---- Database ---
    quiz = {
        "title": post["title"],
        "choices": post["choices"],
        "answer": post["correct"],
        "duration": post["duration"],
        "category": post["category"],
        "username": user
    }
    if post.get("image") != None:
        quiz["image"] = "images/" + post["title"] + '.jpg'
        the_image = post["image"].split(',')[1]
        image_as_bytes = base64.b64decode(the_image)
        file = open('./static/uploaded-images/' + post["title"] + '.jpg', 'wb')
        file.write(image_as_bytes)
        file.close()
    quiz_collection.insert_one(quiz)

    response = "OK"
    return json.dumps(response)

@app.route('/answer-quiz', methods=['POST'])
def answer_quiz():
    post = request.get_json(force=True)
    token = request.cookies.get("auth-token") 

    if token is None or token == 'unauth':
        response = "Unauthenticated"
        return json.dumps(response)
    
    username = registered_users.find_one({"auth-token": token})["username"]
    if username is None:
        response = "Unauthenticated"
        return json.dumps(response)
    else:
        jsonResponse = json.dumps("OK")
        return jsonResponse

    

@app.route('/userGrades')
def user_grades():
    token = request.cookies.get("auth-token")
    user = db["users"].find_one({"auth-token": token})

    if user is None:
        return render_template('login.html')
    else:
        #TODO: finish this later
        return 


@app.route('/createPost', methods=['POST'])
def store_posts():

    post = request.get_json(force=True)
    post["title"] = html.escape(post["title"])
    post["description"] = html.escape(post["description"])

    if request.cookies == None:
        return
    elif request.cookies.get("auth-token") == None:
        return
    else:
        if list((posts_collection.find({}))) == []:
            posts_collection.insert_one({"id_number": 1})
            id = 1
        else:
            id_dict = json.loads(json.dumps(list(posts_collection.find({"id_number": {"$exists": "true"}})), default=str))
            id = id_dict[0]["id_number"] + 1
            posts_collection.update_one({"id_number": id - 1}, {"$set": {"id_number": id + 1}})
        token = request.cookies.get("auth-token")
        the_user = registered_users.find_one({"auth-token": token})

        post["id"] = id
        post["username"] = html.escape(the_user["username"])
        post["likes"] = 0
        post["liked_by"] = []
        posts_collection.insert_one(post)
    return redirect('/posts', 301)

@app.route('/likepost/<id>', methods=['POST'])
def like_post(id):

    post_id = int(id)
    token = request.cookies.get("auth-token")
    the_user = registered_users.find_one({"auth-token": token})
    the_post = posts_collection.find_one({"id": post_id})
    current_likes = the_post["likes"]
    current_liked_by_list = the_post["liked_by"]
    if the_user["username"] in the_post["liked_by"]:
        posts_collection.update_one({"id": post_id}, {"$set": {"likes": current_likes - 1}})
        current_liked_by_list.remove(the_user["username"])
        posts_collection.update_one({"id": post_id}, {"$set": {"liked_by": current_liked_by_list}})
    else:
        posts_collection.update_one({"id": post_id}, {"$set": {"likes": current_likes + 1}})
        current_liked_by_list.append(the_user["username"])
        posts_collection.update_one({"id": post_id}, {"$set": {"liked_by": current_liked_by_list}})

    return redirect('/posts', 301)

@app.route('/post-history')
def post_history():
    all_posts = json.dumps(list(posts_collection.find({"title": {"$exists": "true"}})), default=str)
    return all_posts

@app.route('/register')
def registration():
    print("Redirecting to Registration Page")
    return render_template("register.html")

@app.route('/reg-request', methods = ['POST'])
def regRequest():
    username = request.form["username"]
    password = request.form["password"]
    passConf = request.form["password-confirm"]

    if password != passConf:
        print("Error, Please Try again", flush=True)
        return render_template('register.html')

    # Get the passwords hash value
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    registered_users.insert_one({
        "username": username,
        "password_hash": hashed_pw,
    })

    return render_template('login.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
    print("Listening on port: " + str(port), flush=True)

