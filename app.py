from flask import Flask
from flask import request, render_template, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    numse = np.array([1, 2, 3])
    tvar = 'bob'

    return render_template('index.html', tvar = tvar)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)


# https://github.com/datademofun/heroku-basic-flask/blob/master/README.md