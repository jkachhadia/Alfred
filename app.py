
import time
import os
import sys
import requests
import json
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date
from time import sleep

app=Flask(__name__)
app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

PAGE_ACCESS_TOKEN = "EAAEMH5yZAxtABAIi5RjBMuW5ttS3kgZCOIM1LM92nZBp6ZAMZCg1NPleNMmKsRfS2Jbb4FrYeXca1knaalZBLJf7UCGj3XfBCZBn5YW1w0ZBkY4zhOZASW5Uf75IMJ0P7gIkPBlfZAnv4sYLi75V4EvZC6maLgvriPfaSB1sgHYXAo1gwZDZD"
VERIFY_TOKEN = "alfred"

def short_url(url):
    post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=AIzaSyB0N1UrT-OxThltr9Lr1bb1IeCuYma-rro'
    params = json.dumps({'longUrl': url})
    response = requests.post(post_url,params,headers={'Content-Type': 'application/json'})
    response1=json.loads(response.text)
    return response1['id']

class Event(db.Model):
    __tablename__='events'
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.String(100))
    name=db.Column(db.String(100),default='event')
    date=db.Column(db.Date)
    reminded=db.Column(db.Boolean,default=False)

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
                    if "attachments" in message['message']:
                        if message['message']['attachments'][0]['type'] == "image":
                            image_url = message['message']['attachments'][0]['payload']['url']
                            short_img_url = short_url(image_url)
                            correct_url = 'http://api.havenondemand.com/1/api/async/ocrdocument/v1?apikey=d8023014-ab1d-4831-9b2f-7b9946932405&url='+short_img_url
                            ptext= requests.get(correct_url)
                            job=json.loads(ptext.text)
                            data= requests.get('http://api.havenondemand.com/1/job/result/%s?apikey=d8023014-ab1d-4831-9b2f-7b9946932405' %job['jobID'])
                            dataload=json.loads(data.text)
                            try:
                                impdata=((((dataload['actions'])[0]['result'])['text_block'])[0]['text'])
                            except KeyError:
                                pass
                            text1=requests.get('http://api.meaningcloud.com/topics-2.0?key=26f841b83b15255990e9a1cfed9a47a9&of=json&lang=en&ilang=en&txt='+impdata+'&tt=a&uw=y')
                            textp=json.loads(text1.text)
                            if textp['time_expression_list']:
                                for t in textp['time_expression_list']:
                                    rtime = ""
                                    if t['precision'] == "day" or t['precision'] == "weekday":
                                        dates = t['actual_time']
                                        rtime = dates.split('-')
                                        evedate=date(int(rtime[0]),int(rtime[1]),int(rtime[2]))
                                        nowdate = datetime.now().date()
                                        a=divmod((evedate-nowdate).days* 86400+ (evedate-nowdate).seconds , 60)
                                        if a[0]<0 :
                                            send_message(messaging_event["sender"]["id"], "Sir, you are late!")
                                        else:
                                            if textp['entity_list']:
                                                for e in textp['entity_list']:
                                                    event= e['form']
                                                    eve=Event(sender_id= messaging_event["sender"]["id"],name=event,date=date(int(rtime[0]),int(rtime[1]),int(rtime[2])))
                                            else:
                                                eve=Event(sender_id= messaging_event["sender"]["id"],date=date(int(rtime[0]),int(rtime[1]),int(rtime[2])))
                                            db.session.add(eve)
                                            db.session.commit()
                                            send_message(sender_id, "thank you sir, noted!")
                            else:
                                send_message(messaging_event["sender"]["id"], "I couldn't read that image sir?")
                    else:

                        text1=requests.get('http://api.meaningcloud.com/topics-2.0?key=26f841b83b15255990e9a1cfed9a47a9&of=json&lang=en&ilang=en&txt='+messaging_event["message"]["text"]+'&tt=a&uw=y')
                        textp=json.loads(text1.text)
                        print(textp)
                        if textp['time_expression_list']:
                            for t in textp['time_expression_list']:
                                rtime = ""
                                if t['precision'] == "day" or t['precision'] == "weekday":
                                    dates = t['actual_time']
                                    rtime = dates.split('-')
                                    evedate=date(int(rtime[0]),int(rtime[1]),int(rtime[2]))
                                    nowdate = datetime.now().date()
                                    a=divmod((evedate-nowdate).days* 86400+ (evedate-nowdate).seconds , 60)
                                    if a[0]<0 :
                                        send_message(messaging_event["sender"]["id"], "Sir, you are late!")
                                    else:
                                        if textp['entity_list']:
                                            for e in textp['entity_list']:
                                                event= e['form']
                                                eve=Event(sender_id= messaging_event["sender"]["id"],name=event,date=date(int(rtime[0]),int(rtime[1]),int(rtime[2])))
                                        else:
                                            eve=Event(sender_id= messaging_event["sender"]["id"],date=date(int(rtime[0]),int(rtime[1]),int(rtime[2])))
                                        db.session.add(eve)
                                        db.session.commit()
                                        send_message(sender_id, "thank you sir, noted!")
                        else:
                            send_message(messaging_event["sender"]["id"], "What should I remind you sir?")




                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text



                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

                all_reminders = Event.query.all()
                for i in all_reminders:
                    if i.reminded==False:
                        event_date = i.date
                                            # print event_date
                        if event_date == '':
                            continue
                        else:
                            nowdate = datetime.now().date()
                            a=divmod((event_date-nowdate).days* 86400+ (event_date-nowdate).seconds , 60)
                            if a[0]<1440 :
                                senderid = i.sender_id
                                #print i.reminprint "chutiya"
                                reminder_message = "Sir,you have a event " + i.name + " on " + str(i.date) +" that's today :)"
                                send_message(senderid, reminder_message)
                                i.reminded=True
                                db.session.add(i)
                                db.session.commit()

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


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
