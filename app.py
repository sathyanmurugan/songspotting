import flask
import os
app = flask.Flask(__name__)



@app.route('/')
def hello():
    return "Hello World1!"

if __name__ == '__main__':
    app.run(debug=os.environ['DEBUG'])