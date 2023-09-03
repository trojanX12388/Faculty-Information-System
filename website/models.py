from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class Student(db.Model, UserMixin):
    __tablename__ = 'students'

    id = db.Column(db.String(30), primary_key=True)  # UserID
    name = db.Column(db.String(50), nullable=False)  # Name
    email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    password = db.Column(db.String(128), nullable=False)  # Password
    gender = db.Column(db.Integer)  # Gender
    date_of_birth = db.Column(db.Date)  # DateOfBirth
    place_of_birth = db.Column(db.String(50))  # PlaceOfBirth
    mobile_number = db.Column(db.String(11))  # MobileNumber
    dropout = db.Column(db.Boolean)  # Dropout
    is_graduated = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'place_of_birth': self.place_of_birth,
            'mobile_number': self.mobile_number,
            'dropout': self.dropout,
            'is_graduated': self.is_graduated
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility

class Faculty(db.Model, UserMixin):
    __tablename__ = 'faculties'

    id = db.Column(db.String(30), primary_key=True)  # UserID
    name = db.Column(db.String(50), nullable=False)  # Name
    email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    password = db.Column(db.String(128), nullable=False)  # Password
    gender = db.Column(db.Integer)  # Gender
    date_of_birth = db.Column(db.Date)  # DateOfBirth
    place_of_birth = db.Column(db.String(50))  # PlaceOfBirth
    mobile_number = db.Column(db.String(20))  # MobileNumber
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'place_of_birth': self.place_of_birth,
            'mobile_number': self.mobile_number,
            'is_active': self.is_active
        }
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility
    
class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'

    id = db.Column(db.String(30), primary_key=True)  # UserID
    name = db.Column(db.String(50), nullable=False)  # Name
    email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    password = db.Column(db.String(128), nullable=False)  # Password
    gender = db.Column(db.Integer)  # Gender
    date_of_birth = db.Column(db.Date)  # DateOfBirth
    place_of_birth = db.Column(db.String(50))  # PlaceOfBirth
    mobile_number = db.Column(db.String(11))  # MobileNumber
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth,
            'place_of_birth': self.place_of_birth,
            'mobile_number': self.mobile_number,
            'is_active': self.is_active
        }
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility

def init_db(app):
    db.init_app(app)
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('students'):
            db.create_all()
            create_sample_data()
        
#=====================================================================================================
# INSERTING DATA
def create_sample_data():
    # Create and insert student data
    student_data = [
        {   
            'id': '2020-00001-CM-0',
            'name': 'Student 1',
            'email': 'student1@example.com',
            'password': generate_password_hash('password1'),
            'gender': 1,
            'date_of_birth': '2003-01-15',
            'place_of_birth': 'City 1',
            'mobile_number': '09123123123',
            'dropout': False,
            'is_graduated': False
            # Add more attributes here
        },
        {
            'id': '2020-00002-CM-0',
            'name': 'Student 2',
            'email': 'student2@example.com',
            'password': generate_password_hash('password2'),
            'gender': 2,
            'date_of_birth': '2002-05-20',
            'place_of_birth': 'City 2',
            'mobile_number': '09123123124',
            'dropout': True,
            'is_graduated': False
            # Add more attributes here
        },
        # Add more student data as needed
    ]
    
    for data in student_data:
        student = Student(**data)
        db.session.add(student)

    # Create and insert faculty data
    faculty_data = [
        {
            'id': '2020-00001-TC-0',
            'name': 'Faculty 1',
            'email': 'faculty1@example.com',
            'password': generate_password_hash('password1'),
            'gender': 1,
            'date_of_birth': '1988-07-20',
            'place_of_birth': 'City 2',
            'mobile_number': '09123123111',
            'is_active': True
            # Add more attributes here
        },
        {
            'id': '2020-00002-TC-0',
            'name': 'Faculty 2',
            'email': 'faculty2@example.com',
            'password': generate_password_hash('password2'),
            'gender': 2,
            'date_of_birth': '1975-12-05',
            'place_of_birth': 'City 3',
            'mobile_number': '09123123125',
            'is_active': False
            # Add more attributes here
        },
        # Add more faculty data as needed
    ]
    
    for data in faculty_data:
        faculty = Faculty(**data)
        db.session.add(faculty)
        
    # Create and insert admin data
    admin_data = [
        {
            'id': '2020-00001-AD-0',
            'name': 'Admin 1',
            'email': 'admin1@example.com',
            'password': generate_password_hash('password1'),
            'gender': 2,
            'date_of_birth': '1995-03-10',
            'place_of_birth': 'City 3',
            'mobile_number': '09123123222',
            'is_active': True
            # Add more attributes here
        },
        {
            'id': '2020-00002-AD-0',
            'name': 'Admin 2',
            'email': 'admin2@example.com',
            'password': generate_password_hash('password2'),
            'gender': 1,
            'date_of_birth': '1980-09-18',
            'place_of_birth': 'City 4',
            'mobile_number': '09123123223',
            'is_active': True
            # Add more attributes here
        },
        # Add more admin data as needed
    ]
    
    for data in admin_data:
        admin = Admin(**data)
        db.session.add(admin)

    db.session.commit()

