from flask import Flask, Response, send_file, request, make_response
import os


# starter code found here: https://blog.logrocket.com/build-deploy-flask-app-using-docker/
# directs '/' requests to index.html
app = Flask(__name__)

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


