from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

 # Faculty Profile 

class Faculty_Profile(db.Model, UserMixin):
    __tablename__ = 'Faculty_Profile'
    faculty_account_id = db.Column(db.String(50), primary_key=True)  # UserID
    name = db.Column(db.String(50), nullable=False)  # Name
    first_name = db.Column(db.String(50), nullable=False)  # First Name
    last_name = db.Column(db.String(50), nullable=False)  # Last Name
    middle_name = db.Column(db.String(50))  # Middle Name
    middle_initial = db.Column(db.String(50))  # Middle Initial
    name_extension = db.Column(db.String(50))  # Name Extension
    birth_date = db.Column(db.Date, nullable=False)  # Birthdate
    date_hired = db.Column(db.Date, nullable=False)  # Date Hired
    remarks = db.Column(db.String)  # Remarks
    faculty_code = db.Column(db.Integer, nullable=False)  # Faculty Code
    honorific = db.Column(db.String(50))  # Honorific
    age = db.Column(db.Numeric, nullable=False)  # Age
    email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    password = db.Column(db.String(128), nullable=False)  # Password
    profile_pic = db.Column(db.String(50),default="14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08")  # Profile Pic
    is_active = db.Column(db.Boolean, default=True) 
    
    # PDS FOREIGN TABLES
    
    PDS_Personal_Details = db.relationship('PDS_Personal_Details')
    PDS_Contact_Details = db.relationship('PDS_Contact_Details')
    PDS_Family_Background = db.relationship('PDS_Family_Background')
    PDS_Educational_Background = db.relationship('PDS_Educational_Background')
    PDS_Eligibity = db.relationship('PDS_Eligibity')
    PDS_Work_Experience = db.relationship('PDS_Work_Experience')
    PDS_Voluntary_Work = db.relationship('PDS_Voluntary_Work')
    PDS_Training_Seminars = db.relationship('PDS_Training_Seminars')
    PDS_Outstanding_Achievements = db.relationship('PDS_Outstanding_Achievements')
    PDS_OfficeShips_Memberships = db.relationship('PDS_OfficeShips_Memberships')
    PDS_Agency_Membership = db.relationship('PDS_Agency_Membership')
    PDS_Teacher_Information = db.relationship('PDS_Teacher_Information')
    PDS_Additional_Questions = db.relationship('PDS_Additional_Questions')
    PDS_Character_Reference = db.relationship('PDS_Character_Reference')
    PDS_Signature = db.relationship('PDS_Signature')


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
            'profile_pic': self.profile_pic,
            'is_active': self.is_active,
    
            # PDS FOREIGN TABLES
        
            'PDS_Personal_Details': self.PDS_Personal_Details,
            'PDS_Contact_Details': self.PDS_Contact_Details,
            'PDS_Family_Background': self.PDS_Family_Background,
            'PDS_Educational_Background': self.PDS_Educational_Background,
            'PDS_Eligibity': self.PDS_Eligibity,
            'PDS_Work_Experience': self.PDS_Work_Experience,
            'PDS_Voluntary_Work': self.PDS_Voluntary_Work,
            'PDS_Training_Seminars': self.PDS_Training_Seminars,
            'PDS_Outstanding_Achievements': self.PDS_Outstanding_Achievements,
            'PDS_OfficeShips_Memberships': self.PDS_OfficeShips_Memberships,
            'PDS_Agency_Membership': self.PDS_Agency_Membership,
            'PDS_Teacher_Information': self.PDS_Teacher_Information,
            'PDS_Additional_Questions': self.PDS_Additional_Questions,
            'PDS_Character_Reference': self.PDS_Character_Reference,
            'PDS_Signature': self.PDS_Signature,

            
        }
        
    def get_id(self):
        return str(self.faculty_account_id)  # Convert to string to ensure compatibility
 
  
 # PDS Personal Details  
    
class PDS_Personal_Details(db.Model):
    __tablename__ = 'PDS_Personal_Details'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    sex = db.Column(db.String(50))  
    gender = db.Column(db.String(50)) 
    height = db.Column(db.Float)
    weight = db.Column(db.Float)  
    religion = db.Column(db.String(50))  
    civil_status = db.Column(db.String(50))  
    blood_type = db.Column(db.String(50))  
    pronoun = db.Column(db.String(50))  
    country = db.Column(db.String(50)) 
    city = db.Column(db.String(50)) 
    citizenship = db.Column(db.String(50)) 
    dual_citizenship = db.Column(db.String(50)) 
    remarks = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    
    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'sex': self.sex,
            'gender': self.gender,
            'height': self.height,
            'weight': self.weight,
            'religion': self.religion,
            'civil_status': self.civil_status,
            'blood_type': self.blood_type,
            'pronoun': self.pronoun,
            'country': self.country,
            'city': self.city,
            'citizenship': self.citizenship,
            'dual_citizenship': self.dual_citizenship,
            'remarks': self.remarks,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility

 # PDS Contact Details  
   
