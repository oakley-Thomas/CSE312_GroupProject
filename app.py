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

# starter code found here: https://blog.logrocket.com/build-deploy-flask-app-using-docker/
# directs '/' requests to index.html
app = Flask(__name__)

client = MongoClient("mongodb://mongo:27017/")
db = client["CSE312ProjectDB"]
registered_users = db["users"]
posts_collection = db["posts"]

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

@app.route('/login-request', methods = ['POST'])
def loginRequest():
    username = request.form["username"]
    password = request.form["password"]
    print("Logged In!", flush=True)
    return render_template('index.html')

@app.route('/posts')
def posts():
    print("Redirecting to Posts Page")
    return render_template("posts.html")

@app.route('/createPost', methods=['POST'])
def store_posts():

    post = request.get_json(force=True)

    if request.cookies == None:
        return
    elif request.cookies.get("auth-token") == None:
        return
    else:
        if len(posts_collection.find({})) == 0:
            posts_collection.insert_one({"id_number": 1})
            id = 1
        else:
            id_dict = client['db']['post_collection'].find({"id_number": {"$exists": "true"}})
            id = id_dict['id_number'] + 1
            posts_collection.update_one({"id_number": id - 1}, {"$set": {"id_number": id + 1}})
        token = request.cookies.get("auth-token")
        the_user = registered_users.find_one({"authtoken": token})

        post["id"] = id
        post["username"] = the_user["username"]
        post["likes"] = 0
        post["liked_by"] = []
        posts_collection.insert_one(post)
    return redirect('/posts', 301)

@app.route('/likepost', methods=['POST'])
def like_post():

    post_id = request.path.split('/likepost/')[1]
    token = request.cookies.get("auth-token")
    the_user = registered_users.find_one({"authtoken": token})
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

    return

@app.route('/post-history')
def post_history():
    all_posts = json.dumps(list(posts_collection.find({})), default=str)
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

