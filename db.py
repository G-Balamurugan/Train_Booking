from flask import Flask, request, jsonify, render_template ,make_response
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from models.models import db, User, Train , Home , Type_Class ,Ticket, Seat_Remaining ,Ticket_Booking ,Cancel_Ticket
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
    
    if not data or not data.get('trainname') or not data.get('trainclass') or not data.get('noofcompartment') or not data.get('price'):
        return make_response(
            jsonify({"status" : "Feilds missing.."}),
            401)
    if not Validate.isPresent(db,Train,"train_name",data.get('trainname')):
        return make_response(
            jsonify({"status" : "Train Not Found.."}),
            401)
    else:
        class_chk = Type_Class.query.filter_by(train_name = data.get('trainname')).filter_by(train_class = data.get('trainclass')).first()
        if class_chk:
            return make_response(
                jsonify({"status" : "Entry Already Exists.."}),
                401)
        else:
            compartment_chk = Type_Class.query.filter_by(train_name = data.get('trainname')).all()
            total_compartment = 0
            if compartment_chk:
                for i in compartment_chk:
                    total_compartment = total_compartment + i.no_of_compartment
                train_chk = Train.query.filter_by(train_name = data.get('trainname')).first()
                if total_compartment + int(data.get('noofcompartment')) > train_chk.no_of_compartment:
                    return make_response(jsonify({"status" : "Train Compartment Full...Can't Allocate"}),401)
    
    record = Type_Class(data.get('trainname'),data.get('trainclass'),data.get('noofcompartment'),data.get('price'))
    db.session.add(record)
    db.session.commit()
    
    return make_response(
            jsonify({"status" : "Successfully Inserted.."}),
            200)
    