class PDS_Contact_Details(db.Model):
    __tablename__ = 'PDS_Contact_Details'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    email = db.Column(db.String(50))  
    mobile_number = db.Column(db.Numeric) 
    perm_country = db.Column(db.String(50))
    perm_region = db.Column(db.String(50))    
    perm_province = db.Column(db.String(50))  
    perm_city = db.Column(db.String(50))  
    perm_address = db.Column(db.String(50))  
    perm_zip_code = db.Column(db.Numeric)  
    perm_phone_number = db.Column(db.Numeric) 
    res_country = db.Column(db.String(50))
    res_region = db.Column(db.String(50))    
    res_province = db.Column(db.String(50))  
    res_city = db.Column(db.String(50))  
    res_address = db.Column(db.String(50))  
    res_zip_code = db.Column(db.Numeric)  
    res_phone_number = db.Column(db.Numeric) 
    remarks = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'email': self.email,
            'mobile_number': self.mobile_number,
            'perm_country': self.perm_country,
            'perm_region': self.perm_region,
            'perm_province': self.perm_province,
            'perm_city': self.perm_city,
            'perm_address': self.perm_address,
            'perm_zip_code': self.perm_zip_code,
            'perm_phone_number': self.perm_phone_number,
            'res_country': self.res_country,
            'res_region': self.res_region,
            'res_province': self.res_province,
            'res_city': self.res_city,
            'res_address': self.res_address,
            'res_zip_code': self.res_zip_code,
            'res_phone_number': self.res_phone_number,
            'remarks': self.remarks,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility

# PDS Family Background  
  
class PDS_Family_Background(db.Model):
    __tablename__ = 'PDS_Family_Background'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    full_name = db.Column(db.String(50))  
    relationship = db.Column(db.String(50))  
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'full_name': self.full_name,
            'relationship': self.relationship,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    

# PDS Educational Background  
  
class PDS_Educational_Background(db.Model):
    __tablename__ = 'PDS_Educational_Background'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    school_name = db.Column(db.String(50))  
    level = db.Column(db.String(50))  
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)  
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'school_name': self.school_name,
            'level': self.level,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
    
# PDS Eligibity  
  
class PDS_Eligibity(db.Model):
    __tablename__ = 'PDS_Eligibity'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    eligibity = db.Column(db.String(50))  
    rating = db.Column(db.Float, default=0)  
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'eligibity': self.eligibity,
            'rating': self.rating,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    

   
# PDS Work Experience  
  
class PDS_Work_Experience(db.Model):
    __tablename__ = 'PDS_Work_Experience'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    position = db.Column(db.String(50))  
    company_name = db.Column(db.String(50)) 
    status = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'position_title': self.position,
            'company_name': self.company_name,
            'status': self.status,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
# PDS Voluntary Work  
  
class PDS_Voluntary_Work(db.Model):
    __tablename__ = 'PDS_Voluntary_Work'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    organization = db.Column(db.String(50))  
    position = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'organization': self.organization,
            'position': self.position,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Training & Seminars 
  
class PDS_Training_Seminars(db.Model):
    __tablename__ = 'PDS_Training_Seminars'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    title = db.Column(db.String(50))  
    level = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'title': self.title,
            'level': self.level,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Outstanding Achievements
  
class PDS_Outstanding_Achievements(db.Model):
    __tablename__ = 'PDS_Outstanding_Achievements'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    achievement = db.Column(db.String(50))  
    level = db.Column(db.String(50)) 
    date = db.Column(db.Date) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'achievement': self.achievement,
            'level': self.level,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS OfficeShips/Memberships
  
class PDS_OfficeShips_Memberships(db.Model):
    __tablename__ = 'PDS_OfficeShips_Memberships'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    organization = db.Column(db.String(50))  
    position = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'organization': self.organization,
            'position': self.position,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Agency Membership
  
class PDS_Agency_Membership(db.Model):
    __tablename__ = 'PDS_Agency_Membership'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    GSIS = db.Column(db.String(20))  
    PAGIBIG = db.Column(db.String(20)) 
    PHILHEALTH = db.Column(db.String(20)) 
    SSS = db.Column(db.String(20)) 
    TIN = db.Column(db.String(20)) 
    remarks = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'GSIS': self.GSIS,
            'PAGIBIG': self.PAGIBIG,
            'PHILHEALTH': self.PHILHEALTH,
            'SSS': self.SSS,
            'TIN': self.TIN,
            'remarks': self.remarks,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Teacher Information
  
