from app import Event
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=3)
def timed_job():
    print('This job is run every three minutes.')
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

sched.start()
