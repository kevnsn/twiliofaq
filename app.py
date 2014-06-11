# app.py or app/__init__.py
import urllib
import requests
from pattern import web
from twilio.rest import TwilioRestClient
import twilio.twiml
from xml.sax.saxutils import escape, unescape

from flask import Flask
from flask import request, redirect, session
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

def get_text(search_number, search_results):
    fstr="There were "+search_number+". Top five are as follows, text # back for more info:\n"
    for idx, res in enumerate(search_results):
        fstr+=str(idx+1)+") "+html_unescape(res['title'])+"\n"
    return fstr +"\nText NEW to start over."

def get_search(input_str):
    search_url="https://www.twilio.com/help/search?q="
    query_string=urllib.quote_plus(input_str)
    page = requests.get(search_url+query_string).text

    dom=web.Element(page)
    result_num=(dom.by_class('search-meta'))[0].content[6:]

    raw = dom.by_class('search-result')[0:5]
    results = []
    for res in raw:
        res_link=res.by_class('result-title')[0].by_tag('a')[0]
        link = res_link.attrs['href']
        title = res_link.content
        teaserstr=res.by_class('result-body')[0].content.replace("<em>","").replace("</em>","")
        endindex=teaserstr.find("Related")
        if endindex!=-1:
          teaserstr=teaserstr[:endindex-1]
        results.append({"link":link,"title":title, "teaser":teaserstr})

    return result_num, results

def get_answer_str(answer_index, search_results):
    answer=search_results[answer_index-1]
    return answer.get('title',"")+'\n..."'+answer.get('teaser',"")+'"...\nFor full answer, visit:\n'+answer.get('link',"") +"\nEnter a new answer # or reply NEW to start over"

@app.route('/receive', methods=['POST'])
def sighting():
    isFirst=session.get('isFirst', True)
    Answers=session.get('Answers',None)
    msgbody=request.values.get('Body').strip().lower()
    if isFirst or msgbody=="new":
      message = """Welcome to the Twilio FAQ, to begin, enter a search query or question.\nFor example, "number porting," "uk short code," or "How much does a phone number cost?"
      """
      session['isFirst']=False
      session['Answers']=None
    elif Answers==None:
      search_string=request.values.get('Body')
      search_number, search_results=get_search(search_string)
      message = get_text(search_number, search_results)
      session['Answers']=search_results
    else:
      #In this case Answers is defined and the user is choosing an answer
      if msgbody.isnumeric() and int(msgbody)<6 and int(msgbody)>0:
        message=get_answer_str(int(msgbody), session['Answers'])
        #session['Answers']=None #No longer restarts session
      else:
        message="Invalid question number.  Please enter a number between 1 and 5 or text NEW to ask another question."

    #Convert the message string to a TwiML response that is returned
    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)


if __name__ == '__main__':
    app.run()