class PDS_Teacher_Information(db.Model):
    __tablename__ = 'PDS_Teacher_Information'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    information = db.Column(db.String(50)) 
    type = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'information': self.information,
            'type': self.type,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     


# PDS Additional Questions
  
class PDS_Additional_Questions(db.Model):
    __tablename__ = 'PDS_Additional_Questions'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    
    q1_a = db.Column(db.String(50)) 
    q1_a_details = db.Column(db.String(50)) 
    
    q1_b = db.Column(db.String(50)) 
    q1_b_details = db.Column(db.String(50)) 
    
    q2_a = db.Column(db.String(50)) 
    q2_a_details = db.Column(db.String(50)) 
    
    q2_b = db.Column(db.String(50))
    q2_b_details = db.Column(db.String(50)) 
    
    q3 = db.Column(db.String(50))
    q3_details = db.Column(db.String(50)) 
    
    q4 = db.Column(db.String(50))
    q4_details = db.Column(db.String(50)) 
    
    q5_a = db.Column(db.String(50)) 
    q5_a_details = db.Column(db.String(50)) 
    
    q5_b = db.Column(db.String(50)) 
    q5_b_details = db.Column(db.String(50)) 
    
    q6 = db.Column(db.String(50)) 
    q6_details = db.Column(db.String(50)) 
    
    q7_a = db.Column(db.String(50))
    q7_a_details = db.Column(db.String(50)) 
    
    q7_b = db.Column(db.String(50))  
    q7_b_details = db.Column(db.String(50)) 
    
    q7_c = db.Column(db.String(50)) 
    q7_c_details = db.Column(db.String(50)) 
    
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'q1_a': self.q1_a,
            'q1_a_details': self.q1_a_details,
            
            'q1_b': self.q1_b,
            'q1_b_details': self.q1_b_details,
            
            'q2_a': self.q2_a,
            'q2_a_details': self.q2_a_details,
            
            'q2_b': self.q2_b,
            'q2_b_details': self.q2_b_details,
            
            'q3': self.q3,
            'q3_details': self.q3_details,
            
            'q4': self.q4,
            'q4_details': self.q4_details,
            
            'q5_a': self.q5_a,
            'q5_a_details': self.q5_a_details,
            
            'q5_b': self.q5_b,
            'q5_b_details': self.q5_b_details,
            
            'q6': self.q6,
            'q6_details': self.q6_details,
            
            'q7_a': self.q7_a,
            'q7_a_details': self.q7_a_details,
            
            'q7_b': self.q7_b,
            'q7_b_details': self.q7_b_details,
            
            'q7_c': self.q7_c,
            'q7_c_details': self.q7_c_details,
            
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
# PDS Character Reference
  
class PDS_Character_Reference(db.Model):
    __tablename__ = 'PDS_Character_Reference'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    full_name = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'full_name': self.full_name,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
   
# PDS Signature
  
class PDS_Signature(db.Model):
    __tablename__ = 'PDS_Signature'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    faculty_account_id = db.Column(db.String(50), db.ForeignKey('Faculty_Profile.faculty_account_id'))  # FacultyID
    wet_signature = db.Column(db.String(50)) 
    dict_certificate = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_account_id': self.faculty_account_id,
            'wet_signature': self.wet_signature,
            'dict_certificate': self.dict_certificate,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
 # ADMIN DATA   
    
    
    
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
        faculty_account_id='2020-00072-D-1',
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
        # Add more attributes here
        )
    
    faculty_sample2 = Faculty_Profile(
        faculty_account_id='2020-00073-D-1',
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
        # Add more attributes here
        ) 
    
    faculty_sample3 = Faculty_Profile(
        faculty_account_id='2020-00076-D-4',
        name='Jason Derbis',
        first_name='Jason',
        last_name='Derbis',
        middle_name='Lucero',
        middle_initial='L',
        name_extension='Jr.',
        birth_date= datetime.now(timezone.utc),
        date_hired= datetime.now(timezone.utc),
        remarks='N/A',
        faculty_code=81214,
        honorific='N/A',
        age=29,
        email='sample123@gmail.com',
        password=generate_password_hash('plazma@123'),
        # Add more attributes here
        ) 
    
    # ADD FACULTY DATA
    
    # db.session.add(faculty_sample1)
    # db.session.add(faculty_sample2)
    # db.session.add(faculty_sample3)
    
    # # COMMIT 
    
    # db.session.commit()

    # db.session.close()
