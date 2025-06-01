from flask import Blueprint, request, jsonify,redirect
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
import os
from dotenv import load_dotenv
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import smtplib
from email.mime.text import MIMEText

from modules.db import db

bcrypt = Bcrypt()
def send_email(to_email,token):
        activation_link=f"https://web-backend-sdfc.onrender.com/auth/activate/{token}"
        body = f"Click to activate your account: {activation_link}"
        msg = MIMEText(body)
        msg['Subject'] = "Activate Your Account"
        msg['From'] = os.getenv("smtp_mail")
        msg['To'] = to_email
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(os.getenv("smtp_mail"), os.getenv("app_password"))
                server.send_message(msg)
        except Exception as e:
            print("Email sending failed:", e)

class AuthModule:
    def __init__(self):
        self.bp = Blueprint('auth', __name__, url_prefix='/auth')
        self.users = db["users"] 
        self.register_routes()
         # MongoDB users collection
    

    def register_routes(self):
        @self.bp.route('/register', methods=['POST'])
        def register():
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
        
            if self.users.find_one({"email": email}):
                return jsonify({"msg": "User already exists"}), 400
            token=str(uuid.uuid4())
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            user = {
                "email": email,
                "password_hash": pw_hash,
                "created_at": datetime.utcnow(),
                "isActive":False,
                "activation_token":token
            }
        
            self.users.insert_one(user)
            send_email(email,token)
            return jsonify({"msg": "Registration successfull,check you email for activation link"}), 201
        
        @self.bp.route('/login', methods=['POST'])
        def login():
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
        
            user = self.users.find_one({"email": email})

            if not user or not bcrypt.check_password_hash(
                user["password_hash"], password
            ):
                return jsonify({"msg": "Invalid credentials"}), 401
            if user["isActive"] is False:
                return jsonify({"msg": "Account not activated"}), 403


            access_token = create_access_token(identity=str(user["_id"]))
            return jsonify(access_token=access_token), 200
        @self.bp.route('/activate/<token>', methods=['GET'])
        def activate_account(token):
            user = self.users.find_one({'activation_token': token})
            if not user:
                return jsonify({"message": "Invalid or expired token"}), 400

            self.users.update_one({'_id': user['_id']}, {
        '$set': {'isActive': True},
        '$unset': {'activation_token': ""}
            })

            return redirect("https://web-frontend-five-smoky.vercel.app/login")
        @self.bp.route('/resend/<email>')
        def resend_activation(email):
            user = self.users.find_one({"email": email})
            if not user:
                return jsonify({"msg": "User not found"}), 404
            if user["isActive"]:
                return jsonify({"msg": "Account already activated"}), 400
            
            token = str(uuid.uuid4())
            self.users.update_one({"_id": user["_id"]}, {"$set": {"activation_token": token}})
            send_email(email, token)
            return jsonify({"msg": "Activation email resent"}), 200
        @self.bp.route('/userid', methods=['GET'])
        @jwt_required()
        def protected():
            user_id = get_jwt_identity()
            return jsonify({"msg": "Token is valid!", "user_id": user_id}), 200

    def get_blueprint(self):
        return self.bp
