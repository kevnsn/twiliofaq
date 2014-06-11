# app.py or app/__init__.py
import urllib
import requests
from pattern import web
from twilio.rest import TwilioRestClient

from flask import Flask
from flask import request
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
# Now we can access the configuration variables via app.config["VAR_NAME"].

@app.route('/receive', methods=['POST'])
def sighting():
  client = TwilioRestClient(app.config["ACCOUNT_SID"], app.config["AUTH_TOKEN"])
  client.messages.create(from_="+16176817858", to="+16172866786", body=str(request.args))
  return str(request.args)


if __name__ == '__main__':
    app.run()
