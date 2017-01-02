from flask import Flask
from flask import request, render_template, jsonify
import pandas as pd
import numpy as np
from azure.storage.blob import BlockBlobService


account = 'dhspeed'
account_key = 'gePaxovANJMYSzIEnIWCD0aJPbbeogEjC8NfuJwvuAhKMsaOMwZbeWEr1C4hMqpunca/obB4LlwPlTqfr4EZgg=='


app = Flask(__name__)

@app.route('/')
def index():
    tvar = 'bob'

    block_blob_service = BlockBlobService(account_name=account, account_key=account_key)
    block_blob_service.get_blob_to_path('rides', 'id_1_calibrated.csv', 'azure_out_test.csv')

    ride = pd.read_csv('azure_out_test.csv')

    return render_template('index.html', tvar = tvar)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)


# https://github.com/datademofun/heroku-basic-flask/blob/master/README.md