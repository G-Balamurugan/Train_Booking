from flask import Flask, request, jsonify, render_template ,make_response
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from models.models import db, User
from  werkzeug.security import generate_password_hash, check_password_hash
import uuid
import json
import datetime
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/booking' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['SECRET_KEY'] = 'your secret key'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing !!'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id = data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid !!'})
        return  f(current_user, *args, **kwargs)
    return decorated


@app.route("/")
def root():
    print("Welcome Train Booking")
    return make_response("Welcome To Train Booking", 200)

#   Signup
@app.route("/user/signup", methods = ['POST','GET'])
def user_insert():
    data = request.form
    
    if not data or not data.get('user_name') or not data.get('password') or not data.get('user_type') or not data.get('email') :
        return jsonify({"status" : "Feilds missing"})

    if not data.get('first_name') or not data.get('last_name') or not data.get('dob'):
        return jsonify({"status" : "Feilds missing"})
    
    password = data.get('password')       
    user_name , email = data.get('user_name') , data.get('email')
    first_name , last_name = data.get('first_name') , data.get('last_name')
    dob = data.get('dob')
    user_type = data.get('user_type')
    
    user = User.query.filter_by(user_name = user_name).first() or  User.query.filter_by(email = email).first()
    if user:
        return jsonify({"status" : "User already exists"})

    
    password= generate_password_hash(data["password"])
    public_id = str(uuid.uuid4())
    record = User(public_id,first_name,last_name,user_name,email,dob,user_type,password)
    db.session.add(record)
    db.session.commit()
    return jsonify({"status" : "Successfully Created"})

#   Login

@app.route("/user/login" , methods = ['POST','GET'])
def login():
    data = request.form
    
    if not data or not data.get('user_name') or not data.get('password'):
        return jsonify({"status" : "Feilds missing"})
    
    user_name = data.get('user_name')
    password = data.get('password')
    
    user = User.query.filter_by(user_name = user_name).first()
    
    if not user:
        return jsonify({"status" : "User not found"})
    
    if check_password_hash(user.password, password):
        jwt_token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'],"HS256")
        
        return jsonify({"status" : "Success", "token" : jwt_token})
    else:
        return jsonify({"status" : "Wrong password"})
