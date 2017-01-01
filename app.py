from flask import Flask
from flask import request, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    tvar = 'bob'

    return render_template('index.html', tvar = tvar)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)