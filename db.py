from flask import Flask, request, jsonify, render_template ,make_response
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from models.models import db, User, Train , Home , Type_Class ,Ticket, Seat_Remaining ,Ticket_Booking
from  werkzeug.security import generate_password_hash, check_password_hash
from Validate import Validate
from Duration import Duration
import uuid
import json
import jwt
from datetime import date,datetime, timedelta
from functools import wraps
from flask_cors import CORS
import random


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/booking' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['SECRET_KEY'] = 'your secret key'

jsondecoder = json.JSONDecoder()


@app.route("/", methods=['POST', 'GET'])
def root():
    print("Welcome Train Booking")
    return make_response(jsonify({'message' : "Welcome To Train Booking"}), 200)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return make_response(
            jsonify({'message' : 'Token is missing !!'}),
            401) 
        print(token)
        token = str.replace(str(token), "Bearer ", "")
        try:
            #token = jsondecoder.decode(token)
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            print(data)
            current_user = User.query.filter_by(public_id = data['public_id']).first()
            if current_user.validity == 0:
                return make_response(
                jsonify({'message' : 'User Logged Out..Need to Login'}),
                401)
            print(current_user)
        except Exception as e:
            print(".....!!!!!.... ", e)
            return make_response(
            jsonify({'message' : 'Token is invalid !!'}),
            401)
        print(token)
        return  f(current_user, *args, **kwargs)
    return decorated

#   Signup

@app.route("/user/signup", methods = ['POST','GET'])
def user_insert():
    data = request.form
    
    if not data or not data.get('username') or not data.get('password') or not data.get('userType') or not data.get('email') :
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )
    if not data.get('firstName') or not data.get('lastName') or not data.get('dob'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )

    password = data.get('password')       
    user_name , email = data.get('username') , data.get('email')
    first_name , last_name = data.get('firstName') , data.get('lastName')
    user_type = data.get('userType')
    dob = data.get('dob')

    birthdate = datetime.strptime(dob , "%Y-%m-%d")
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    print(age)
    
    user = User.query.filter_by(user_name = user_name).first() or  User.query.filter_by(email = email).first()
    if user:
        return make_response(
            jsonify({"status" : "User Already Exists"}),
            401
            )
    
    password= generate_password_hash(data["password"])
    public_id = str(uuid.uuid4())
    record = User(public_id,first_name,last_name,user_name,email,dob,age,user_type,password,0)
    db.session.add(record)
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Created"}),
            200
            )

#   Login

@app.route("/user/login" , methods = ['POST','GET'])
def login():
    data = request.form
    
    if not data or not data.get('username') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401
            )
    user_name = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(user_name = user_name).first()
    print(user,type(user))
    if not user:
        return make_response(
            jsonify({"status" : "User not found"}),
            401
            )
    
    if check_password_hash(user.password, password):
        jwt_token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.utcnow() + timedelta(minutes = 3000)
            }, app.config['SECRET_KEY'],"HS256")
        setattr(user, "validity", 1)
        db.session.commit()
        return make_response(
            jsonify({"status" : "Success", "token" : jwt_token}),
            200)
    else:
        return make_response(
            jsonify({"status" : "Wrong password"}),
            401)

#   Logout

@app.route("/logout" , methods=['POST','GET'])
@token_required
def logout(current_user):
    setattr(current_user, "validity", 0)
    db.session.commit()
    return make_response(
        jsonify({'message' : 'Logged Out'}),
        200)


#   Train 

@app.route("/train/insert" , methods=["GET","POST"])
@token_required
def train_insert(current_user):
    
    data = request.form
    
    if not data or not data.get('trainname') or not data.get('starttime') or not data.get('endtime'):
        return make_response(
        jsonify({"status" : "Feilds missing."}),
        401)    
    if not data.get('trainfrom') or not data.get('trainto') or not data.get('noofcompartment') or not data.get('ticketcompartment'):
        return make_response(
        jsonify({"status" : "Feilds missing.."}),
        401)
    if not data.get('startdate') or not data.get('enddate'):
        return make_response(
        jsonify({"status" : "Feilds missing..."}),
        401)

    train_name_chk = Train.query.filter_by(train_name = data.get('trainname')).first()
    if train_name_chk:
        return make_response(
            jsonify({"status" : "Train Already Exists..!"}),
            401)
    
    total_tickets = int(data.get('noofcompartment')) * int(data.get('ticketcompartment'))
    
    duration = Duration.duration(data.get('startdate'),data.get('enddate'),data.get('starttime'),data.get('endtime'))
    print(duration)
    
    record = Train(data.get('trainname'),data.get('starttime'),data.get('endtime'),duration,data.get('trainfrom'),data.get('trainto'),data.get('startdate'),data.get('enddate'),data.get('noofcompartment'),data.get('ticketcompartment'),total_tickets)    
    db.session.add(record)
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Created"}),
            200)

