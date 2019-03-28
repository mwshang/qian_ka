from flask import Flask

app = Flask(__name__)

@app.route("/")
def getTest():
    return "root gotted..."

@app.route("/hello")
def hello():
    return "Hello World!"

@app.route('/projects/')
def projects():
    return 'The project page'
hasattr()
@app.route('/about')
def about():
    return 'The about page'

if __name__ == "__main__":
    app.run(debug=True)