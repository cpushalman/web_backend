from flask import Flask, request, redirect, jsonify
from pymongo import MongoClient
from datetime import datetime
from user_agents import parse
import json
import requests
from collections import Counter

app=Flask(__name__)
from flask import Blueprint
app_sub = Blueprint('app_sub', __name__, url_prefix='/sub')


MONGO_URI="mongodb+srv://apk:curious-champ@cluster0.dpdv9hr.mongodb.net/"
client=MongoClient(MONGO_URI)
db=client['shortly']
collection=db['urls']

#location from ip address
def get_location(ip):
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url).json()

    return {
        "country": response.get("country", "Unknown"),
        "region": response.get("regionName", "Unknown"),
        "city": response.get("city", "Unknown")
    }

@app_sub.route('/<short>')
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
    
    location_data = get_location(ip_address)
    click_data = {
        "time": now.strftime("%H:%M:%S"),
        "date": now.day,
        "month": now.strftime("%B"),
        "year": now.year,
        "day": now.strftime("%A"),
        "device": user_agent.device.family,
        "os": user_agent.os.family,
        "browser": user_agent.browser.family,
        "ip": ip_address,
        "country": location_data["country"],
        "region": location_data["region"],
        "city": location_data["city"]
    }
    #Getting unique visitors
    collection.update_one(
        {"shortCode": short, "clicks.ip": {"$ne": ip_address}},  #Checking if IP does not already exist
        {"$inc": {"unique_visitors": 1}},
        upsert=True
    )

    #Updating MongoDB
    collection.update_one(
        {"shortCode": short},
        {"$push": {"click_data": click_data}}  
    )
    
    return redirect(url['longUrl'])

#Getting impressions for ctr
@app_sub.route('/impression/<short>')
def count_impression(short):
    collection.update_one(
        {"shortCode": short},
        {"$inc": {"impressions": 1}}, 
        upsert=True 
    )
    return "Impression counted", 200

#Diplaying ctr
@app_sub.route('/ctr/<short>')
def getctr(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "short code not found"
    if "click_data" not in url:
        return "No clicks yet"
    if "impressions" not in url:
        return "No impressions yet"
    clicks=len(url['click_data'])
    impressions=url['impressions']
    ctr=clicks/impressions
    display={"shortCode": short, "ctr": ctr, "totalImpressions": impressions, "clicks": clicks}
    pretty_json = json.dumps(display, indent=4)  #pretty printing
    return pretty_json

#Displaying analytics
@app_sub.route('/analytics/<short>')
def get_analytics(short):
    url=collection.find_one({'shortCode':short})
    if not url:
        return "Short code does not exist", 404
    clicks=len(url['click_data'])
    
    device = Counter(click['device'] for click in url['click_data'])
    os = Counter(click['os'] for click in url['click_data'])
    browser = Counter(click['browser'] for click in url['click_data'])

    display={"shortCode": short, "totalClicks": clicks, "uniqueVisitors": url.get('unique_visitors',0), "deviceDistribution": device, "osDistribution": os, "browserDistribution": browser}
    pretty_json = json.dumps(display, indent=4)  #pretty printing
    return pretty_json

if __name__=='__main__':
    app.run(debug=True)
