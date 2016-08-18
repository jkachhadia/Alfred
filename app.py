
import time
import os
import sys
import requests
import json
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
import datetime
import time
from datetime import date


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
    date=db.Column(db.DateTime)
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
                    if "attachments" in messaging_event['message']:
                        if messaging_event['message']['attachments'][0]['type'] == "image":
                            image_url = messaging_event['message']['attachments'][0]['payload']['url']
                            b=0
                            c=0
                            d=0
                            short_img_url = short_url(image_url)
                            correct_url = 'http://api.havenondemand.com/1/api/async/ocrdocument/v1?apikey=d8023014-ab1d-4831-9b2f-7b9946932405&url='+short_img_url
                            ptext= requests.get(correct_url)
                            job=json.loads(ptext.text)
                            data= requests.get('http://api.havenondemand.com/1/job/result/%s?apikey=d8023014-ab1d-4831-9b2f-7b9946932405' %job['jobID'])
                            dataload=json.loads(data.text)
                            try:
                                if ((((dataload['actions'])[0]['result'])['text_block'])[0]['text']):
                                    impdata=((((dataload['actions'])[0]['result'])['text_block'])[0]['text'])
                                    text1=requests.get('http://api.meaningcloud.com/topics-2.0?key=26f841b83b15255990e9a1cfed9a47a9&of=json&lang=en&ilang=en&txt='+impdata+'&tt=a&uw=y')
                                    textp=json.loads(text1.text)
                                    print(textp)
                                    if textp['time_expression_list']:
                                        for t in textp['time_expression_list']:
                                            if (t['precision'] == "day" or t['precision'] == "weekday") and b==0:
                                                dates = t['actual_time']
                                                rtime = dates.split('-')
                                                evedate=date(int(rtime[0]),int(rtime[1]),int(rtime[2]))
                                                nowdate = datetime.datetime.now().date()
                                                a=divmod((evedate-nowdate).days* 86400+ (evedate-nowdate).seconds , 60)
                                                if a[0]<0 :
                                                    send_message(messaging_event["sender"]["id"], "Sir, you are late!")
                                                    d=1
                                                else:
                                                    b=1

                                            if (t['precision']=='minutesAMPM' or t['precision']=='hourAMPM') and c==0:
                                                times=t['actual_time']
                                                times=times.split(' ')
                                                times=times[0].split(':')
                                                c=1




                                        if b==1 and c==1:
                                            eve=Event(sender_id= messaging_event["sender"]["id"],date=datetime.datetime(int(rtime[0]),int(rtime[1]),int(rtime[2]),int(times[0]),int(times[1]),int(times[2])))
                                            db.session.add(eve)
                                            db.session.commit()
                                            send_message(messaging_event["sender"]["id"], "thank you sir, noted!")
                                        elif b==0 and c==1 and d!=1:
                                            send_message(messaging_event["sender"]["id"], "I can't read date sir! Can you tell me the date and name of event?")
                                        elif b==1 and c==0:
                                            eve=Event(sender_id= messaging_event["sender"]["id"],date=datetime.datetime(int(rtime[0]),int(rtime[1]),int(rtime[2]),2,0,0))
                                            db.session.add(eve)
                                            db.session.commit()
                                            send_message(messaging_event["sender"]["id"], "thank you sir, noted!")

                                    else:
                                        send_message(messaging_event["sender"]["id"], "I have grown old! I can't read your image sir. sorry :( Can you tell me the date and name of event?")
                            except IndexError:
                                send_message(messaging_event["sender"]["id"],"I have grown old! I can't read your image sir. sorry :( Can you tell me the date and name of event?")
                    else:

                        text1=requests.get('http://api.meaningcloud.com/topics-2.0?key=26f841b83b15255990e9a1cfed9a47a9&of=json&lang=en&ilang=en&txt='+messaging_event["message"]["text"]+'&tt=a&uw=y')
                        textp=json.loads(text1.text)
                        print(textp)
                        b=0
                        c=0
                        d=0
                        if textp['time_expression_list']:
                            for t in textp['time_expression_list']:

                                if ((t['precision'] == "day") or (t['precision'] == "weekday")) and b==0:
                                    dates = t['actual_time']
                                    rtime = dates.split('-')
                                    evedate=date(int(rtime[0]),int(rtime[1]),int(rtime[2]))
                                    nowdate = datetime.datetime.now().date()
                                    a=divmod((evedate-nowdate).days* 86400+ (evedate-nowdate).seconds , 60)
                                    if a[0]<0 :
                                        send_message(messaging_event["sender"]["id"], "Sir, you are late!")
                                        d=1
                                    else:
                                        b=1

                                if ((t['precision']=='minutesAMPM') or (t['precision']=='hourAMPM')) and c==0:
                                    times=t['actual_time']
                                    times=times.split(' ')
                                    times=times[0].split(':')
                                    c=1

                            if textp['entity_list']:
                                for e in textp['entity_list']:
                                    event= e['form']
                                    if b==1 and c==1:
                                        eve=Event(sender_id= messaging_event["sender"]["id"],name=event,date=datetime.datetime(int(rtime[0]),int(rtime[1]),int(rtime[2]),int(times[0]),int(times[1]),int(times[2])))
                                        db.session.add(eve)
                                        db.session.commit()
                                        send_message(messaging_event["sender"]["id"], "thank you sir, noted!")
                                    elif b==0 and c==1 and d!=1:
                                        send_message(messaging_event["sender"]["id"], "Sir, please mention today if it's today's reminder!")
                                    elif b==1 and c==0:
                                        eve=Event(sender_id= messaging_event["sender"]["id"],name=event,date=datetime.datetime(int(rtime[0]),int(rtime[1]),int(rtime[2]),2,0,0))
                                        db.session.add(eve)
                                        db.session.commit()
                                        send_message(messaging_event["sender"]["id"], "thank you sir, noted!")


                            else:
                                if b==1 and c==1:
                                    eve=Event(sender_id= messaging_event["sender"]["id"],date=datetime.datetime(int(rtime[0]),int(rtime[1]),int(rtime[2]),int(times[0]),int(times[1]),int(times[2])))
                                    db.session.add(eve)
                                    print('hello')
                                    db.session.commit()
                                    send_message(messaging_event["sender"]["id"], "thank you sir, noted!")
                                elif b==0 and c==1 and d!=1:
                                    send_message(messaging_event["sender"]["id"], "Sir, please mention today if it's today's reminder!")
                                elif b==1 and c==0:
                                    eve=Event(sender_id= messaging_event["sender"]["id"],date=datetime.datetime(int(rtime[0]),int(rtime[1]),int(rtime[2]),2,0,0))
                                    db.session.add(eve)
                                    db.session.commit()
                                    send_message(messaging_event["sender"]["id"], "thank you sir, noted!")
                        else:
                            send_message(messaging_event["sender"]["id"], "What should I remind you sir?")







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
                        nowdate = datetime.datetime.today()
                        e=divmod((event_date-nowdate).days* 86400+ (event_date-nowdate).seconds , 60)
                        if (e[0]<450) and (e[0]>330) :
                            timeleft= (e[0]-330)/60.0
                            hr=timeleft-(timeleft%1)
                            mi=round((timeleft%1)*60,0)
                            senderid = i.sender_id
                            reminder_message = "Sir, you have a " + i.name + " after "+str(hr)+" hours and "+str(mi)+" minutes!"
                            send_message(senderid, reminder_message)
                            i.reminded=True
                            db.session.add(i)
                            db.session.commit()
                        elif e[0]<330:
                            i.reminded=True
                            send_message(i.sender_id,"sir, your "+ i.name +" is over already!")
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
