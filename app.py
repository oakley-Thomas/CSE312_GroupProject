from flask import Flask
from flask import Response
from flask import render_template
from flask import send_file
from flask import request
from flask import send_from_directory
from flask import make_response
from urllib.parse import unquote, quote
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
import string, random
from flask import Flask, jsonify, request, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from werkzeug.wrappers import Response
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# starter code found here: https://blog.logrocket.com/build-deploy-flask-app-using-docker/
# directs '/' requests to index.html
app = Flask(__name__, static_folder=None)
socketio = SocketIO(app, cors_allowed_origins="*", transports='websocket')

client = MongoClient("mongodb://mongo:27017/")
db = client["CSE312ProjectDB"]
registered_users = db["users"]
posts_collection = db["posts"]
quiz_collection = db["quizzes"]
timers = {}
blockedIp = {}


# @app.route('/', methods=['POST'])
# def insert():
#     data = request.json
#     registered_users.insert_one(data)
#     return

wsgiApp = app.wsgi_app

def checkBlock(environ, start_response):
    ip = environ['REMOTE_ADDR']
    if ip in blockedIp:
        block_until = blockedIp[ip]
        if datetime.now() < block_until:
            response = Response('Too many requests. Please slow down.', 429)
            return response(environ, start_response)
        else:
            del blockedIp[ip]
    return wsgiApp(environ, start_response)

app.wsgi_app = checkBlock

limiter = Limiter(key_func=get_remote_address, default_limits=["50 per 10 second"])
limiter.init_app(app)

def get_remote_address():
    if 'X-Forwarded-For' in request.headers:
        return request.headers.getlist("X-Forwarded-For")[-1]
    else:
        return request.remote_addr

@app.errorhandler(429)
def ratelimit_handler(e):
    ip = get_remote_address()
    blockedIp[ip] = datetime.now() + timedelta(seconds=30)
    return make_response(jsonify(error="Too many requests. Please slow down."), 429)

@app.route('/static/<path:path>')
@limiter.limit("50 per 10 second")
def send_static_file(path):
    return send_from_directory('static', path)

def gmail_authenticate():
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def build_message(destination, obj, body):
    our_email = 'spiderwebquizzes@gmail.com'

    message = MIMEMultipart()
    message['to'] = destination
    # message['from'] = our_email
    message['subject'] = obj
    message.attach(MIMEText(body))

    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, destination, obj, body):
    return service.users().messages().send(
      userId="me",
      body=build_message(destination, obj, body)
    ).execute()

def gmail_send_message(user):
    service = gmail_authenticate()

    random_string_with_80_bits_of_entropy = ''.join(random.choices(string.ascii_letters + string.digits, k=50))  # hashlib.sha256()

    body = "This is a verification email.\n\nClick on this link to verify your email: http://159.65.240.148:8080/verifyemail/" + random_string_with_80_bits_of_entropy

    send_message(service, user, "Verify your email", body)

    return

@app.route('/verifyemail/<id>')
def verified(id):
    id = id
    user = get_user()
    registered_users.update_one({"username": user}, {"$set": {"email_verified": "true"}})
    return redirect('/', 302)

@app.route('/verify_email', methods=['POST'])
def send_verification_link():
    user = get_user()
    gmail_send_message(user)
    return "Success", 200


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

# @app.route('/')
# def home():
#     if request.cookies != None and request.cookies.get("auth-token") != None:
#         token = request.cookies.get("auth-token")
#         user = get_user()
#
#         # user = db["users"].find_one({"auth-token": token})
#         response = make_response(render_template('index.html'))
#         if user is None:
#             response.set_cookie('username', "inv-token")
#         if user is not None:
#             nametest = user # user["username"]
#             response.set_cookie('username', nametest)
#         return response
#     return render_template('index.html')

@app.route('/')
def home():
    show_verify_button = True
    if request.cookies != None and request.cookies.get("auth-token") != None:
        token = request.cookies.get("auth-token")
        user = get_user()
        user_data = registered_users.find_one({'username': user})
        user_verified_email = user_data["email_verified"]

        # user = db["users"].find_one({"auth-token": token})
        show_verify_button = user_verified_email != "true"
        response = make_response(render_template('index.html',show_verify_button=show_verify_button))
        if user is None:
            response.set_cookie('username', "inv-token")
        if user is not None:
            nametest = user # user["username"]
            response.set_cookie('username', nametest)
        return response
    return render_template('index.html',show_verify_button=show_verify_button)


@socketio.on('connect')
def handle_connect():
    url = request.args.get('url')
    if url is not None:
        session['url'] = url
    print(f"Client connected with url {url}")
    if url in timers:
        remaining_time = timers[url]

        # Emit the remaining time to the client
        emit('timer', {'url': url, 'data': remaining_time})

