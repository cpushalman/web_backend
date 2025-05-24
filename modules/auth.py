from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import os
from dotenv import load_dotenv

from modules.db import db

bcrypt = Bcrypt()
auth = Blueprint('auth', __name__)
class AuthModule:
    def __init__(self):
        self.bp = Blueprint('auth', __name__, url_prefix='/auth')
        self.register_routes()
        users = db["users"]  # MongoDB users collection
        
       @self.bp.route('/register', methods=['POST'])
        def register():
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
        
            if users.find_one({"email": email}):
                return jsonify({"msg": "User already exists"}), 400
        
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user = {
                "email": email,
                "password_hash": pw_hash,
                "created_at": datetime.utcnow()
            }
        
            users.insert_one(user)
            return jsonify({"msg": "User created successfully"}), 201
        
        @self.bp.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
        
            user = users.find_one({"email": email})
            if not user or not bcrypt.check_password_hash(user["password_hash"], password):
                return jsonify({"msg": "Invalid credentials"}), 401

            access_token = create_access_token(identity=str(user["_id"]))
            return jsonify(access_token=access_token), 200

        def get_blueprint(self):
            return self.bp
