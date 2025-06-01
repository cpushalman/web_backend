from flask import Flask, request, jsonify, Blueprint
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import string
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import base64
from modules.db import db

import pymongo.errors


collection = db["urls"]


class BSModule:
    def __init__(self):
        self.bp = Blueprint("bs", __name__, url_prefix="/bs")
        self.register_routes()

    def generate_short_code(self):
        """Generate a random 6-character alphanumeric short code."""
        while True:
            code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
            if not collection.find_one({"shortCode": code}):
                return code
    

    def register_routes(self):
        """Register routes for the bulk shorten module."""
        def qr(payload):
            data = payload
            url = "https://api.qrcode-monkey.com//qr/custom"
            resp = requests.post(url, json=data)
            imageurl = resp.json().get("imageUrl")
            imageurl = "https:" + imageurl
            img_resp = requests.get(imageurl)
            img_base64 = base64.b64encode(img_resp.content).decode("utf-8")
            return img_base64
        

        @self.bp.route("/bulk-shorten", methods=["POST"])
        def bulk_shorten():
            # TODO CH4 change the base_url, frontend team should provide this once they decide
            # In-memory storage for URL mappings
            url_mapping = {}
            base_url = "https://short.ly/"

            """Bulk shorten URLs."""
            data = request.json
            if not data or "urls" not in data:
                return (
                    jsonify(
                        {
                            "error": 'Invalid request. Provide a list of URLs under "urls" key.'
                        }
                    ),
                    400,
                )

            urls = data["urls"]
            payloads=data.get("payloads","")
            userid=ObjectId(str(data.get("userid","")))

            if not isinstance(urls, list):
                return jsonify({"error": '"urls" should be a list.'}), 400
            # urls is a list of long urls

            shortened_urls = []
            qrRenders=[]
            
            
                
            for url,payload in zip(urls,payloads):
                if not url.startswith("http://") and not url.startswith("https://"):
                    return jsonify({"error": f"Invalid URL: {url}"}), 400
                if url in url_mapping:
                    short_code = url_mapping[url]
                else:
                    short_code = self.generate_short_code()
                    short_url=base_url + short_code
                    payload["data"]=short_url
                    print(payload["data"])
                    base64img=qr(payload)
                    print(base64img)
                    
                    
                    url_mapping[url] = short_code
                    url_mapping[short_code] = url  # Reverse mapping for retrieval

                    created_at = datetime.utcnow().isoformat()
                    expiry_date = (datetime.utcnow() + timedelta(days=90)).isoformat()
                    record = {
                        "userid":userid,
                        "shortCode": short_code,
                        "longUrl": url,
                        "createdAt": created_at,
                        "expiryDate": expiry_date,
                        "clicks": 0,
                        "impressions":0,
                        "base64img": base64img,
                        "unique_visitors_list":[],
                        "unique_visitors":0
                        
                    }
                    try:
                        collection.insert_one(record)
                    except pymongo.errors.DuplicateKeyError:
                        # If duplicate key error, generate a new short code and insert again
                        short_code = self.generate_short_code()
                        record["shortCode"] = short_code
                        collection.insert_one(record)

                shortened_urls.append(
                    {
                        "longUrl": url,
                        "shortUrl": base_url + short_code,
                        "shortCode": short_code,
                    }
                
                )
                qrRenders.append(
                    {"base64img": base64img}
                    )
            return jsonify({"shortUrls": shortened_urls,
                           "qrRenders": qrRenders})

    def get_blueprint(self):
        return self.bp