@app.route('/start-quiz', methods=['POST'])
def start_quiz():
    # Get the URL and duration from the request body
    url = request.json.get('url')
    url = unquote(url).replace(" ", "_").replace("?","*")
    print("QUIZ URL: " + url, flush=True)
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

def get_user():
    auth_token_from_cookie = request.cookies.get("auth-token")
    hashed_of_above_token = hashlib.sha256(auth_token_from_cookie.encode()).hexdigest()
    stored_hash = registered_users.find_one({"auth-token": hashed_of_above_token})
    if stored_hash is not None:
        user = stored_hash["username"]
        return user
    else:
        return None

@app.route('/login-request', methods=['POST'])
def loginRequest():
    username = request.form["username"]
    password = request.form["password"]

    if username and password:
        user_data = registered_users.find_one({'username': username})
        if user_data and verify_password(password, user_data['password_hash']):
            # authtoken = hash_function(user_data['username'])
            random_string = ''.join(random.choices(string.ascii_letters, k=25))
            authtoken = hashlib.sha256(random_string.encode()).hexdigest()
            registered_users.update_one({'username': username}, {'$set': {'auth-token': authtoken}})
            response = make_response(redirect('/'))
            response.set_cookie('auth-token', random_string, httponly=True, max_age=3600)
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

@app.route('/view-quiz/images/<name_of_image>')
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

def get_the_grade(hashed_value):
    if bcrypt.checkpw(b'0', hashed_value):
        return '0'
    elif bcrypt.checkpw(b'1', hashed_value):
        return '1'
    elif bcrypt.checkpw(b'Not Answered (Grade = 0)', hashed_value):
        return 'Not Answered (Grade = 0)'

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    token = request.cookies.get("auth-token") 
    if token is None or token == 'unauth':
        response = "Unauthenticated"
        return json.dumps(response)

    user = get_user()
    if user is None:
        response = "Unauthenticated"
        return json.dumps(response)
    

    post = request.get_json(force=True)

    # Escape HTML
    post["title"] = html.escape(post["title"])
    post["correct"] = html.escape(post["correct"])
    post["duration"] = html.escape(post["duration"])
    post["category"] = html.escape(post["category"])

    for choice in post["choices"].keys():
        post["choices"][choice] = html.escape(post["choices"][choice])
    #post["choices"] = html.escape(post["choices"])

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
        print("Found Image!", flush=True)
        quiz["image"] = "images/" + post["title"].replace('?', '') + '.jpg'
        the_image = post["image"].split(',')[1]
        image_as_bytes = base64.b64decode(the_image)
        file = open('./static/uploaded-images/' + post["title"].replace('?', '') + '.jpg', 'wb')
        file.write(image_as_bytes)
        file.close()

    new_quiz = {}
    new_quiz["option_chosen"] = ""
    hashed_grade = bcrypt.hashpw(b'Not Answered (Grade = 0)', bcrypt.gensalt())
    new_quiz["grade"] = hashed_grade
    for users in list(registered_users.find()):
        if users["username"] == user:
            pass
        else:
            if users.get("quizzes_list") == None:
                quiz_to_insert = {quiz["title"]: new_quiz}
                registered_users.update_one({"username": users["username"]}, {"$set": {"quizzes_list": quiz_to_insert}})
            else:
                previous_quizzes = users["quizzes_list"]
                previous_quizzes[quiz["title"]] = new_quiz
                registered_users.update_one({"username": users["username"]}, {"$set": {"quizzes_list": previous_quizzes}})

    quiz_collection.insert_one(quiz)

    response = "OK"
    return json.dumps(response)

def grade_quiz(post):
    username = get_user()
    user = registered_users.find_one({"username": username})
    
    question = unquote(post["id"])
    answer_given = post["answer"]
    quiz = quiz_collection.find_one({"title": question})
    correct_answer = quiz["answer"]

    if user["quizzes_list"].get(question) == None:
        return

    quizzes_updated = user["quizzes_list"]

    if quizzes_updated[question]["option_chosen"] == "":
        if answer_given == correct_answer:
            quizzes_updated[question]["option_chosen"] = answer_given
            quizzes_updated[question]["grade"] = bcrypt.hashpw(b'1', bcrypt.gensalt())
            registered_users.update_one({"username": user["username"]}, {"$set": {"quizzes_list": quizzes_updated}})
            return
        else:
            quizzes_updated[question]["option_chosen"] = answer_given
            quizzes_updated[question]["grade"] = bcrypt.hashpw(b'0', bcrypt.gensalt())
            registered_users.update_one({"username": user["username"]}, {"$set": {"quizzes_list": quizzes_updated}})
            return
    else:
        return

