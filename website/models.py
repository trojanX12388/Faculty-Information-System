from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

db = SQLAlchemy()


class Faculty_Profile(db.Model, UserMixin):
    __tablename__ = 'Faculty_Profile'

    faculty_account_id = db.Column(db.Integer, primary_key=True)  # UserID
    name = db.Column(db.String(50), nullable=False)  # Name
    first_name = db.Column(db.String(50))  # First Name
    last_name = db.Column(db.String(50))  # Last Name
    middle_name = db.Column(db.String(50))  # Middle Name
    middle_initial = db.Column(db.String(50))  # Middle Initial
    name_extension = db.Column(db.String(50))  # Name Extension
    birth_date = db.Column(db.Date)  # Birthdate
    date_hired = db.Column(db.Date)  # Date Hired
    remarks = db.Column(db.String)  # Remarks
    faculty_code = db.Column(db.Integer, nullable=False)  # Faculty Code
    honorific = db.Column(db.String(50))  # Honorific
    age = db.Column(db.Integer, nullable=False)  # Age
    email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    password = db.Column(db.String(128), nullable=False)  # Password
    gender = db.Column(db.String(10), nullable=False)  # Gender
    data = db.relationship('Faculty_Data')

    def to_dict(self):
        return {
            'faculty_account_id': self.faculty_account_id,
            'name': self.name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'middle_initial': self.middle_initial,
            'name_extension': self.name_extension,
            'birth_date': self.birth_date,
            'date_hired': self.date_hired,
            'remarks': self.remarks,
            'faculty_code': self.faculty_code,
            'honorific': self.honorific,
            'age': self.age,
            'email': self.email,
            'password': self.password,
            'gender': self.gender,
            'data': self.data
        }
        
    def get_id(self):
        return str(self.faculty_account_id)  # Convert to string to ensure compatibility
    
class Faculty_Data(db.Model, UserMixin):
    __tablename__ = 'Faculty_Data'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_profile_id = db.Column(db.Integer, db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    data = db.Column(db.String(50), nullable=False)  # Data

    def to_dict(self):
        return {
            'id': self.id,
            'Faculty_Profile_id': self.Faculty_Profile_id,
            'data': self.data
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility

    
class Admin(db.Model, UserMixin):
    __tablename__ = 'Admins'

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
        if not inspector.has_table('Faculty_Profile'):
            db.create_all()
            create_sample_data()
        
#=====================================================================================================
# INSERTING DATA
def create_sample_data():
        
    # Create and insert Admin Data
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
        
           
 # Create and insert Faculty_Profile
    faculty_sample1 = Faculty_Profile(
        name='Alma Matter',
        first_name='Palma',
        last_name='Matter',
        middle_name='Bryant',
        middle_initial='B',
        name_extension='',
        birth_date= datetime.now(timezone.utc),
        date_hired= datetime.now(timezone.utc),
        remarks='',
        faculty_code=91801,
        honorific='N/A',
        age=35,
        email='alma123@gmail.com',
        password=generate_password_hash('alma123'),
        gender='Female'
        # Add more attributes here
        )
    
    faculty_sample2 = Faculty_Profile(
        name='Andrew Bardoquillo',
        first_name='Andrew',
        last_name='Bardoquillo',
        middle_name='Lucero',
        middle_initial='L',
        name_extension='',
        birth_date= datetime.now(timezone.utc),
        date_hired= datetime.now(timezone.utc),
        remarks='',
        faculty_code=51295,
        honorific='N/A',
        age=26,
        email='robertandrewb.up@gmail.com',
        password=generate_password_hash('plazma@123'),
        gender='Male'
        # Add more attributes here
        ) 
    
    db.session.add(faculty_sample1)
    db.session.add(faculty_sample2)

    db.session.commit()

