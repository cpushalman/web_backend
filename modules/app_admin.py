from flask import Blueprint, request,jsonify
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from dateutil.parser import parse
from modules.db import db

collection = db["urls"]


class AdminModule:
    def __init__(self):
        self.bp = Blueprint("admin", __name__, url_prefix="/admin")
        self.register_routes()

    def register_routes(self):
        @self.bp.route("/delete", methods=["DELETE"])
        def delete_short_url():
            data = request.json
            if not data:
                return "No data provided", 400

            short_code = data.get("shortCode")
            if not short_code:
                return "No short URL code provided", 400

            result = collection.delete_one({"shortCode": short_code})
            if result.deleted_count == 0:
                return "Short URL not found in the database", 404

            return "Short URL deleted successfully", 200

        @self.bp.route("/update/expiry", methods=["PATCH"])
        def update_expiry():
            try:
                data = request.json
                if not data:
                    return "No data provided", 400

                short_code = data.get("shortCode")
                expiration = data.get("expiryDate")

                # Validate input
                if not short_code:
                    return "No short URL code provided", 400
                if not expiration:
                    return "No expiration date provided", 400

                try:
                    # Parse and validate the expiration date
                    new_expiration_date = parse(expiration).isoformat()
                except ValueError:
                    return (
                        "Invalid expiration date format. Use ISO 8601 format (YYYY-MM-DD).",
                        400,
                    )

                # Fetch the existing entry from the database
                try:
                    existing_entry = collection.find_one({"shortCode": short_code})
                except Exception as e:
                    return f"Database error: {e}", 500

                if not existing_entry:
                    return "Short URL not found in the database", 404

                # Check if the current expiration date exists and is a string
                current_expiration = existing_entry.get("expiryDate")
                if current_expiration:
                    try:
                        # Ensure the value is a string before parsing
                        if not isinstance(current_expiration, str):
                            print(
                                f"Invalid type for expiryDate: {type(current_expiration)}"
                            )
                            return (
                                "Invalid current expiration date format in the database.",
                                500,
                            )

                        # Parse the expiration date using dateutil.parser.parse
                        current_expiration_date = parse(current_expiration)
                        print(f"Parsed expiration date: {current_expiration_date}")

                        # Ensure both dates are timezone-aware for comparison
                        now = datetime.now(
                            current_expiration_date.tzinfo
                        )  # Use the same timezone as the parsed date
                        print(f"Current datetime: {now}")

                        if current_expiration_date < now:
                            return "The current expiration date is still valid.", 200
                    except Exception as e:
                        print(f"Error while parsing expiryDate: {e}")
                        return (
                            "Invalid current expiration date format in the database.",
                            500,
                        )
                else:
                    return "No expiration date found in the database.", 404

                # Update the expiration date in the database
                try:
                    result = collection.update_one(
                        {"shortCode": short_code, "expiryDate": current_expiration},
                        {"$set": {"expiryDate": new_expiration_date}},
                    )
                except Exception as e:
                    return f"Database error: {e}", 500

                if result.matched_count == 0:
                    return "Short URL not found in the database", 404

                return "Expiration date updated successfully", 200

            except Exception as e:
                return f'Internal server error: {e}', 500
        @self.bp.route('/recent',methods=['POST'])
        def recent():
            data = request.json
            userid = data.get("userid")
            userid = ObjectId(str(userid))

            url = collection.find_one({"userid": userid}, sort=[("_id", -1)])

            if not url:
                return jsonify({"error": "No records found"}), 404

            # Remove _id from the result before returning
            
            # Remove any other non-serializable fields if needed

            # Optionally, filter/format the response to only include desired fields
            url.pop("_id", None)  # Remove _id field
            url.pop("userid", None)  # Remove userid field
            return jsonify(url), 200
        @self.bp.route('/all',methods=['POST'])
        def all():
            data=request.json
            userid=data.get("userid")
            userid=ObjectId(str(userid))

            urls = collection.find({"userid": userid})
            all_urls = []
            for url in urls:
                all_urls.append({
                    "base64img":url.get("base64img",""),
                    "shortCode": url.get("shortCode", ""),
                    "longUrl": url.get("longUrl", ""),
                    "createdAt": url.get("createdAt", ""),
                    "expiryDate": url.get("expiryDate", ""),
                    "clicks": url.get("clicks", 0)
                })
            return jsonify(all_urls), 200


    def get_blueprint(self):
        return self.bp
