
import time
import os
import sys
import requests
import json
from flask import Flask,request, render_template
from pymongo import MongoClient
import datetime
from datetime import date
import apiai
def main(query,sessionid):
    ai = apiai.ApiAI('13537e5537c543b78b713852b76ff0f3 ')

    request = ai.text_request()

    request.lang = 'en'  # optional, default value equal 'en'

    request.session_id = sessionid

    request.query = query

    response = request.getresponse()
    response=json.loads(response.read())
    print(response)

    send_message(sessionid, response['result']['fulfillment']['speech'])

app=Flask(__name__)
CONNECTION = 'mongodb://sumedh:sumedh@ds145158.mlab.com:45158/alfred'
client = MongoClient(CONNECTION)
db = client.alfred
app.config.from_pyfile('app.cfg')

PAGE_ACCESS_TOKEN = "EAAYUNKfFZCuABAGVZBWod8KemrBFFcGZBgtNVhM4i90jaU1SlEh6iemDlJddfq8vhXLDZAqMkQytKZBtgnlE1DJ1R3dBQsAphDT3TdV8lAeHadYzwX056X2kseO8vzxH1h3YMo6AEfgak6r9MOcdbhlidAupLUEdgKtg3NGBHAgZDZD"
VERIFY_TOKEN = "alfred-svnit"

def short_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB0N1UrT-OxThltr9Lr1bb1IeCuYma-rro'
    params = json.dumps({'longUrl': url})
    response = requests.post(post_url,params,headers={'Content-Type': 'application/json'})
    response1=json.loads(response.text)
    return response1['id']

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments

    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200

@app.route('/', methods=['POST'])
def webook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    print 'Got message'
                    currentuser = db.user.find_one({ 'user_id' : messaging_event["sender"]["id"] })
                    if currentuser is None :
                        print 'User not found'
                        db.user.insert_one({ "user_id" : messaging_event["sender"]["id"], "adm_no" : 0 })
                        print 'inserted'
                        send_message(messaging_event["sender"]["id"], "Can I know your roll no??")
                    elif currentuser and currentuser["adm_no"] == 0 and messaging_event["sender"]["id"] != 1851054981802215:
                        db.user.update({"_id" : currentuser["_id"]} ,{"adm_no" : str.lower(str(messaging_event["message"]["text"])), "user_id" : messaging_event["sender"]["id"]}, upsert = False)
                        send_message(messaging_event["sender"]["id"], 'You are now part of alfred SVNIT notification system.')
                    else:
                        print messaging_event["message"]["text"]
                        main(messaging_event["message"]["text"],messaging_event["sender"]["id"])

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass
                if messaging_event.get("optin"):  # optin confirmation
                    pass
                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200




def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

@app.route('/sent', methods = ['GET', 'POST'])
def mass():
    print 'received'
    users = db.user
    notification = str(request.form.get('notification'))
    branchDropdown = str(request.form.get('dropdown-branch'))
    print branchDropdown
    yearDropdown = str(request.form.get('dropdown-year'))
    if branchDropdown != 'all' and yearDropdown != 'all':
        for u in users.find():
            # print u
            if str.lower(branchDropdown) in u["adm_no"]:
                if yearDropdown in u["adm_no"]:
                    send_message(int(u["user_id"]), notification)
                    return "Notification sent successfully", 200
    if branchDropdown != 'all' and yearDropdown == 'all':
        for u in users.find():
            if branchDropdown in u["adm_no"]:
                send_message(int(u["user_id"]), notification)
                return "Notification sent successfully", 200

    if branchDropdown == 'all' and yearDropdown != 'all':
        for u in user.find():
            if yearDropdown in u["adm_no"]:
                send_message(int(u["user_id"]), notification)
                return 'Notification sent successfully', 200
    if branchDropdown == 'all' and yearDropdown == 'all':
        for u in users.find():
            send_message(int(u["user_id"]), notification)
            return 'Notification sent successfully', 200

@app.route('/sendNotification', methods = ['GET', 'POST'])
def send():
    return render_template('index.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)