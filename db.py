from flask import Flask, request, jsonify 
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from models.models import db, User
from  werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/booking' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def root():
    return "Hello..!"

#   User 

@app.route("/user/insert", methods = ['POST','GET'])
def user_insert():
    data = request.get_json()
    response = {}
    password= generate_password_hash(data["password"])
    record = User(data["id"],data["user_name"],data["age"],data["mobile"],data["email"],password,data["gender"],data["addr"])
    db.session.add(record)
    db.session.commit()
    response["status"] = "Inserted Successfully"
    return response