@app.route('/answer-quiz', methods=['POST'])
def answer_quiz():
    post = request.get_json(force=True)
    token = request.cookies.get("auth-token") 

    if token is None or token == 'unauth':
        response = "Unauthenticated"
        return json.dumps(response)

    username = get_user()
    quiz_id = unquote(post["id"])
    quiz_data = quiz_collection.find_one({"title": quiz_id})
    ownerUsername = quiz_data["username"]


    if ownerUsername == username:
        response = "Owner"
        return json.dumps(response)
    
    if username is None:
        response = "Unauthenticated"
        return json.dumps(response)
    
    else:
        grade_quiz(post)
        response = "OK"
        return json.dumps(response)

@app.route('/user_grades')
def send_grades():
    user = get_user()
    if registered_users.find_one({"username": user}).get("quizzes_list") == None:
        a_dict = [{"question": "", "grade": ""}, {"question": "", "grade": ""}]
        return json.dumps(a_dict)
    quizzes = registered_users.find_one({"username": user})["quizzes_list"]
    list_to_send = []
    for each_quiz in quizzes:
        quiz = quizzes[each_quiz]
        a_quiz = {}
        a_quiz["question"] = each_quiz
        hashed_grade = quiz["grade"]
        unhashed_grade = get_the_grade(hashed_grade)
        a_quiz["grade"] = unhashed_grade
        list_to_send.append(a_quiz)
    send_as_json = json.dumps(list_to_send)
    return send_as_json

@app.route('/user_posted_quizzes_grades')
def send_quizzes_grades():
    user = get_user()
    quizzes_by_this_user = quiz_collection.find({"username": user})
    list_of_quizzes = []
    for quiz in quizzes_by_this_user:
        title = quiz["title"]
        list_of_quizzes.append(title)
    list_to_send = []
    for quizzes in list_of_quizzes:
        for users in list(registered_users.find()):
            if users["username"] == user:
                pass
            else:
                if users.get("quizzes_list") == None:
                    pass
                elif (users["quizzes_list"]).get(quizzes) == None:
                    pass
                else:
                    a_quiz = {}
                    this_quiz = users["quizzes_list"][quizzes]
                    a_quiz["question"] = quizzes
                    a_quiz["username"] = users["username"]
                    hashed_grade = this_quiz["grade"]
                    unhashed_grade = get_the_grade(hashed_grade)
                    a_quiz["grade"] = unhashed_grade
                    list_to_send.append(a_quiz)

    send_as_json = json.dumps(list_to_send)
    return send_as_json

@app.route('/view-quiz/<id>')
def view_quiz(id):
    quiz_id = str(id)
    quiz_id = quiz_id.replace("_", " ")
    quiz_id = quiz_id.replace("*", "?")
    
    quiz_data = quiz_collection.find_one({"title": quiz_id})
    if (quiz_data is None):
        return render_template("quiz.html", quizTitle = "ERROR", quizCategory = "ERROR", timeRemaining = 0)

    choices = quiz_data["choices"]
    img = quiz_data.get("image")

    if img is not None:
        return render_template("quiz.html", 
                           quizTitle = quiz_data["title"], 
                           quizCategory = quiz_data["category"], 
                           timeRemaining = quiz_data["duration"],
                           quizChoices = choices,
                           postOwner = quiz_data["username"],
                           image = quote(img)
                           )
    else:
        return render_template("quiz.html", 
                           quizTitle = quiz_data["title"], 
                           quizCategory = quiz_data["category"], 
                           timeRemaining = quiz_data["duration"],
                           quizChoices = choices,
                           postOwner = quiz_data["username"]
                           )

    
    

@app.template_filter('url_decode')
def url_decode_filter(s):
    ret = unquote(s) 
    print("Decoded: " + ret)
    return ret

@app.route('/gradebook')
def user_gradebook():
    return render_template('user_gradebook.html')

@app.route('/userGrades')
def user_grades():
    #token = request.cookies.get("auth-token")
    #user = db["users"].find_one({"auth-token": token})

    #if user is None:
        #return render_template('login.html')
    #else:
    return render_template('user_grades.html')


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
    username = html.escape(request.form["username"])
    password = html.escape(request.form["password"])
    passConf = html.escape(request.form["password-confirm"]) 

    if password != passConf:
        print("Error, Please Try again", flush=True)
        return render_template('register.html')

    # Get the passwords hash value
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    registered_users.insert_one({
        "username": username,
        "password_hash": hashed_pw,
        "email_verified": "false"
    })

    return render_template('login.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
    print("Listening on port: " + str(port), flush=True)

