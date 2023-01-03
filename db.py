from flask import Flask, request, jsonify, render_template 
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from models.models import db, User
from  werkzeug.security import generate_password_hash, check_password_hash
from Validate import Validate
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/booking' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def root():
    print("hi")
    #return render_template("Home.html")

#   Signup

@app.route("/user/signup", methods = ['POST','GET'])
def user_insert():
    #return "HI"
    data = request.get_json()
    #data = Lower.toLower(data)
    response = {}
    if Validate.json(data, ["user_name", "user_type", "email","password"]):
        if Validate.isPresent(db, User, "user_name", data["user_name"]) and Validate.isPresent(db, User,"email",data["email"]):
            password= generate_password_hash(data["password"])
            record = User(data["user_name"],data["email"],data["user_type"],password)
            db.session.add(record)
            db.session.commit()
            response["status"] = "Inserted Successfully"
        else:
            response["status"] = "Entry Already Exists..!"
    else:
        response["status"] = "Entry Fields Missing..!"
    return response

# @app.route("/user/login", methods = ['POST'])
# def passenger_insert():
#     data = request.get_json()
#     data = Lower.toLower(data)
#     response= {}
#     if Validate.json(data, ["id","user_name", "email","booking_status"]):
#         if Validate.isPresent(db, User, "id", data["id"]) and Validate.isPresent(db, User,"user_name",data["user_name"]):
#             record = User(data["id"],data["user_name"],data["email"],data["booking_status"])
#             db.session.add(record)
#             db.session.commit()
#             response["status"] = "Inserted Successfully"
#         else:
#             response["status"] = "Entry Already Exists..!"
#     else:
#         response["status"] = "Entry Fields Missing..!"
#     return response


#   Login
"""
@app.route("/user/login" , methods = ['POST','GET'])
def login():
    data = request.get_json()
    response = {}
    if Validate.json(data, ["user_name","password"]):
         """