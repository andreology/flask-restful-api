from flask import Flask 

app = Flask(__name__)

@app.route('/')
def ello_world():
    return 'Ello Chap'

if __name__ == '__name__':
    app.run()