@app.route('/type_class/insert')
@token_required
def type_class_insert(current_user):
    
    data = request.form
    
    if not data or not data.get('trainname') or not data.get('trainclass') or not data.get('noofcompartment') or not data.get('noofticket') or not data.get('price'):
        return make_response(
            jsonify({"status" : "Feilds missing.."}),
            401)
    if not Validate.isPresent(db,Train,"train_name",data.get('trainname')):
        return make_response(
            jsonify({"status" : "Train Not Found.."}),
            401)
    else:
        class_chk = Type_Class.query.filter_by(train_name = data.get('trainname')).first() and Type_Class.query.filter_by(train_class = data.get('trainclass')).first()
        if class_chk:
            return make_response(
                jsonify({"status" : "Entry Already Exists.."}),
                401)
    record = Type_Class(data.get('trainname'),data.get('trainclass'),data.get('noofcompartmen'),data.get('noofticket'),data.get('price'))
    db.session.add(record)
    db.session.commit()
    
    return make_response(
            jsonify({"status" : "Successfully Inserted.."}),
            200)
    
@app.route("/seat_remaining/insert", methods = ['POST','GET'])
@token_required
def seat_remaining_insert(current_user):
    
    data = request.form
    
    if not data or not data.get('trainid') or not data.get('trainclass') or not data.get('totalclassseat') or not data.get('startseat'):
        return make_response(
            jsonify({"status" : "Feilds Missing."}),
            401)
    
    train_chk = Train.query.filter_by(id=data.get('trainid')).first()
    if not train_chk:
        return make_response(
            jsonify({"status" : "Train Not Found.."}),
            401)
    
    class_chk = Type_Class.query.filter_by(train_class=data.get('trainclass')).first()
    if not class_chk:
        return make_response(
            jsonify({"status" : "Details Did Not Match..."}),
            401)
    
    seat_chk = Seat_Remaining.query.filter_by(train_id = data.get('trainid')).first() and Seat_Remaining.query.filter_by(train_class = data.get('trainclass')).first()
    if seat_chk:
        return make_response(
            jsonify({"status" : "Entry Already Exists..!"}),
            401)    
    record = Seat_Remaining(data.get('trainid'),data.get('trainclass'),data.get('totalclassseat'),data.get('startseat'))
    db.session.add(record)
    db.session.commit()
    
    return make_response(
        jsonify({"status" : "Successfully Inserted.."}),
        200)
    
#   Home

@app.route("/user/home", methods = ['POST','GET'])
@token_required
def home(current_user):
    data = request.get_json()
    temp = {} 
    output = []
    
    if not Validate.json(data, ["trainfrom","trainto","class","type","date","trainavailable"]):
        return make_response(
            jsonify({"status" : "Fields Missing"}),
            401)
    
    record = Home(data["trainfrom"],data["trainto"],data["class"],data["type"],data["date"],data["trainavailable"]) 
    db.session.add(record)
    db.session.commit()
    
    if Validate.isPresent(db, Train, "train_from", data["trainfrom"]) and\
        Validate.isPresent(db, Train, "train_to", data["trainto"]):
        
        train_check = db.session.query(Train.start_time, Train.total_tickets,Train.start_date, Train.train_name, Train.train_from, Train.train_to, Type_Class.train_class,Type_Class.no_of_tickets).join(Type_Class,Train.train_name == Type_Class.train_name).all()
        print(train_check,type(train_check),type(train_check[0]))
        
        for i in train_check:
            if i.train_from == data["trainfrom"] and i.train_to == data["trainto"] and\
                i.train_class == data["class"] and i.start_date ==  data["date"]:
                    if (data["trainavailable"] == "yes" and i.no_of_tickets > 0) or data["trainavailable"] == "no": 
                        temp = {}
                        temp["trainname"] =i.train_name
                        temp["time"] = i.start_time
                        temp["date"] = i.start_date
                        temp["no_of_tickets"] = i.total_tickets
                        temp["trainfrom"] = i.train_from
                        temp["trainto"] = i.train_to
                        temp["class"] = i.train_class  
                        output.append(temp)
                        print(output)
        print(output)
    else:
        return make_response(
            jsonify({"status" : "Train Details Missing"}),
            401)   
    print(output)
    return output


#   Booking

