from flask import Blueprint, request
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['shortly']
collection = db['urls']


class AdminModule:
    def __init__(self):
        self.bp = Blueprint('admin', __name__, url_prefix='/admin')
        self.register_routes()
    def register_routes(self):
        @self.bp.route('/delete', methods=['DELETE'])
        def delete_short_url():
            data = request.json
            if not data:
                return 'No data provided', 400

        

            short_code = data.get('shortCode')
            if not short_code:
                return 'No short URL code provided', 400

            result = collection.delete_one({'shortCode': short_code})
            if result.deleted_count == 0:
                return 'Short URL not found in the database', 404

            return 'Short URL deleted successfully', 200

        @self.bp.route('/update/expiry', methods=['PATCH'])
        def update_expiry():
            data = request.json
            if not data:
                return 'No data provided', 400

            short_code = data.get('shortCode')
            expiration = data.get('expiryDate')

            # Validate input
            if not short_code:
                return 'No short URL code provided', 400
            if not expiration:
                return 'No expiration date provided', 400

            try:
                #Parse and validate the expiration date
                # Assuming the expiration date is in ISO 8601 format (YYYY-MM-DD)
                # You can adjust the format as per your requirement
                new_expiration_date = datetime.fromisoformat(expiration).isoformat()
            except ValueError:
                return 'Invalid expiration date format. Use ISO 8601 format (YYYY-MM-DD).', 400

            existing_entry = collection.find_one({'shortCode': short_code})
            if not existing_entry:
                return 'Short URL not found in the database', 404

            # Check if the current expiration date is still valid
            current_expiration = existing_entry.get('expiryDate')
            if current_expiration:
                try:
                    current_expiration_date = datetime.fromisoformat(current_expiration)
                except ValueError:
                    return 'Invalid current expiration date format in the database.', 500

                if current_expiration_date > datetime.now():
                        return 'The current expiration date is still valid.', 200

            result = collection.update_one(
                {'shortCode': short_code},
                {'$set': {'expiryDate': new_expiration_date}}
            )   

            if result.matched_count == 0:
                return 'Short URL not found in the database', 404

            return 'Expiration date updated successfully', 200

    def get_blueprint(self):
        return self.bp

