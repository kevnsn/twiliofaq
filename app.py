# app.py or app/__init__.py
import urllib
import requests
from pattern import web
from twilio.rest import TwilioRestClient
import twilio.twiml

from flask import Flask
from flask import request
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
# Now we can access the configuration variables via app.config["VAR_NAME"].

@app.route('/receive', methods=['POST'])
def sighting():
    from_number = request.values.get('From', None)
    message = "Monkey, thanks for the message!"+str(request.values)
    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)


if __name__ == '__main__':
    app.run()
