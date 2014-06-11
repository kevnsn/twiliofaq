# app.py or app/__init__.py
import urllib
import requests
from pattern import web
from twilio.rest import TwilioRestClient
import twilio.twiml
from xml.sax.saxutils import escape, unescape

from flask import Flask
from flask import request
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
# Now we can access the configuration variables via app.config["VAR_NAME"].


#Helper methods
html_escape_table = {
     "&": "&amp;",
     '"': "&quot;",
     "'": "&apos;",
     ">": "&gt;",
     "<": "&lt;",
     "'":"&rsquo;"
}
html_unescape_table = {v:k for k, v in html_escape_table.items()}

def html_unescape(text):
    return unescape(text, html_unescape_table)

def get_text(seach_number, search_results):
    fstr="There were "+search_number+" results for your query.  Top five are listed, text the number back for more info:\n"
    for idx, res in enumerate(search_results):
        fstr+=str(idx+1)+") "+html_unescape(res['title'])+"\n"
    return fstr

def get_search(input_str):
    search_url="https://www.twilio.com/help/search?q="
    query_string=urllib.quote_plus(input_str)
    page = requests.get(search_url+query_string).text

    dom=web.Element(page)
    result_num=(dom.by_class('search-meta'))[0].content[6:]

    raw = dom.by_class('result-title')[0:5]
    results = []
    for res in raw:
        res_link=res.by_tag('a')[0]
        link = res_link.attrs['href']
        title = res_link.content
        results.append({"link":link,"title":title})

    return result_num, results

@app.route('/receive', methods=['POST'])
def sighting():
    isFirst=session.get('isFirst', True)
    Answers=session.get('Answers',None)
    if isFirst:
      message = """Welcome to the Twilio FAQ, to begin, enter a search query.\n
      For example, "number porting" or "volume pricing"
      """
      session['isFirst']=False
    elif Answers==None:
      search_string=request.values.get('Body')
      search_number, search_results=get_search(search_string)
      message = get_text(search_number, search_results)
    #Convert the message string to a TwiML response that is returned
    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)


if __name__ == '__main__':
    app.run()
