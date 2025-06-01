from flask import Flask, request, jsonify, redirect, Response
from pymongo import MongoClient
from datetime import datetime, timedelta
from flask import Blueprint
import os
from flask_cors import CORS
import requests
import base64
from dotenv import load_dotenv
from bson.objectid import ObjectId
from random import choices
import string

load_dotenv()
from modules.db import db


collection = db["urls"]
collection.create_index("shortCode", unique=True)
history= db["shortcode"]
history.create_index("shortCode", unique=True)


class ShortenModule:
    def __init__(self):
        self.bp = Blueprint("shorten", __name__, url_prefix="/shorten")
        CORS(self.bp)
        self.register_routes()

    def register_routes(self):
        # Generate a short code
        def generate_short_code():
            from random import choices
            import string

            short_code = "".join(choices(string.ascii_letters + string.digits, k=6))
            if not collection.find_one({"shortCode": short_code}):
                return short_code
            else:
                return generate_short_code()

        def qr(payload):
            data = payload
            url = "https://api.qrcode-monkey.com//qr/custom"
            resp = requests.post(url, json=data)
            imageurl = resp.json().get("imageUrl")
            imageurl = "https:" + imageurl
            img_resp = requests.get(imageurl)
            img_base64 = base64.b64encode(img_resp.content).decode("utf-8")
            return img_base64

        @self.bp.route("/shorten", methods=["POST"])
        def shorten_url():
            data = request.json
            long_url = data.get('longUrl')
            qrRender=data.get('qrRender')
            userid=data.get('userid')
            userid=ObjectId(str(userid))
            custom_alias = data.get("customAlias")

            if not long_url:
                return jsonify({"error": "Long URL is required"}), 400

            if custom_alias:
                if collection.find_one({"shortCode": custom_alias}):
                    return jsonify({"error": "Custom alias already in use."}), 400
                else:
                    short_code = custom_alias
            else:
                short_code = generate_short_code()  # Fixed variable usage

            created_at = datetime.utcnow().isoformat()
            expiry_date = (datetime.utcnow() + timedelta(days=90)).isoformat()
            short_url = f"https://short.ly/{short_code}"
            if not isinstance(qrRender, dict):
                qrRender = {}
            qrRender["data"] = short_url
            try:
                base64img = qr(qrRender)

            except Exception as e:
                return (
                    jsonify({"error": "QR code generation failed", "details": str(e)}),
                    500,
                )
            record = {
                "userid":userid,
                "shortCode": short_code,
                "longUrl": long_url,
                "createdAt": created_at,
                "expiryDate": expiry_date,
                "clicks": 0,
                "impressions": 0,
                "base64img": base64img,
            }
            try:

                collection.insert_one(record)
                history.insert_one({"userid":userid,"shortCode": short_code})
                return (
                    jsonify(
                        {
                            "shortUrl": short_url,
                            "shortCode": short_code,
                            "longUrl": long_url,
                            "createdAt": record["createdAt"],
                            "expiryDate": record["expiryDate"],
                            "base64img": base64img,
                        }
                    ),
                    201,
                )
            except Exception as e:
                return (
                    jsonify({"error": "Database insert failed", "details": str(e)}),
                    500,
                )

    def get_blueprint(self):
        return self.bp
