import datetime
from functools import wraps
from flask import Flask, jsonify, make_response, request, session
from flask_sqlalchemy import SQLAlchemy
import jwt
from sqlalchemy import and_, or_, func
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)

    return decorated

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref='users')

    def __repr__(self):
        return f'<User {self.username}>'

# Role Model
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Role {self.name}>'

# Patient Model
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Patient {self.first_name} {self.last_name}>'

# Appointment Model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Confirmed')

    def __repr__(self):
        return f'<Appointment {self.id}>'

# Admissions Model
class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    registration_date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Completed')

    def __repr__(self):
        return f'<Admission {self.id}>'

# Patient Test Model
class PatientTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)
    test_date_time = db.Column(db.DateTime, nullable=False)
    test_result = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<PatientTest {self.id}>'

# Operation Theatre Model
class OperationTheater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    theater_name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    availability = db.Column(db.String(50), nullable=False)
                     
    def __repr__(self):
        return f'<OperationTheater {self.name}>'

# Doctor Model
class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    specialization = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Doctor {self.first_name} {self.last_name}>'
    
# Doctor Availability Model
class DoctorAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f'<DoctorAvailability {self.id}>'
    
# Hospital Staff Model
class HospitalStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    job_title = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<HospitalStaff {self.first_name} {self.last_name}>'
    


class OperationTheatreBooking(db.Model):
    patient = db.ForeignKey(Patient, on_delete=db.CASCADE)
    doctor = db.ForeignKey(Doctor, on_delete=db.CASCADE)
    operation_type = db.CharField(max_length=255)
    date = db.DateField()
    start_time = db.TimeField()
    end_time = db.TimeField()
    notes = db.TextField(blank=True)

    def __str__(self):
        return f"OperationTheatreBooking {self.id}"

class Duty(db.Model):
    staff_id = db.ForeignKey(HospitalStaff, on_delete=db.CASCADE)
    date = db.DateField()

    def __str__(self):
        return f"Duty {self.id}"

class StaffAttendance(db.Model):
    staff_id = db.ForeignKey(HospitalStaff, on_delete=db.CASCADE)
    date = db.DateField()
    status = db.CharField(max_length=255)# (choices: "Present", "Absent")
    
    def __str__(self):
        return f"StaffAttendance {self.id}"

class Payment(db.Model):

    patient_id = db.ForeignKey(Patient, on_delete=db.CASCADE)
    amount= db.FloatField()
    payment_date = db.DateField()

    def __str__(self):
        return f"Payment {self.id}"


class PatientTestRecord(db.Model):
    
    patient_id= db.ForeignKey(Patient, on_delete=db.CASCADE)
    test_name = db.CharField(max_length=255)
    test_date = db.CharField(max_length=255)
    test_result = db.CharField(max_length=255)
    
    def __str__(self):
        return f"PatientTestRecord {self.id}"


# you can define like below sql format
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StaffAvailability(Base):
    __tablename__ = 'staff_availability'
    id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, ForeignKey('hospital_staff.id'), nullable=False)
    staff = relationship('HospitalStaff', backref='availabilities')
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    def __repr__(self):
        return f'<StaffAvailability staff_id={self.staff_id}, start_time={self.start_time}, end_time={self.end_time}>'


# Login API
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({'message': 'Logged in successfully'})
    return jsonify({'message': 'Invalid username or password'})


# Sign-Out API
@app.route('/sign-out', methods=['POST'])
def sign_out():
    session.pop('user_id', None)
    return jsonify({'message': 'Signed out successfully'})


# Patient API
@app.route('/patients', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify({'patients': [patient.dict for patient in patients]})

@app.route('/patients', methods=['POST'])
def create_patient():
    patient_data = request.json
    patient = Patient(**patient_data)
    db.session.add(patient)
    db.session.commit()
    return jsonify({'message': 'Patient created successfully'})

@app.route('/patients/int:patient_id', methods=['PUT'])
def update_patient(patient_id):
    patient_data = request.json
    patient = Patient.query.filter_by(id=patient_id).first()
    patient.first_name = patient_data.get('first_name', patient.first_name)
    patient.last_name = patient_data.get('last_name', patient.last_name)
    patient.date_of_birth = patient_data.get('date_of_birth', patient.date_of_birth)
    patient.gender = patient_data.get('gender', patient.gender)
    patient.contact_number = patient_data.get('contact_number', patient.contact_number)
    patient.email = patient_data.get('email', patient.email)
    patient.address = patient_data.get('address', patient.address)
    db.session.commit()
    return jsonify({'message': 'Patient updated successfully'})

@app.route('/patients/int:patient_id', methods=['DELETE'])
def delete_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id).first()
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'})

# Appointment API
@app.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify({'appointments': [appointment.__dict__ for appointment in appointments]})

@app.route('/appointments', methods=['POST'])
def create_appointment():
    appointment_data = request.json
    appointment = Appointment(**appointment_data)
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment created successfully'})

@app.route('/appointments/int:appointment_id', methods=['PUT'])
def update_appointment(appointment_id):
    appointment_data = request.json
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    appointment.patient_id = appointment_data.get('patient_id', appointment.patient_id)
    appointment.doctor_id = appointment_data.get('doctor_id', appointment.doctor_id)
    appointment.appointment_datetime = appointment_data.get('appointment_datetime', appointment.appointment_datetime)
    appointment.notes = appointment_data.get('notes', appointment.notes)
    db.session.commit()
    return jsonify({'message': 'Appointment updated successfully'})