@app.route("/ticket/booking", methods=['POST','GET'])
@token_required
def ticket_booking(current_user):
    
    data = request.form
    
    if not data or  not data.get('trainid') or not data.get('trainname') or not data.get('trainclass') or not data.get('tickettype') or not data.get('noofticketrequired'):
        return make_response(
            jsonify({"status" : "Feilds missing."}),
            401)
    train_id = data.get('trainid')
    train_name = data.get('trainname')
    train_class = data.get('trainclass')
    ticket_type = data.get('tickettype')
    no_of_tickets_required = data.get('noofticketrequired')
    
    user = Train.query.filter_by(train_name=train_name).first()
    if not user or user.train_name != train_name:
        return make_response(
            jsonify({"status" : "Train Not Found.."}),
            401)
        
    if not Validate.check_str_isInt(no_of_tickets_required):
        return make_response(
            jsonify({"status" : "Enter a Integer Input"}),
            401)
        
    no_of_tickets_required = int(no_of_tickets_required)
    
    if no_of_tickets_required > 6:
        return make_response(
            jsonify({"status" : "User Can Book Only in the Range 1 to 6 Tickets.."}),
            401)
    
    user_seat = Seat_Remaining.query.filter_by(train_id=train_id).first() and Seat_Remaining.query.filter_by(train_class=train_class).first()
    print()
    if not user_seat:
        return make_response(
            jsonify({"status" : "Train Details Did Not Match"})
            )
    if (user_seat.total_class_seat - user_seat.seat_start_no) < no_of_tickets_required:
        return make_response(
            jsonify({"status" : "Train Seats Not Available.."}),
            401) 
    
    user_check = User.query.filter_by(user_name = current_user.user_name).first()
    if not user_check:
        return make_response(
            jsonify({"status" : "User not found"}),
            401)
    
    current_seat_no = user_seat.seat_start_no
    
    pnr = random.randint((10**7)+1,10**8)
    pnr = int(str(pnr)+str(current_user.id))

    price_chk = Type_Class.query.filter_by(train_class = train_class).first() and Type_Class.query.filter_by(train_name = train_name).first() 
    base_price = price_chk.price 
    
    for i in range(no_of_tickets_required):
        current_seat_no = current_seat_no + 1
        if ticket_type == "general":
            price = base_price
        elif ticket_type == "":
            price = (base_price * 1.25)
        elif ticket_type == "":
            price = (base_price * 1.5)
        elif ticket_type == "":
            price = (base_price * 1.75)
        
        record = Ticket(pnr,current_user.user_name,train_id, current_seat_no,price,"Successfull")
        db.session.add(record)
        db.session.commit()
    
    setattr(user_seat, "seat_start_no", current_seat_no)
    db.session.commit()
    
    record = Ticket_Booking(train_id,train_name,train_class,ticket_type,no_of_tickets_required)
    db.session.add(record)
    db.session.commit() 
    return make_response(
        jsonify({"status" : "Successfully Inserted"}),
        200)
    
    
#   PNR CHECK

@app.route("/pnr", methods = ['POST','GET'])
@token_required
def pnr(current_user):
    data = request.get_json()
    
    if not Validate.json(data, ["pnr"]):
        return make_response(
            jsonify({"status" : "PNR Number Missing"}),
            404)
    if not Validate.isPresent(db, Ticket, "pnr" ,data["pnr"]):
        return make_response(
            jsonify({"status" : "PNR Not Found"}),
            404)
    
    temp = Ticket.query.filter_by(pnr = data["pnr"]).first()
    output = {}
    output["pnr"] = temp.pnr
    output["username"] = temp.user_name
    output["ticketstatus"] = temp.ticket_status
    
    user = Train.query.filter_by(id = temp.train_id).first()
    output["trainname"] = user.train_name
    output["trainfrom"] = user.train_from
    output["trainto"] = user.train_to
    output["time"] = user.start_time 
    output["date"] = user.start_date  
    
    return output

#   UPDATE 

@app.route("/editusername" , methods = ["POST"])
@token_required
def editname(current_user) :

    data = request.get_json()

    if not Validate.json(data,["username"]):
        return make_response(
            jsonify({"status" : "Feids Missing..!"}),
            401)
    record = User.query.filter_by(id=current_user.id).first()
    record.user_name = data["username"]

    db.session.commit()
    return jsonify({"status" : "Successfully changed"})


@app.route("/editemail" , methods = ["POST"])
@token_required
def editemail(current_user) :

    data = request.get_json()
    
    if not Validate.json(data,["email"]):
        return make_response(
            jsonify({"status" : "Feids Missing..!"}),
            401)
    
    data = request.get_json()
    record = User.query.filter_by(email=current_user.email).first()
    record.email = data["email"]

    db.session.commit()
    return jsonify({"status" : "Successfully changed"})


@app.route("/editpassword" , methods = ["POST"])
@token_required
def editpassword(current_user) :
    
    data = request.get_json()
    
    if not Validate.json(data,["password"]):
        return make_response(
            jsonify({"status" : "Feids Missing..!"}),
            401)
        
    data = request.get_json()
    record = User.query.filter_by(password=current_user.password).first()
    record.password = generate_password_hash(data["password"])

    db.session.commit()
    return jsonify({"status" : "Successfully changed"})