from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient
from datetime import datetime
from user_agents import parse
import json

app=Flask(__name__)

client=MongoClient('mongodb://localhost:27017/')
db=client['shortly']
collection=db['urls']

@app.route('/<short>')
def get_info_and_redirect(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "URL not found",404
    #Getting the data of a click
    now=datetime.utcnow()
    user_agent=parse(request.user_agent.string)
    if request.headers.get('X-Forwarded-For'):
        ip_address = request.headers.get('X-Forwarded-For').split(',')[0]#first ip in the list
    else:
        ip_address = request.remote_addr
    click_data = {
        "time": now.strftime("%H:%M:%S"),
        "date": now.day,
        "month": now.strftime("%B"),
        "year": now.year,
        "day": now.strftime("%A"),
        "device": user_agent.device.family,
        "os": user_agent.os.family,
        "browser": user_agent.browser.family,
        "ip": ip_address
    }
    #Getting unique visitors
    ip_list = [click["ip"] for click in url.get("clicks",[])]
    if ip_address not in ip_list:
        collection.update_one(
            {"shortCode": short},
            {"$inc": {"unique_visitors": 1}},
            upsert=True 
        ) 
    #Updating MongoDB
    collection.update_one(
        {"shortCode": short},
        {"$push": {"clicks": click_data}}  
    )
    
    return redirect(url['original_url'])

#Getting impressions for ctr
@app.route('/impression/<short>')
def count_impression(short):
    collection.update_one(
        {"shortCode": short},
        {"$inc": {"impressions": 1}}, 
        upsert=True 
    )
    return "Impression counted", 200

#Diplaying ctr
@app.route('/ctr/<short>')
def getctr(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "short code not found"
    if "clicks" not in url:
        return "No clicks yet"
    if "impressions" not in url:
        return "No impressions yet"
    clicks=len(url['clicks'])
    impressions=url['impressions']
    ctr=clicks/impressions
    display={"shortCode": short, "ctr": ctr, "totalImpressions": impressions, "clicks": clicks}
    pretty_json = json.dumps(display, indent=4)  #pretty printing
    return pretty_json

#Displaying analytics
@app.route('/analytics/<short>')
def get_analytics(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "Short code does not exist", 404
    clicks=len(url['clicks'])
    device={}
    os={}
    browser={}
    for click in url['clicks']:
        if click['device'] not in device:
            device[click['device']]=1
        else:
            device[click['device']]+=1
        if click['os'] not in os:
            os[click['os']]=1
        else:
            os[click['os']]+=1
        if click['browser'] not in browser:
            browser[click['browser']]=1
        else:
            browser[click['browser']]+=1

    display={"shortCode": short, "totalClicks": clicks, "uniqueVisitors": url.get('unique_visitors',0), "deviceDistribution": device, "osDistribution": os, "browserDistribution": browser}
    pretty_json = json.dumps(display, indent=4)  #pretty printing
    return pretty_json

if __name__=='__main__':
    app.run(debug=True)