@app.route("/seat_remaining/insert", methods = ['POST','GET'])
@token_required
def seat_remaining_insert(current_user):
    
    data = request.form
    
    if not data or not data.get('trainid') or not data.get('trainclass') or not data.get('startseat'):
        return make_response(
            jsonify({"status" : "Feilds Missing."}),
            401)
    
    train_chk = Train.query.filter_by(id=data.get('trainid')).first()
    if not train_chk:
        return make_response(
            jsonify({"status" : "Train Not Found.."}),
            401)
    
    class_chk = Type_Class.query.filter_by(train_class=data.get('trainclass')).filter_by(train_name=train_chk.train_name).first()
    if not class_chk:
        return make_response(
            jsonify({"status" : "Details Did Not Match..."}),
            401)
    
    total_class_seat = train_chk.no_of_tickets_compartment * class_chk.no_of_compartment
    
    seat_chk = Seat_Remaining.query.filter_by(train_id = data.get('trainid')).filter_by(train_class = data.get('trainclass')).first()
    if seat_chk:
        return make_response(
            jsonify({"status" : "Entry Already Exists..!"}),
            401)    
    record = Seat_Remaining(data.get('trainid'),data.get('trainclass'),total_class_seat,data.get('startseat'))
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
    
    if not Validate.isPresent(db,Type_Class,"train_class",data["class"]) and data["class"]!="all class":
        return make_response(jsonify({"status" : "Class Not Found.."}),401)
    
    if Validate.isPresent(db, Train, "train_from", data["trainfrom"]) and\
        Validate.isPresent(db, Train, "train_to", data["trainto"]):

        train_extract = Train.query.filter_by(train_from = data["trainfrom"]).all() and Train.query.filter_by(train_to = data["trainto"]).all() and Train.query.filter_by(start_date = data["date"]).all()
        
        train_list=[]
        
        for i in train_extract:
            print("///////////",i.train_name)
            train_class_list = []    
            if data["class"] == "all class":
                all_class_extract = Type_Class.query.filter_by(train_name=i.train_name).all()
                for j in all_class_extract:
                    train_class_list.append(j.train_class)
            else:
                class_chk = Type_Class.query.filter_by(train_name=i.train_name).filter_by(train_class=data["class"]).first()
                if class_chk:
                    train_class_list.append(data["class"])
            print(train_class_list)
            seat_dict = {}
            for j in train_class_list:
                seat_available_chk = Seat_Remaining.query.filter_by(train_id=i.id).filter_by(train_class=j).first()
                if seat_available_chk:
                    seat_dict[j] = seat_available_chk.total_class_seat - seat_available_chk.seat_start_no
                else:
                    continue  
                print("!... ",seat_dict)
            temp={}
            if seat_dict:
                temp[i.id]=seat_dict
            
            if temp and temp not in train_list:
                train_list.append(temp) 
        print("....! ",train_list)
        
        final_list = []
        for i in train_list:
            for l in i.keys():
                print(l)
                temp = {}
                train_query = Train.query.filter_by(id=l).first()
                temp["trainname"] =train_query.train_name
                temp["trainid"] = train_query.id
                #temp["duration"] = train.duration
                temp["starttime"] = train_query.start_time
                temp["startdate"] = train_query.start_date
                temp["class"] = train_list
                #temp["no_of_tickets"] = train_query.total_tickets
                temp["trainfrom"] = train_query.train_from
                temp["trainto"] = train_query.train_to
                temp["enddate"] = train_query.end_date
                temp["endtime"] = train_query.end_time
                final_list.append(temp)
        return final_list
        

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
    print(user.id)

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
    
    user_seat = Seat_Remaining.query.filter_by(train_id=data.get('trainid')).filter_by(train_class=train_class).first()
    print(user_seat.train_id, user_seat.train_class)
    if not user_seat:
        return make_response(
            jsonify({"status" : "Train Details Did Not Match"}),401)
    
    ticket_pending = 0 
    ticket_cancel_chk = Cancel_Ticket.query.filter_by(train_id=data.get('trainid')).filter_by(train_class=data.get('trainclass')).all()
    flag_pending_ticket = 0 

    for d in ticket_cancel_chk:
        ticket_pending = ticket_pending + 1
            
    if (user_seat.total_class_seat - user_seat.seat_start_no) < no_of_tickets_required:
        flag_pending_ticket = 1

        if not ticket_cancel_chk or ticket_pending < no_of_tickets_required:
            return make_response(
                jsonify({"status" : "Train Seats Not Available.."}),
                401) 

    user_check = User.query.filter_by(user_name = current_user.user_name).first()
    if not user_check:
        return make_response(
            jsonify({"status" : "User not found"}),
            401)
    
    pnr = random.randint((10**7)+1,10**8)
    pnr = int(str(pnr)+str(current_user.id))

    price_chk = Type_Class.query.filter_by(train_class = train_class).first() and Type_Class.query.filter_by(train_name = train_name).first() 
    base_price = price_chk.price 
    
    current_seat_no = user_seat.seat_start_no
    
    for i in range(no_of_tickets_required):
        current_seat_no = current_seat_no + 1
        if ticket_type == "general":
            price = base_price
        elif ticket_type == "ladies":
            price = (base_price * 1.25)
        elif ticket_type == "tatkal":
            price = (base_price * 1.5)
        elif ticket_type == "premium tatkal":
            price = (base_price * 1.75)
            
        record = Ticket(pnr,current_user.user_name,train_id, current_seat_no, train_class, ticket_type ,price,"Successfull")
        db.session.add(record)
        db.session.commit()
    
    setattr(user_seat, "seat_start_no", current_seat_no)
    db.session.commit()
    
    record = Ticket_Booking(train_id,train_name,train_class,ticket_type,no_of_tickets_required)
    db.session.add(record)
    db.session.commit() 
    return make_response(
        jsonify({"status" : "Ticket Booked Successfully"}),
        200)
    
@app.route("/booking/cancel", methods=['POST','GET'])
@token_required
def booking_cancel(current_user):
    data = request.form
    
    if not data or not data.get('trainid') or not data.get('seatno') or not data.get('class'):
        return make_response(jsonify({"status" : "Train Details Missing..!"}),401)
    
    seat_cancel_chk = Ticket.query.filter_by(train_id=data.get('trainid')).filter_by(user_name=current_user.user_name).filter_by(seat_no=data.get('seatno')).first()
    if not seat_cancel_chk:
        return make_response(jsonify({"status" : "Wrong Entry..!"}),401)
    
    record = Cancel_Ticket(current_user.user_name,data.get('trainid'),data.get('seatno'),data.get('class'))
    db.session.add(record)
    db.session.commit()
    
    ticket_table_del = Ticket.query.filter_by(train_id=data.get('trainid')).filter_by(user_name=current_user.user_name).filter_by(seat_no=data.get('seatno')).delete()
    db.session.commit()
    
    return make_response(jsonify({"status" : "Ticket Cancelled Successfully"}),200)

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