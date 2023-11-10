from flask import Flask
from flask import Response
from flask import render_template
from flask import send_file
from flask import request
from flask import make_response
import os, bcrypt
from pymongo import MongoClient
import json
from flask import redirect
import html
import hashlib

# starter code found here: https://blog.logrocket.com/build-deploy-flask-app-using-docker/
# directs '/' requests to index.html
app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017/")
db = client["CSE312ProjectDB"]
registered_users = db["users"]
posts_collection = db["posts"]
quiz_collection = db["quizzes"]


# @app.route('/', methods=['POST'])
# def insert():
#     data = request.json
#     registered_users.insert_one(data)
#     return

def hash_function(stringToHash):
    return bcrypt.hashpw(stringToHash.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, hash):
    return bcrypt.checkpw(password.encode('utf-8'), hash)

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

@app.route('/login')
def login():
    print("Redirecting to Login Page")
    return render_template("login.html")

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

#TODO this needs to be deleted before pushing to production... clears quiz database
@app.route('/clear')
def clear_quizzes():
    quiz_collection.delete_many({})
    print("Cleared DB", flush=True)
    jsonResponse = json.dumps("Cleared Database")
    return jsonResponse

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    #if request.cookies.get("auth-token") == None:
     #   return
    post = request.get_json(force=True)
    # Get username and create database: Title -> Title, Choices(json), Correct ("option1", "option2"...)
    post["title"] = html.escape(post["title"])
    # TODO: Ask ChatGPT if its a valid question?
    # TODO: Escape each input answer HTML
    post["correct"] = html.escape(post["correct"])

    # Make sure a valid duration is given (default to 1 hour)
    if (int(post["duration"]) > 24 or int(post["duration"]) < 1):
        post["duration"] = 1
    
    print("Duration: " + post["duration"], flush=True)
    #---- Database ---
    quiz = {
        "title": post["title"],
        "choices": post["choices"],
        "answer": post["correct"],
        "duration": post["duration"]
    }
    jsonQuiz = json.dumps(quiz)
    # For now the uid for the post is just the title.... this probably means no duplicate questions
    quiz_collection.insert_one({post["title"]: jsonQuiz})

    jsonResponse = json.dumps("OK")
    return jsonResponse

@app.route('/answer-quiz', methods=['POST'])
def answer_quiz():
    post = request.get_json(force=True)
    print("Post ID: " + post["id"], flush=True)
    print("Selected Answer: " + post["answer"], flush=True)
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
    app.run(debug=True, host='0.0.0.0', port=port)
    print("Listening on port: " + str(port), flush=True)