@app.route('/appointments/int:appointment_id', methods=['DELETE'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({'message': 'Appointment deleted successfully'})


# Patient Test Record API
@app.route('/patient-tests', methods=['GET'])
def get_patient_tests():
    patient_tests = PatientTest.query.all()
    return jsonify({'patient_tests': [patient_test.dict for patient_test in patient_tests]})

@app.route('/patient-tests', methods=['POST'])
def create_patient_test():
    patient_test_data = request.json
    patient_test = PatientTest(**patient_test_data)
    db.session.add(patient_test)
    db.session.commit()
    return jsonify({'message': 'Patient test record created successfully'})

@app.route('/patient-tests/int:patient_test_id', methods=['PUT'])
def update_patient_test(patient_test_id):
    patient_test_data = request.json
    patient_test = PatientTest.query.filter_by(id=patient_test_id).first()
    patient_test.patient_id = patient_test_data.get('patient_id', patient_test.patient_id)
    patient_test.test_name = patient_test_data.get('test_name', patient_test.test_name)
    patient_test.test_datetime = patient_test_data.get('test_datetime', patient_test.test_datetime)
    patient_test.result = patient_test_data.get('result', patient_test.result)
    db.session.commit()
    return jsonify({'message': 'Patient test record updated successfully'})

@app.route('/patient-tests/int:patient_test_id', methods=['DELETE'])
def delete_patient_test(patient_test_id):
    patient_test = PatientTest.query.filter_by(id=patient_test_id).first()
    db.session.delete(patient_test)
    db.session.commit()
    return jsonify({'message': 'Patient test record deleted successfully'})

#Operation Theatre Booking API
@app.route('/operation-theatre-bookings', methods=['GET'])
def get_operation_theatre_bookings():
    operation_theatre_bookings = OperationTheatreBooking.query.all()
    return jsonify({'operation_theatre_bookings': [ot_booking.dict for ot_booking in operation_theatre_bookings]})

@app.route('/operation-theatre-bookings', methods=['POST'])
def create_operation_theatre_booking():
    operation_theatre_booking_data = request.json
    operation_theatre_booking = OperationTheatreBooking(**operation_theatre_booking_data)
    db.session.add(operation_theatre_booking)
    db.session.commit()
    return jsonify({'message': 'Operation theatre booking created successfully'})

@app.route('/operation-theatre-bookings/int:ot_booking_id', methods=['PUT'])
def update_operation_theatre_booking(ot_booking_id):
    operation_theatre_booking_data = request.json
    operation_theatre_booking = OperationTheatreBooking.query.filter_by(id=ot_booking_id).first()
    operation_theatre_booking.patient_id = operation_theatre_booking_data.get('patient_id', operation_theatre_booking.patient_id)
    operation_theatre_booking.doctor_id = operation_theatre_booking_data.get('doctor_id', operation_theatre_booking.doctor_id)
    operation_theatre_booking.ot_datetime = operation_theatre_booking_data.get('ot_datetime', operation_theatre_booking.ot_datetime)
    operation_theatre_booking.ot_notes = operation_theatre_booking_data.get('ot_notes', operation_theatre_booking.ot_notes)
    operation_theatre_booking.status = operation_theatre_booking_data.get('status', operation_theatre_booking.status)
    db.session.commit()
    return jsonify({'message': 'Operation theatre booking updated successfully'})


@app.route('/operation-theatre-bookings/int:ot_booking_id', methods=['DELETE'])
def delete_operation_theatre_booking(ot_booking_id):
    operation_theatre_booking = OperationTheatreBooking.query.filter_by(id=ot_booking_id).first()
    db.session.delete(operation_theatre_booking)
    db.session.commit()
    return jsonify({'message': 'Operation theatre booking deleted successfully'})


# Hospital Staff API
@app.route('/hospital-staff', methods=['GET'])
def get_hospital_staff():
    hospital_staff = HospitalStaff.query.all()
    return jsonify({'hospital_staff': [staff.dict for staff in hospital_staff]})

@app.route('/hospital-staff', methods=['POST'])
def create_hospital_staff():
    staff_data = request.json
    staff = HospitalStaff(**staff_data)
    db.session.add(staff)
    db.session.commit()
    return jsonify({'message': 'Hospital staff member created successfully'})

@app.route('/hospital-staff/int:staff_id', methods=['PUT'])
def update_hospital_staff(staff_id):
    staff_data = request.json
    staff = HospitalStaff.query.filter_by(id=staff_id).first()
    staff.name = staff_data.get('name', staff.name)
    staff.designation = staff_data.get('designation', staff.designation)
    staff.phone_number = staff_data.get('phone_number', staff.phone_number)
    db.session.commit()
    return jsonify({'message': 'Hospital staff member updated successfully'})

@app.route('/hospital-staff/int:staff_id', methods=['DELETE'])
def delete_hospital_staff(staff_id):
    staff = HospitalStaff.query.filter_by(id=staff_id).first()
    db.session.delete(staff)
    db.session.commit()
    return jsonify({'message': 'Hospital staff member deleted successfully'})


# User and Role API
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify({'users': [user.dict for user in users]})

@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    hashed_password = generate_password_hash(user_data['password'], method='sha256')
    user = User(username=user_data['username'], password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'})

@app.route('/users/int:user_id', methods=['PUT'])
def update_user(user_id):
    user_data = request.json
    user = User.query.filter_by(id=user_id).first()
    user.username = user_data.get('username', user.username)
    if user_data.get('password'):
        user.password = generate_password_hash(user_data['password'], method='sha256')
    db.session.commit()
    return jsonify({'message': 'User updated successfully'})

@app.route('/users/int:user_id', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})



################ ADMIN ##########
#Admin Dashboard API
@app.route('/dashboard', methods=['GET'])
@token_required
def admin_dashboard(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    
    patient_count = Patient.query.count()
    appointment_count = Appointment.query.count()
    admission_count = Admission.query.count()
    test_count = PatientTest.query.count()
    ot_booking_count = OperationTheatreBooking.query.count()
    doctor_count = Doctor.query.count()
    staff_count = HospitalStaff.query.count()

    return jsonify({
        'patient_count': patient_count,
        'appointment_count': appointment_count,
        'admission_count': admission_count,
        'test_count': test_count,
        'ot_booking_count': ot_booking_count,
        'doctor_count': doctor_count,
        'staff_count': staff_count
    })


# Authentication API
@app.route('/login', methods=['POST'])
def login():
    auth_data = request.json
    if not auth_data or not auth_data['username'] or not auth_data['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    
    user = User.query.filter_by(username=auth_data['username']).first()

    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth_data['password']):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@app.route('/logout', methods=['POST'])
def logout():
    return jsonify({'message': 'Logged out successfully'})


# Patient API
@app.route('/patients', methods=['GET'])
@token_required
def get_all_patients(current_user):
    
    patients = Patient.query.all()
    result = []
    for patient in patients:
        patient_data = {}
        patient_data['id'] = patient.id
        patient_data['first_name'] = patient.first_name
        patient_data['last_name'] = patient.last_name
        patient_data['gender'] = patient.gender
        patient_data['date_of_birth'] = patient.date_of_birth.strftime('%Y-%m-%d')
        patient_data['phone'] = patient.phone
        patient_data['address'] = patient.address
        patient_data['city'] = patient.city
        patient_data['state'] = patient.state
        patient_data['zip'] = patient.zip
        result.append(patient_data)

    return jsonify({'patients': result})


@app.route('/patients/int:id', methods=['GET'])
@token_required
def get_patient(current_user, id):
    
    
    patient = Patient.query.filter_by(id=id).first()
    if not patient:
        return jsonify({'message': 'Patient not found'})

    patient_data = {}
    patient_data['id'] = patient.id
    patient_data['first_name'] = patient.first_name
    patient_data['last_name'] = patient.last_name
    patient_data['gender'] = patient.gender
    patient_data['date_of_birth'] = patient.date_of_birth.strftime('%Y-%m-%d')
    patient_data['phone'] = patient.phone
    patient_data['address'] = patient.address
    patient_data['city'] = patient.city
    patient_data['state'] = patient.state
    patient_data['zip'] = patient.zip

    return jsonify({'patient': patient_data})


@app.route('/patients', methods=['POST'])
@token_required
def create_patient(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    
    data = request.get_json()

    new_patient = Patient(
        first_name=data['first_name'],
        last_name=data['last_name'],
        gender=data['gender'],
        date_of_birth=datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d'),
        phone=data['phone'],
        address=data['address'],
        city=data['city'],
        state=data['state'],
        zip=data['zip']
    )

    db.session.add(new_patient)
    db.session.commit()

    return jsonify({'message': 'New patient created'})

@app.route('/patients/int:id', methods=['PUT'])
@token_required
def update_patient(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    patient = Patient.query.filter_by(id=id).first()
    if not patient:
        return jsonify({'message': 'Patient not found'})

    data = request.get_json()

    patient.first_name = data['first_name']
    patient.last_name = data['last_name']
    patient.gender = data['gender']
    patient.date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
    patient.phone = data['phone']
    patient.address = data['address']
    patient.city = data['city']
    patient.state = data['state']
    patient.zip = data['zip']

    db.session.commit()

    return jsonify({'message': 'Patient updated'})

@app.route('/patients/int:id', methods=['DELETE'])
@token_required
def delete_patient(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    
    patient = Patient.query.filter_by(id=id).first()
    if not patient:
        return jsonify({'message': 'Patient not found'})

    db.session.delete(patient)
    db.session.commit()

    return jsonify({'message': 'Patient deleted'})



# Appointment API
@app.route('/appointments', methods=['GET'])
@token_required
def get_all_appointments(current_user):
    
    appointments = Appointment.query.all()
    result = []
    for appointment in appointments:
        appointment_data = {}
        appointment_data['id'] = appointment.id
        appointment_data['patient_id'] = appointment.patient_id
        appointment_data['doctor_id'] = appointment.doctor_id
        appointment_data['appointment_date'] = appointment.appointment_date.strftime('%Y-%m-%d')
        appointment_data['appointment_time'] = appointment.appointment_time.strftime('%H:%M:%S')
        result.append(appointment_data)

    return jsonify({'appointments': result})



@app.route('/appointments/int:id', methods=['GET'])
@token_required
def get_appointment(current_user, id):

    appointment = Appointment.query.filter_by(id=id).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'})

    appointment_data = {}
    appointment_data['id'] = appointment.id
    appointment_data['patient_id'] = appointment.patient_id
    appointment_data['doctor_id'] = appointment.doctor_id
    appointment_data['appointment_date'] = appointment.appointment_date.strftime('%Y-%m-%d')
    appointment_data['appointment_time'] = appointment.appointment_time.strftime('%H:%M:%S')

    return jsonify({'appointment': appointment_data})



@app.route('/appointments', methods=['POST'])
@token_required
def create_appointment(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    data = request.get_json()

    new_appointment = Appointment(
        patient_id=data['patient_id'],
        doctor_id=data['doctor_id'],
        appointment_date=datetime.datetime.strptime(data['appointment_date'], '%Y-%m-%d'),
        appointment_time=datetime.datetime.strptime(data['appointment_time'], '%H:%M:%S').time()
    )

    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({'message': 'New appointment created'})



@app.route('/appointments/int:id', methods=['PUT'])
@token_required
def update_appointment(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    appointment = Appointment.query.filter_by(id=id).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'})

    data = request.get_json()

    appointment.patient_id = data['patient_id']
    appointment.doctor_id = data['doctor_id']
    appointment.appointment_date = datetime.datetime.strptime(data['appointment_date'], '%Y-%m-%d')
    appointment.appointment_time = datetime.datetime.strptime(data['appointment_time'], '%H:%M:%S').time()

    db.session.commit()

    return jsonify({'message': 'Appointment updated'})

@app.route('/appointments/int:id', methods=['DELETE'])
@token_required
def delete_appointment(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    appointment = Appointment.query.filter_by(id=id).first()
    if not appointment:
        return jsonify({'message': 'Appointment not found'})

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({'message': 'Appointment deleted'})


# Admission API
@app.route('/admissions', methods=['GET'])
@token_required
def get_all_admissions(current_user):
    
    admissions = Admission.query.all()
    result = []
    for admission in admissions:
        admission_data = {}
        admission_data['id'] = admission.id
        admission_data['patient_id'] = admission.patient_id
        admission_data['admission_date'] = admission.admission_date.strftime('%Y-%m-%d')
        admission_data['admission_time'] = admission.admission_time.strftime('%H:%M:%S')
        admission_data['discharge_date'] = admission.discharge_date.strftime('%Y-%m-%d') if admission.discharge_date else None
        admission_data['discharge_time'] = admission.discharge_time.strftime('%H:%M:%S') if admission.discharge_time else None
        result.append(admission_data)

    return jsonify({'admissions': result})


@app.route('/admissions/int:id', methods=['GET'])
@token_required
def get_admission(current_user, id):
    
    admission = Admission.query.filter_by(id=id).first()
    if not admission:
        return jsonify({'message': 'Admission not found'})

    admission_data = {}
    admission_data['id'] = admission.id
    admission_data['patient_id'] = admission.patient_id
    admission_data['admission_date'] = admission.admission_date.strftime('%Y-%m-%d')
    admission_data['admission_time'] = admission.admission_time.strftime('%H:%M:%S')
    admission_data['discharge_date'] = admission.discharge_date.strftime('%Y-%m-%d') if admission.discharge_date else None
    admission_data['discharge_time'] = admission.discharge_time.strftime('%H:%M:%S') if admission.discharge_time else None

    return jsonify({'admission': admission_data})


@app.route('/admissions', methods=['POST'])
@token_required
def create_admission(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    data = request.get_json()

    new_admission = Admission(
        patient_id=data['patient_id'],
        admission_date=datetime.datetime.strptime(data['admission_date'], '%Y-%m-%d'),
        admission_time=datetime.datetime.strptime(data['admission_time'], '%H:%M:%S').time(),
        discharge_date=datetime.datetime.strptime(data['discharge_date'], '%Y-%m-%d') if data.get('discharge_date') else None,
        discharge_time=datetime.datetime.strptime(data['discharge_time'], '%H:%M:%S').time() if data.get('discharge_time') else None
    )

    db.session.add(new_admission)
    db.session.commit()

    return jsonify({'message': 'New admission created'})

@app.route('/admissions/int:id', methods=['PUT'])
@token_required
def update_admission(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    admission = Admission.query.filter_by(id=id).first()
    if not admission:
        return jsonify({'message': 'Admission not found'})
    
    data = request.get_json()

    admission.patient_id = data.get('patient_id', admission.patient_id)
    admission.admission_date = datetime.datetime.strptime(data['admission_date'], '%Y-%m-%d') if data.get('admission_date') else admission.admission_date
    admission.admission_time = datetime.datetime.strptime(data['admission_time'], '%H:%M:%S').time() if data.get('admission_time') else admission.admission_time
    admission.discharge_date = datetime.datetime.strptime(data['discharge_date'], '%Y-%m-%d') if data.get('discharge_date') else None
    admission.discharge_time = datetime.datetime.strptime(data['discharge_time'], '%H:%M:%S').time() if data.get('discharge_time') else None

    db.session.commit()

    return jsonify({'message': 'Admission updated'})



@app.route('/admissions/int:id', methods=['DELETE'])
@token_required
def delete_admission(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    admission = Admission.query.filter_by(id=id).first()
    if not admission:
        return jsonify({'message': 'Admission not found'})

    db.session.delete(admission)
    db.session.commit()

    return jsonify({'message': 'Admission deleted'})


# Patient Test API
@app.route('/patient-tests', methods=['GET'])
@token_required
def get_all_patient_tests(current_user):

    patient_tests = PatientTest.query.all()
    result = []
    for patient_test in patient_tests:
        patient_test_data = {}
        patient_test_data['id'] = patient_test.id
        patient_test_data['patient_id'] = patient_test.patient_id
        patient_test_data['test_date'] = patient_test.test_date.strftime('%Y-%m-%d')
        patient_test_data['test_name'] = patient_test.test_name
        patient_test_data['test_result'] = patient_test.test_result
        result.append(patient_test_data)

    return jsonify({'patient_tests': result})


@app.route('/patient-tests/int:id', methods=['GET'])
@token_required
def get_patient_test(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    patient_test = PatientTest.query.filter_by(id=id).first()
    if not patient_test:
        return jsonify({'message': 'Patient test not found'})

    patient_test_data = {}
    patient_test_data['id'] = patient_test.id
    patient_test_data['patient_id'] = patient_test.patient_id
    patient_test_data['test_date'] = patient_test.test_date.strftime('%Y-%m-%d')
    patient_test_data['test_name'] = patient_test.test_name
    patient_test_data['test_result'] = patient_test.test_result

    return jsonify({'patient_test': patient_test_data})

@app.route('/patient-tests', methods=['POST'])
@token_required
def create_patient_test(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    data = request.get_json()

    new_patient_test = PatientTest(
        patient_id=data['patient_id'],
        test_date=datetime.datetime.strptime(data['test_date'], '%Y-%m-%d'),
        test_name=data['test_name'],
        test_result=data['test_result']
    )

    db.session.add(new_patient_test)
    db.session.commit()

    return jsonify({'message': 'Patient test created'})


@app.route('/patient-tests/int:id', methods=['PUT'])
@token_required
def update_patient_test(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})


    patient_test = PatientTest.query.filter_by(id=id).first()
    if not patient_test:
        return jsonify({'message': 'Patient test not found'})

    data = request.get_json()

    patient_test.patient_id = data.get('patient_id', patient_test.patient_id)
    patient_test.test_date = datetime.datetime.strptime(data['test_date'], '%Y-%m-%d') if data.get('test_date') else patient_test.test_date
    patient_test.test_name = data.get('test_name', patient_test.test_name)
    patient_test.test_result = data.get('test_result', patient_test.test_result)

    db.session.commit()

    return jsonify({'message': 'Patient test updated'})



@app.route('/patient-tests/int:id', methods=['DELETE'])
@token_required
def delete_patient_test(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    patient_test = PatientTest.query.filter_by(id=id).first()
    if not patient_test:
        return jsonify({'message': 'Patient test not found'})

    db.session.delete(patient_test)
    db.session.commit()

    return jsonify({'message': 'Patient test deleted'})



# Operation Theater API
@app.route('/operation-theaters', methods=['GET'])
@token_required
def get_all_operation_theaters(current_user):

    operation_theaters = OperationTheater.query.all()
    result = []
    for operation_theater in operation_theaters:
        operation_theater_data = {}
        operation_theater_data['id'] = operation_theater.id
        operation_theater_data['theater_name'] = operation_theater.theater_name
        operation_theater_data['location'] = operation_theater.location
        operation_theater_data['availability'] = operation_theater.availability
        result.append(operation_theater_data)

    return jsonify({'operation_theaters': result})

@app.route('/operation-theaters/int:id', methods=['GET'])
@token_required
def get_operation_theater(current_user, id):

    operation_theater = OperationTheater.query.filter_by(id=id).first()
    if not operation_theater:
        return jsonify({'message': 'Operation theater not found'})

    operation_theater_data = {}
    operation_theater_data['id'] = operation_theater.id
    operation_theater_data['theater_name'] = operation_theater.theater_name
    operation_theater_data['location'] = operation_theater.location
    operation_theater_data['availability'] = operation_theater.availability

    return jsonify({'operation_theater': operation_theater_data})



@app.route('/operation-theaters', methods=['POST'])
@token_required
def create_operation_theater(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    data = request.get_json()

    new_operation_theater = OperationTheater(
        theater_name=data['theater_name'],
        location=data['location'],
        availability=data['availability']
    )

    db.session.add(new_operation_theater)
    db.session.commit()

    return jsonify({'message': 'Operation theater created'})

@app.route('/operation-theaters/int:id', methods=['PUT'])
@token_required
def update_operation_theater(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    operation_theater = OperationTheater.query.filter_by(id=id).first()
    if not operation_theater:
        return jsonify({'message': 'Operation theater not found'})

    data = request.get_json()

    operation_theater.theater_name = data.get('theater_name', operation_theater.theater_name)
    operation_theater.location = data.get('location', operation_theater.location)
    operation_theater.availability = data.get('availability', operation_theater.availability)

    db.session.commit()

    return jsonify({'message': 'Operation theater updated'})


@app.route('/operation-theaters/int:id', methods=['DELETE'])
@token_required
def delete_operation_theater(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    operation_theater = OperationTheater.query.filter_by(id=id).first()
    if not operation_theater:
        return jsonify({'message': 'Operation theater not found'})

    db.session.delete(operation_theater)
    db.session.commit()

    return jsonify({'message': 'Operation theater deleted'})


# Hospital Staff API
@app.route('/hospital-staff', methods=['GET'])
@token_required
def get_all_hospital_staff(current_user):

    hospital_staff = HospitalStaff.query.all()
    result = []
    for staff in hospital_staff:
        staff_data = {}
        staff_data['id'] = staff.id
        staff_data['name'] = staff.name
        staff_data['designation'] = staff.designation
        staff_data['phone'] = staff.phone
        staff_data['email'] = staff.email
        result.append(staff_data)

    return jsonify({'hospital_staff': result})


@app.route('/hospital-staff/int:id', methods=['GET'])
@token_required
def get_hospital_staff(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    staff = HospitalStaff.query.filter_by(id=id).first()
    if not staff:
        return jsonify({'message': 'Hospital staff not found'})

    staff_data = {}
    staff_data['id'] = staff.id
    staff_data['name'] = staff.name
    staff_data['designation'] = staff.designation
    staff_data['phone'] = staff.phone
    staff_data['email'] = staff.email

    return jsonify({'hospital_staff': staff_data})


@app.route('/hospital-staff', methods=['POST'])
@token_required
def create_hospital_staff(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    data = request.get_json()

    new_staff = HospitalStaff(
        name=data['name'],
        designation=data['designation'],
        phone=data['phone'],
        email=data['email']
    )

    db.session.add(new_staff)
    db.session.commit()

    return jsonify({'message': 'Hospital staff created'})


@app.route('/hospital-staff/int:id', methods=['PUT'])
@token_required
def update_hospital_staff(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    staff = HospitalStaff.query.filter_by(id=id).first()
    if not staff:
        return jsonify({'message': 'Hospital staff not found'})

    data = request.get_json()

    staff.name = data.get('name', staff.name)
    staff.designation = data.get('designation', staff.designation)
    staff.phone = data.get('phone', staff.phone)
    staff.email = data.get('email', staff.email)

    db.session.commit()

    return jsonify({'message': 'Hospital staff updated'})

@app.route('/hospital-staff/int:id', methods=['DELETE'])
@token_required
def delete_hospital_staff(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    staff = HospitalStaff.query.filter_by(id=id).first()
    if not staff:
        return jsonify({'message': 'Hospital staff not found'})

    db.session.delete(staff)
    db.session.commit()

    return jsonify({'message': 'Hospital staff deleted'})



# User and Role API
@app.route('/users', methods=['GET'])
@token_required
def get_all_users(current_user):
    
    users = User.query.all()
    result = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['username'] = user.username
        user_data['role'] = user.role
        result.append(user_data)

    return jsonify({'users': result})


@app.route('/users/int:id', methods=['GET'])
@token_required
def get_user(current_user, id):

    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'message': 'User not found'})

    user_data = {}
    user_data['id'] = user.id
    user_data['username'] = user.username
    user_data['role'] = user.role

    return jsonify({'user': user_data})


@app.route('/users', methods=['POST'])
@token_required
def create_user(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    data = request.get_json()

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    new_user = User(
        username=data['username'],
        password=hashed_password,
        role=data['role']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created'})



@app.route('/users/int:id', methods=['PUT'])
@token_required
def update_user(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'message': 'User not found'})

    data = request.get_json()

    user.username = data.get('username', user.username)
    user.role = data.get('role', user.role)

    db.session.commit()

    return jsonify({'message': 'User updated'})


@app.route('/users/int:id', methods=['DELETE'])
@token_required
def delete_user(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    user = User.query.filter_by(id=id).first()
    if not user:
        return jsonify({'message': 'User not found'})

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted'})


# Doctor API
@app.route('/doctors', methods=['GET'])
@token_required
def get_all_doctors(current_user):

    doctors = Doctor.query.all()
    result = []
    for doctor in doctors:
        doctor_data = {}
        doctor_data['id'] = doctor.id
        doctor_data['name'] = doctor.name
        doctor_data['specialization'] = doctor.specialization
        result.append(doctor_data)
    return jsonify({'doctors': result})



@app.route('/doctors/int:id', methods=['GET'])
@token_required
def get_doctor(current_user, id):
    
    doctor = Doctor.query.filter_by(id=id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'})

    doctor_data = {}
    doctor_data['id'] = doctor.id
    doctor_data['name'] = doctor.name
    doctor_data['specialization'] = doctor.specialization

    return jsonify({'doctor': doctor_data})


@app.route('/doctors', methods=['POST'])
@token_required
def create_doctor(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    data = request.get_json()

    new_doctor = Doctor(
        name=data['name'],
        specialization=data['specialization']
    )

    db.session.add(new_doctor)
    db.session.commit()

    return jsonify({'message': 'Doctor created'})


@app.route('/doctors/int:id', methods=['PUT'])
@token_required
def update_doctor(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    doctor = Doctor.query.filter_by(id=id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'})

    data = request.get_json()

    doctor.name = data.get('name', doctor.name)
    doctor.specialization = data.get('specialization', doctor.specialization)

    db.session.commit()

    return jsonify({'message': 'Doctor updated'})


@app.route('/doctors/int:id', methods=['DELETE'])
@token_required
def delete_doctor(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    
    doctor = Doctor.query.filter_by(id=id).first()
    if not doctor:
        return jsonify({'message': 'Doctor not found'})

    db.session.delete(doctor)
    db.session.commit()

    return jsonify({'message': 'Doctor deleted'})

@app.route('/doctor-availability', methods=['GET'])
@token_required
def get_doctor_availability(current_user):
    
    availabilities = DoctorAvailability.query.all()
    result = []
    for availability in availabilities:
        availability_data = {}
        availability_data['id'] = availability.id
        availability_data['doctor_id'] = availability.doctor_id
        availability_data['day'] = availability.day
        availability_data['start_time'] = str(availability.start_time)
        availability_data['end_time'] = str(availability.end_time)
        result.append(availability_data)
    return jsonify({'availabilities': result})

@app.route('/doctor-availability/int:id', methods=['GET'])
@token_required
def get_doctor_availability_by_id(current_user, id):
    
    availability = DoctorAvailability.query.filter_by(id=id).first()
    if not availability:
        return jsonify({'message': 'Doctor availability not found'})

    availability_data = {}
    availability_data['id'] = availability.id
    availability_data['doctor_id'] = availability.doctor_id
    availability_data['day'] = availability.day
    availability_data['start_time'] = str(availability.start_time)
    availability_data['end_time'] = str(availability.end_time)

    return jsonify({'availability': availability_data})

@app.route('/doctor-availability', methods=['POST'])
@token_required
def create_doctor_availability(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    data = request.get_json()

    new_availability = DoctorAvailability(
        doctor_id=data['doctor_id'],
        day=data['day'],
        start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
        end_time=datetime.strptime(data['end_time'], '%H:%M').time()
    )

    db.session.add(new_availability)
    db.session.commit()

    return jsonify({'message': 'Doctor availability created'})

@app.route('/doctor-availability/int:id', methods=['PUT'])
@token_required
def update_doctor_availability(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    availability = DoctorAvailability.query.filter_by(id=id).first()
    if not availability:
        return jsonify({'message': 'Doctor availability not found'})

    data = request.get_json()

    availability.doctor_id = data.get('doctor_id', availability.doctor_id)
    availability.day = data.get('day', availability.day)
    availability.start_time = datetime.strptime(data.get('start_time', str(availability.start_time)), '%H:%M').time()
    availability.end_time = datetime.strptime(data.get('end_time', str(availability.end_time)), '%H:%M').time()

    db.session.commit()

    return jsonify({'message': 'Doctor availability updated'})

@app.route('/doctor-availability/int:id', methods=['DELETE'])
@token_required
def delete_doctor_availability(current_user, id):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    availability = DoctorAvailability.query.filter_by(id=id).first()
    if not availability:
        return jsonify({'message': 'Doctor availability not found'})

    db.session.delete(availability)
    db.session.commit()

    return jsonify({'message': 'Doctor availability deleted'})



# Operation Theater Booking API
@app.route('/operation-theater-booking', methods=['POST'])
@token_required
def book_operation_theater(current_user):
    data = request.get_json()


    doctor_id = data.get('doctor_id')
    theater_id = data.get('theater_id')
    start_time = datetime.strptime(data.get('start_time'), '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(data.get('end_time'), '%Y-%m-%d %H:%M:%S')

    # check if the doctor and theater are available at the specified time
    doctor_availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id, day=start_time.weekday()).first()
    if not doctor_availability or start_time.time() < doctor_availability.start_time or end_time.time() > doctor_availability.end_time:
        return jsonify({'message': 'Doctor not available at the specified time'})

    theater = OperationTheater.query.filter_by(id=theater_id).first()
    if not theater or theater.capacity <= 0:
        return jsonify({'message': 'Theater not available at the specified time'})

    # create new operation theater booking
    new_booking = OperationTheatreBooking(
        doctor_id=doctor_id,
        theater_id=theater_id,
        start_time=start_time,
        end_time=end_time
    )

    db.session.add(new_booking)

    # decrease theater capacity by 1
    theater.capacity -= 1
    db.session.commit()

    return jsonify({'message': 'Operation theater booked successfully'})



@app.route('/analytics/patient-status', methods=['GET'])
@token_required
def get_patient_status(current_user):
    if current_user.role != 'doctor' and current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the total number of patients
    total_patients = Patient.query.count()

    # get the number of patients with each status
    statuses = Patient.query.with_entities(Patient.status, func.count(Patient.status)).group_by(Patient.status).all()

    # create a dictionary with the data
    data = {
        'total_patients': total_patients,
        'statuses': [{'status': status, 'count': count} for status, count in statuses]
    }

    return jsonify(data)


# API to get hospital revenues
@app.route('/analytics/hospital-revenues', methods=['GET'])
@token_required
def get_hospital_revenues(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the total revenue
    total_revenue = db.session.query(func.sum(Payment.amount)).scalar()

    # get the revenue for each payment type
    payment_types = Payment.query.with_entities(Payment.payment_type, func.sum(Payment.amount)).group_by(Payment.payment_type).all()

    # create a dictionary with the data
    data = {
        'total_revenue': total_revenue,
        'payment_types': [{'type': payment_type, 'revenue': revenue} for payment_type, revenue in payment_types]
    }

    return jsonify(data)


#API to get doctor availability and attendance
@app.route('/analytics/doctor-availability', methods=['GET'])
@token_required
def get_doctor_availability(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    # get the total number of doctors
    total_doctors = Doctor.query.count()

    # get the number of available doctors for each day
    availabilities = DoctorAvailability.query.with_entities(DoctorAvailability.day, func.count(DoctorAvailability.doctor_id)).group_by(DoctorAvailability.day).all()

    # get the number of attended appointments for each doctor
    attendances = Appointment.query.with_entities(Appointment.doctor_id, func.count(Appointment.id)).group_by(Appointment.doctor_id).all()

    # create a dictionary with the data
    data = {
        'total_doctors': total_doctors,
        'availabilities': [{'day': day, 'available_doctors': available_doctors} for day, available_doctors in availabilities],
        'attendances': [{'doctor_id': doctor_id, 'attended_appointments': attended_appointments} for doctor_id, attended_appointments in attendances]
    }

    return jsonify(data)


# API to get staff availability and attendance
@app.route('/analytics/staff-availability', methods=['GET'])
@token_required
def get_staff_availability(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    # get the total number of staff members
    total_staff = HospitalStaff.query.count()

    # get the number of available staff members for each day
    availabilities = StaffAvailability.query.with_entities(StaffAvailability.day, func.count(StaffAvailability.staff_id)).group_by(StaffAvailability.day).all()

    # get the number of attended appointments for each staff member
    attendances = Appointment.query.with_entities(Appointment.staff_id, func.count(Appointment.id)).group_by(Appointment.staff_id).all()

    # create a dictionary with the data
    data = {
        'total_staff': total_staff,
        'availabilities': [{'day': day, 'available_staff': available_staff} for day, available_staff in availabilities],
        'attendances': [{'staff_id': staff_id, 'attended_appointments': attended_appointments} for staff_id, attended_appointments in attendances]
    }

    return jsonify(data)



# API to get filtered patient test records
@app.route('/analytics/patient-test-records', methods=['GET'])
@token_required
def get_patient_test_records(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the parameters from the query string
    patient_id = request.args.get('patient_id')
    test_type = request.args.get('test_type')
    test_date_start = request.args.get('test_date_start')
    test_date_end = request.args.get('test_date_end')

    # query the database based on the parameters
    query = PatientTestRecord.query
    if patient_id:
        query = query.filter(PatientTestRecord.patient_id == patient_id)
    if test_type:
        query = query.filter(PatientTestRecord.test_type == test_type)
    if test_date_start:
        query = query.filter(PatientTestRecord.test_date >= test_date_start)
    if test_date_end:
        query = query.filter(PatientTestRecord.test_date <= test_date_end)
    records = query.all()

    # create a list with the data
    data = [{'id': record.id, 'patient_id': record.patient_id, 'test_type': record.test_type, 'test_date': record.test_date.strftime('%Y-%m-%d %H:%M:%S')} for record in records]

    return jsonify(data)


# API to get filtered operation theatre bookings
@app.route('/analytics/operation-theatre-bookings', methods=['GET'])
@token_required
def get_operation_theatre_bookings(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the parameters from the query string
    operation_theatre_id = request.args.get('operation_theatre_id')
    booking_date_start = request.args.get('booking_date_start')
    booking_date_end = request.args.get('booking_date_end')

    # query the database based on the parameters
    query = OperationTheatreBooking.query
    if operation_theatre_id:
        query = query.filter(OperationTheatreBooking.operation_theatre_id == operation_theatre_id)
    if booking_date_start:
        query = query.filter(OperationTheatreBooking.booking_date >= booking_date_start)
    if booking_date_end:
        query = query.filter(OperationTheatreBooking.booking_date <= booking_date_end)
    bookings = query.all()

    # create a list with the data
    data = [{'id': booking.id, 'operation_theatre_id': booking.operation_theatre_id, 'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M:%S')} for booking in bookings]

    return jsonify(data)


# API to get filtered hospital staff members
@app.route('/analytics/hospital-staff', methods=['GET'])
@token_required
def get_hospital_staff(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the parameters from the query string
    staff_type = request.args.get('staff_type')
    name = request.args.get('name')
    date_of_joining_start = request.args.get('date_of_joining_start')
    date_of_joining_end = request.args.get('date_of_joining_end')
    # query the database based on the parameters
    query = HospitalStaff.query
    if staff_type:
        query = query.filter(HospitalStaff.staff_type == staff_type)
    if name:
        query = query.filter(HospitalStaff.name.like('%{}%'.format(name)))
    if date_of_joining_start:
        query = query.filter(HospitalStaff.date_of_joining >= date_of_joining_start)
    if date_of_joining_end:
        query = query.filter(HospitalStaff.date_of_joining <= date_of_joining_end)
    staff_members = query.all()

    # create a list with the data
    data = [{'id': staff.id, 'name': staff.name, 'staff_type': staff.staff_type, 'date_of_joining': staff.date_of_joining.strftime('%Y-%m-%d')} for staff in staff_members]

    return jsonify(data)



# API to get filtered hospital revenues
@app.route('/analytics/hospital-revenues', methods=['GET'])
@token_required
def get_hospital_revenues(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the parameters from the query string
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    # query the database based on the parameters
    query = Payment.query.with_entities(func.sum(Payment.amount)).group_by(func.strftime('%Y-%m', Payment.payment_date))
    if date_start:
        query = query.filter(Payment.payment_date >= date_start)
    if date_end:
        query = query.filter(Payment.payment_date <= date_end)
    revenues = query.all()

    # create a list with the data
    data = [{'date': revenue[0].strftime('%Y-%m'), 'revenue': revenue[1]} for revenue in revenues]

    return jsonify(data)


# API to get patient data
@app.route('/patient/int:patient_id', methods=['GET'])
@token_required
def get_patient_data(current_user, patient_id):
    if current_user.role not in ['admin', 'doctor']:
        return jsonify({'message': 'You do not have permission to perform this action'})
    # get the patient from the database
    patient = Patient.query.get(patient_id)

    # check if the patient exists
    if not patient:
        return jsonify({'message': 'Patient not found'})

    # check if the current user is authorized to access the patient data
    if current_user.role == 'doctor' and patient.doctor_id != current_user.id:
        return jsonify({'message': 'You do not have permission to perform this action'})

    # create a dictionary with the patient data
    data = {
        'name': patient.name,
        'age': patient.age,
        'gender': patient.gender,
        'address': patient.address,
        'phone_number': patient.phone_number,
        'email': patient.email,
        'status': patient.status,
        'doctor_name': patient.doctor.name,
        'admission_date': patient.admission_date,
        'discharge_date': patient.discharge_date
    }

    # get the patient tests and add them to the dictionary
    tests = [{'test_name': test.name, 'result': test.result} for test in patient.tests]
    data['tests'] = tests

    # get the patient history and add it to the dictionary
    history = [{'date': entry.date, 'note': entry.note} for entry in patient.history]
    data['history'] = history

    return jsonify(data)



# API to get staff attendance
@app.route('/staff_attendance', methods=['GET'])
@token_required
def get_staff_attendance(current_user):
    if current_user.role not in ['admin']:
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the staff attendance data from the database
    staff_attendance = StaffAttendance.query.all()

    # create a dictionary to store the attendance data for each staff member
    attendance_data = {}

    # loop through the staff attendance data and add it to the dictionary
    for attendance in staff_attendance:
        if attendance.staff_id not in attendance_data:
            attendance_data[attendance.staff_id] = {'name': attendance.staff.name,
                                                    'attendance': []}
        attendance_data[attendance.staff_id]['attendance'].append({'date': attendance.date,
                                                                    'status': attendance.status})

    # return the staff attendance data
    return jsonify({'attendance_data': list(attendance_data.values())})


# API to assign daily duty to staff members
@app.route('/assign_duty', methods=['POST'])
@token_required
def assign_duty(current_user):
    if current_user.role not in ['admin']:
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the request data
    data = request.get_json()

    # get the staff member and date from the request data
    staff_id = data.get('staff_id')
    date = data.get('date')

    # get the staff member from the database
    staff = HospitalStaff.query.get(staff_id)

    # check if the staff member exists
    if not staff:
        return jsonify({'message': 'Staff member not found'})

    # check if the staff member is available on the specified date
    if not staff.is_available(date):
        return jsonify({'message': 'Staff member is not available on this date'})

    # create a new duty object
    duty = Duty(staff_id=staff_id, date=date)

    # add the duty to the database
    db.session.add(duty)
    db.session.commit()

    # return a success message
    return jsonify({'message': 'Duty assigned successfully'})


# API to get staff duty schedule
@app.route('/staff_duty_schedule', methods=['GET'])
@token_required
def get_staff_duty_schedule(current_user):
    if current_user.role not in ['admin', 'staff']:
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the staff member id from the request data
    staff_id = request.args.get('staff_id')

    # get the staff member from the database
    staff = HospitalStaff.query.get(staff_id)

    # check if the staff member exists
    if not staff:
        return jsonify({'message': 'Staff member not found'})

    # get the duty schedule for the staff member
    duty_schedule = staff.get_duty_schedule()

    # return the duty schedule
    return jsonify({'duty_schedule': duty_schedule})


# API to mark staff attendance
@app.route('/mark_staff_attendance', methods=['POST'])
@token_required
def mark_staff_attendance(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the staff attendance details from the request data
    data = request.get_json()
    staff_id = data['staff_id']
    date = data['date']
    is_present = data['is_present']

    # get the staff member from the database
    staff = HospitalStaff.query.get(staff_id)

    # check if the staff member exists
    if not staff:
        return jsonify({'message': 'Staff member not found'})

    # mark the staff member's attendance
    staff.mark_attendance(date, is_present)

    # save the changes to the database
    db.session.commit()

    # return a success message
    return jsonify({'message': 'Attendance marked successfully'})



#API to get staff attendance report
@app.route('/staff_attendance_report', methods=['GET'])
@token_required
def get_staff_attendance_report(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})
    # get the date range from the request data
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # get all staff members from the database
    staff_members = HospitalStaff.query.all()

    # create a dictionary to hold the attendance report
    attendance_report = {}

    # loop through each staff member and add their attendance data to the report
    for staff_member in staff_members:
        attendance_data = staff_member.get_attendance_data(start_date, end_date)
        attendance_report[staff_member.id] = attendance_data

    # return the attendance report
    return jsonify({'attendance_report': attendance_report})

# API to get attendance report for all staff members
@app.route('/staff_attendance_report', methods=['GET'])
@token_required
def get_staff_attendance_report(current_user):
    if current_user.role != 'admin':
        return jsonify({'message': 'You do not have permission to perform this action'})

    # get the date range from the request data
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # get all staff members from the database
    staff_members = HospitalStaff.query.all()

    # create a dictionary to hold the attendance report
    attendance_report = {}

    # loop through each staff member and add their attendance data to the report
    for staff_member in staff_members:
        attendance_data = staff_member.get_attendance_data(start_date, end_date)
        attendance_report[staff_member.id] = attendance_data

    # return the attendance report
    return jsonify({'attendance_report': attendance_report})



# Error handling    
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'message': 'The requested resource could not be found'}, 404)

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'message': 'Internal server error'}, 500)

if __name__ == 'main':
    app.run()