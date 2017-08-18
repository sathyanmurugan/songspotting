import flask
import os
app = flask.Flask(__name__)




@app.route('/')
def main():
	return flask.render_template('main.html')

if __name__ == '__main__':
    app.run(debug=os.environ['DEBUG'])