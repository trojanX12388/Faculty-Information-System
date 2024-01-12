from datetime import datetime, timezone
from sqlalchemy import inspect
from werkzeug.security import generate_Password_hash
from flask_login import UserMixin

from .extensions import db

# Faculty Users
class Faculty(db.Model):
    __tableName__ = 'FISFaculty' # Set the Name of table in database
    FacultyId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FacultyType = db.Column(db.String(50), nullable=False)  # Faculty Type
    Rank = db.Column(db.String(50))  # Faculty Rank
    Units = db.Column(db.Numeric, nullable=False)  # Faculty Unit
    Name = db.Column(db.String(50), nullable=False)  # Name
    FirstName = db.Column(db.String(50), nullable=False)  # First Name
    LastName = db.Column(db.String(50), nullable=False)  # Last Name
    MiddleName = db.Column(db.String(50))  # Middle Name
    MiddleInitial = db.Column(db.String(50))  # Middle Initial
    NameExtension = db.Column(db.String(50))  # Name Extension
    BirthDate = db.Column(db.Date, nullable=False)  # Birthdate
    DateHired = db.Column(db.Date, nullable=False)  # Date Hired
    Degree = db.Column(db.String)  # Degree
    Remarks = db.Column(db.String)  # Remarks
    FacultyCode = db.Column(db.Integer, nullable=False)  # Faculty Code
    Honorific = db.Column(db.String(50))  # Honorific
    Age = db.Column(db.Numeric, nullable=False)  # Age
    
    Email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    ResidentialAddress = db.Column(db.String(50))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    Gender = db.Column(db.Integer) # Gender # 1 if Male 2 if Female
    
    Password = db.Column(db.String(128), nullable=False)  # Password
    ProfilePic= db.Column(db.String(50),default="14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08")  # Profile Pic
    IsActive = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # FOREIGN TABLES
    

    def to_dict(self):
        return {
            'FacultyId': self.FacultyId,
            'FacultyType': self.FacultyType,
            'Rank': self.Rank,
            'Units': self.Units,
            'Name': self.Name,
            'FirstName': self.FirstName,
            'LastName': self.LastName,
            'MiddleName': self.MiddleName,
            'MiddleInitial': self.MiddleInitial,
            'NameExtension': self.NameExtension,
            'BirthDate': self.BirthDate,
            'DateHired': self.DateHired,
            'Degree': self.Degree,
            'Remarks': self.Remarks,
            'FacultyCode': self.FacultyCode,
            'Honorific': self.Honorific,
            'Age': self.Age,

            'Email': self.Email,
            # 'Password': self.Password,
            'ProfilePic': self.ProfilePic,
            'IsActive': self.IsActive,
        }
        
    def get_id(self):
        return str(self.FacultyId)  # Convert to string to ensure compatibility


 # Faculty Profile 

class FISFaculty(db.Model, UserMixin):
    __tableName__ = 'FISFaculty'
    FacultyId = db.Column(db.Integer, primary_key=True, autoincrement=True)  # UserID
    FacultyType = db.Column(db.String(50), nullable=False)  # Faculty Type
    Rank = db.Column(db.String(50))  # Faculty Rank
    Units = db.Column(db.Numeric, nullable=False)  # Faculty Unit
    Name = db.Column(db.String(50), nullable=False)  # Name
    FirstName = db.Column(db.String(50), nullable=False)  # First Name
    LastName = db.Column(db.String(50), nullable=False)  # Last Name
    MiddleName = db.Column(db.String(50))  # Middle Name
    MiddleInitial = db.Column(db.String(50))  # Middle Initial
    NameExtension = db.Column(db.String(50))  # Name Extension
    BirthDate = db.Column(db.Date, nullable=False)  # Birthdate
    DateHired = db.Column(db.Date, nullable=False)  # Date Hired
    Degree = db.Column(db.String)  # Degree
    Remarks = db.Column(db.String)  # Remarks
    FacultyCode = db.Column(db.Integer, nullable=False)  # Faculty Code
    Honorific = db.Column(db.String(50))  # Honorific
    Age = db.Column(db.Numeric, nullable=False)  # Age
    
    Email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    ResidentialAddress = db.Column(db.String(50))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    Gender = db.Column(db.Integer) # Gender # 1 if Male 2 if Female

    Password = db.Column(db.String(128), nullable=False)  # Password
    ProfilePic= db.Column(db.String(50),default="14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08")  # Profile Pic
    IsActive = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # FOREIGN TABLES
    
    # PDS
    FISPDS_PersonalDetails = db.relationship('FISPDS_PersonalDetails')
    FISPDS_ContactDetails = db.relationship('FISPDS_ContactDetails')
    FISPDS_FamilyBackground = db.relationship('FISPDS_FamilyBackground')
    FISPDS_EducationalBackground = db.relationship('FISPDS_EducationalBackground')
    FISPDS_Eligibity = db.relationship('FISPDS_Eligibity')
    FISPDS_WorkExperience = db.relationship('FISPDS_WorkExperience')
    FISPDS_VoluntaryWork = db.relationship('FISPDS_VoluntaryWork')
    FISPDS_TrainingSeminars = db.relationship('FISPDS_TrainingSeminars')
    FISPDS_OutstandingAchievements = db.relationship('FISPDS_OutstandingAchievements')
    FISPDS_OfficeShipsMemberships = db.relationship('FISPDS_OfficeShipsMemberships')
    FISPDS_AgencyMembership = db.relationship('FISPDS_AgencyMembership')
    FISPDS_TeacherInformation = db.relationship('FISPDS_TeacherInformation')
    FISPDS_AdditionalQuestions = db.relationship('FISPDS_AdditionalQuestions')
    FISPDS_CharacterReference = db.relationship('FISPDS_CharacterReference')
    FISPDS_Signature = db.relationship('FISPDS_Signature')
    
    # SUBMODULES
    FISEvaluations = db.relationship('FISEvaluations')
    FISAwards = db.relationship('FISAwards')
    FISQualifications = db.relationship('FISQualifications')
    FISPublications = db.relationship('FISPublications')
    FISConferences = db.relationship('FISConferences')
    FISAnnouncement = db.relationship('FISAnnouncement')
    FISResearchProjects = db.relationship('FISResearchProjects')
    FISAdvising = db.relationship('FISAdvising')
    FISMentoring = db.relationship('FISMentoring')
    FISCommittee = db.relationship('FISCommittee')
    FISCollaborationOpportunities = db.relationship('FISCollaborationOpportunities')
    FISProfessionalDevelopment = db.relationship('FISProfessionalDevelopment')
    FISFeedback = db.relationship('FISFeedback')
    FISTeachingActivities = db.relationship('FISTeachingActivities')
    FISAssignmentTypes = db.relationship('FISAssignmentTypes')
    FISTeachingAssignments = db.relationship('FISTeachingAssignments')
    FISMandatoryRequirements = db.relationship('FISMandatoryRequirements')
    
    # TOKEN
    FISLoginToken = db.relationship('FISLoginToken')


    def to_dict(self):
        return {
            'FacultyId': self.FacultyId,
            'FacultyType': self.FacultyType,
            'Rank': self.Rank,
            'Units': self.Units,
            'Name': self.Name,
            'FirstName': self.FirstName,
            'LastName': self.LastName,
            'MiddleName': self.MiddleName,
            'MiddleInitial': self.MiddleInitial,
            'NameExtension': self.NameExtension,
            'BirthDate': self.BirthDate,
            'DateHired': self.DateHired,
            'Degree': self.Degree,
            'Remarks': self.Remarks,
            'FacultyCode': self.FacultyCode,
            'Honorific': self.Honorific,
            'Age': self.Age,

            'Email': self.Email,
            'ResidentialAddress': self.ResidentialAddress,
            'MobileNumber': self.MobileNumber,
            'Gender': self.Gender,
            
            'Password': self.Password,
            'ProfilePic': self.ProfilePic,
            'IsActive': self.IsActive,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
    
            # FOREIGN TABLES
            
            # PDS
            'FISPDS_PersonalDetails': self.FISPDS_PersonalDetails,
            'FISPDS_ContactDetails': self.FISPDS_ContactDetails,
            'FISPDS_FamilyBackground': self.FISPDS_FamilyBackground,
            'FISPDS_EducationalBackground': self.FISPDS_EducationalBackground,
            'FISPDS_Eligibity': self.FISPDS_Eligibity,
            'FISPDS_WorkExperience': self.FISPDS_WorkExperience,
            'FISPDS_VoluntaryWork': self.FISPDS_VoluntaryWork,
            'FISPDS_TrainingSeminars': self.FISPDS_TrainingSeminars,
            'FISPDS_OutstandingAchievements': self.FISPDS_OutstandingAchievements,
            'FISPDS_OfficeShipsMemberships': self.FISPDS_OfficeShipsMemberships,
            'FISPDS_AgencyMembership': self.FISPDS_AgencyMembership,
            'FISPDS_TeacherInformation': self.FISPDS_TeacherInformation,
            'FISPDS_AdditionalQuestions': self.FISPDS_AdditionalQuestions,
            'FISPDS_CharacterReference': self.FISPDS_CharacterReference,
            'FISPDS_Signature': self.FISPDS_Signature,
            
            # SUBMODULES
            'FISEvaluations': self.FISEvaluations,
            'FISAwards': self.FISAwards,
            'FISQualifications': self.FISQualifications,
            'FISPublications': self.FISPublications,
            'FISConferences': self.FISConferences,
            'FISAnnouncement': self.FISAnnouncement,
            'FISResearchProjects': self.FISResearchProjects,
            'FISAdvising': self.FISAdvising,
            'FISMentoring': self.FISMentoring,
            'FISCommittee': self.FISCommittee,
            'FISCollaborationOpportunities': self.FISCollaborationOpportunities,
            'FISProfessionalDevelopment': self.FISProfessionalDevelopment,
            'FISFeedback': self.FISFeedback,
            'FISTeachingActivities': self.FISTeachingActivities,
            'FISAssignmentTypes': self.FISAssignmentTypes,
            'FISTeachingAssignments': self.FISTeachingAssignments,
            'FISMandatoryRequirements': self.FISMandatoryRequirements,
            
            'FISLoginToken': self.FISLoginToken,

            
        }
        
    def get_id(self):
        return str(self.FacultyId)  # Convert to string to ensure compatibility
  
# Admin Profile 

class FISAdmin(db.Model, UserMixin):
    __tableName__ = 'FISAdmin'
    AdminId = db.Column(db.Integer, primary_key=True, autoincrement=True)  # UserID
    AdminType = db.Column(db.String(50), nullable=False)  # Faculty Type
    Rank = db.Column(db.String(50))  # Faculty Rank
    Units = db.Column(db.Numeric, nullable=False)  # Faculty Unit
    Name = db.Column(db.String(50), nullable=False)  # Name
    FirstName = db.Column(db.String(50), nullable=False)  # First Name
    LastName = db.Column(db.String(50), nullable=False)  # Last Name
    MiddleName = db.Column(db.String(50))  # Middle Name
    MiddleInitial = db.Column(db.String(50))  # Middle Initial
    NameExtension = db.Column(db.String(50))  # Name Extension
    BirthDate = db.Column(db.Date, nullable=False)  # Birthdate
    DateHired = db.Column(db.Date, nullable=False)  # Date Hired
    Degree = db.Column(db.String)  # Degree
    Remarks = db.Column(db.String)  # Remarks
    FacultyCode = db.Column(db.Integer, nullable=False)  # Faculty Code
    Honorific = db.Column(db.String(50))  # Honorific
    Age = db.Column(db.Numeric, nullable=False)  # Age
    
    Email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    ResidentialAddress = db.Column(db.String(50))  # ResidentialAddress
    MobileNumber = db.Column(db.String(11))  # MobileNumber
    Gender = db.Column(db.Integer) # Gender # 1 if Male 2 if Female

    Password = db.Column(db.String(128), nullable=False)  # Password
    ProfilePic= db.Column(db.String(50),default="14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08")  # Profile Pic
    IsActive = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  
    
    # FOREIGN TABLES
    
    FISPDS_PersonalDetails = db.relationship('FISPDS_PersonalDetails')
    FISPDS_ContactDetails = db.relationship('FISPDS_ContactDetails')
    FISPDS_FamilyBackground = db.relationship('FISPDS_FamilyBackground')
    FISPDS_EducationalBackground = db.relationship('FISPDS_EducationalBackground')
    FISPDS_Eligibity = db.relationship('FISPDS_Eligibity')
    FISPDS_WorkExperience = db.relationship('FISPDS_WorkExperience')
    FISPDS_VoluntaryWork = db.relationship('FISPDS_VoluntaryWork')
    FISPDS_TrainingSeminars = db.relationship('FISPDS_TrainingSeminars')
    FISPDS_OutstandingAchievements = db.relationship('FISPDS_OutstandingAchievements')
    FISPDS_OfficeShipsMemberships = db.relationship('FISPDS_OfficeShipsMemberships')
    FISPDS_AgencyMembership = db.relationship('FISPDS_AgencyMembership')
    FISPDS_TeacherInformation = db.relationship('FISPDS_TeacherInformation')
    FISPDS_AdditionalQuestions = db.relationship('FISPDS_AdditionalQuestions')
    FISPDS_CharacterReference = db.relationship('FISPDS_CharacterReference')
    FISPDS_Signature = db.relationship('FISPDS_Signature')
    
    FISLoginToken = db.relationship('FISLoginToken')
    
    def to_dict(self):
        return {
            'AdminId': self.AdminId,
            'AdminType': self.AdminType,
            'Rank': self.Rank,
            'Units': self.Units,
            'Name': self.Name,
            'FirstName': self.FirstName,
            'LastName': self.LastName,
            'MiddleName': self.MiddleName,
            'MiddleInitial': self.MiddleInitial,
            'NameExtension': self.NameExtension,
            'BirthDate': self.BirthDate,
            'DateHired': self.DateHired,
            'Degree': self.Degree,
            'Remarks': self.Remarks,
            'FacultyCode': self.FacultyCode,
            'Honorific': self.Honorific,
            'Age': self.Age,

            'Email': self.Email,
            'ResidentialAddress': self.ResidentialAddress,
            'MobileNumber': self.MobileNumber,
            'Gender': self.Gender,
            
            'Password': self.Password,
            'ProfilePic': self.ProfilePic,
            'IsActive': self.IsActive,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            
            # PDS FOREIGN TABLES
        
            'FISPDS_PersonalDetails': self.FISPDS_PersonalDetails,
            'FISPDS_ContactDetails': self.FISPDS_ContactDetails,
            'FISPDS_FamilyBackground': self.FISPDS_FamilyBackground,
            'FISPDS_EducationalBackground': self.FISPDS_EducationalBackground,
            'FISPDS_Eligibity': self.FISPDS_Eligibity,
            'FISPDS_WorkExperience': self.FISPDS_WorkExperience,
            'FISPDS_VoluntaryWork': self.FISPDS_VoluntaryWork,
            'FISPDS_TrainingSeminars': self.FISPDS_TrainingSeminars,
            'FISPDS_OutstandingAchievements': self.FISPDS_OutstandingAchievements,
            'FISPDS_OfficeShipsMemberships': self.FISPDS_OfficeShipsMemberships,
            'FISPDS_AgencyMembership': self.FISPDS_AgencyMembership,
            'FISPDS_TeacherInformation': self.FISPDS_TeacherInformation,
            'FISPDS_AdditionalQuestions': self.FISPDS_AdditionalQuestions,
            'FISPDS_CharacterReference': self.FISPDS_CharacterReference,
            'FISPDS_Signature': self.FISPDS_Signature,
            
            'FISLoginToken': self.FISLoginToken,
        }
        
    def get_id(self):
        return str(self.AdminId)  # Convert to string to ensure compatibility
   
# SYSTEM ADMIN 

class System_Admin(db.Model, UserMixin):
    __tableName__ = 'System_Admin'
    SystemAdminId = db.Column(db.String(50), primary_key=True)  # UserID
    Name = db.Column(db.String(50), nullable=False)  # Name
    Email = db.Column(db.String(50), unique=True, nullable=False)  # Email
    Password = db.Column(db.String(128), nullable=False)  # Password
   
    ProfilePic = db.Column(db.String(50),default="14wkc8rPgd8NcrqFoRFO_CNyrJ7nhmU08")  # Profile Pic  
    access_token = db.Column(db.String)
    refresh_token = db.Column(db.String)
    
    def to_dict(self):
        return {
            'SystemAdminId': self.SystemAdminId,
            'Name': self.Name,
            'Email': self.Email,
            'Password': self.Password,
            'ProfilePic': self.ProfilePic,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
        }
        
    def get_id(self):
        return str(self.SystemAdminId)  # Convert to string to ensure compatibility

    
 # PDS Personal Details  
    
class FISPDS_PersonalDetails(db.Model):
    __tableName__ = 'FISPDS_PersonalDetails'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
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
    Remarks = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    
    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
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
            'Remarks': self.Remarks,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility

 # PDS Contact Details  
   
class FISPDS_ContactDetails(db.Model):
    __tableName__ = 'FISPDS_ContactDetails'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    Email = db.Column(db.String(50))  
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
    Remarks = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'Email': self.Email,
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
            'Remarks': self.Remarks,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility

# PDS Family Background  
  
class FISPDS_FamilyBackground(db.Model):
    __tableName__ = 'FISPDS_FamilyBackground'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    full_Name = db.Column(db.String(50))  
    relationship = db.Column(db.String(50))  
    is_delete = db.Column(db.Boolean, default=False) 
    
    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'full_Name': self.full_Name,
            'relationship': self.relationship,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    

# PDS Educational Background  
  
class FISPDS_EducationalBackground(db.Model):
    __tableName__ = 'FISPDS_EducationalBackground'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    school_Name = db.Column(db.String(50))  
    level = db.Column(db.String(50))  
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)  
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'school_Name': self.school_Name,
            'level': self.level,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
    
# PDS Eligibity  
  
class FISPDS_Eligibity(db.Model):
    __tableName__ = 'FISPDS_Eligibity'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    eligibity = db.Column(db.String(50))  
    rating = db.Column(db.Float, default=0)  
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'eligibity': self.eligibity,
            'rating': self.rating,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    

   
# PDS Work Experience  
  
class FISPDS_WorkExperience(db.Model):
    __tableName__ = 'FISPDS_WorkExperience'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    position = db.Column(db.String(50))  
    company_Name = db.Column(db.String(50)) 
    status = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'position_title': self.position,
            'company_Name': self.company_Name,
            'status': self.status,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
# PDS Voluntary Work  
  
class FISPDS_VoluntaryWork(db.Model):
    __tableName__ = 'FISPDS_VoluntaryWork'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    organization = db.Column(db.String(50))  
    position = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'organization': self.organization,
            'position': self.position,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Training & Seminars 
  
class FISPDS_TrainingSeminars(db.Model):
    __tableName__ = 'FISPDS_TrainingSeminars'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    title = db.Column(db.String(50))  
    level = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'title': self.title,
            'level': self.level,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Outstanding Achievements
  
class FISPDS_OutstandingAchievements(db.Model):
    __tableName__ = 'FISPDS_OutstandingAchievements'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    achievement = db.Column(db.String(50))  
    level = db.Column(db.String(50)) 
    date = db.Column(db.Date) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'achievement': self.achievement,
            'level': self.level,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS OfficeShips/Memberships
  
class FISPDS_OfficeShipsMemberships(db.Model):
    __tableName__ = 'FISPDS_OfficeShipsMemberships'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    organization = db.Column(db.String(50))  
    position = db.Column(db.String(50)) 
    from_date = db.Column(db.Date) 
    to_date = db.Column(db.Date)   
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'organization': self.organization,
            'position': self.position,
            'from_date': self.from_date,
            'to_date': self.to_date,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Agency Membership
  
class FISPDS_AgencyMembership(db.Model):
    __tableName__ = 'FISPDS_AgencyMembership'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    GSIS = db.Column(db.String(20))  
    PAGIBIG = db.Column(db.String(20)) 
    PHILHEALTH = db.Column(db.String(20)) 
    SSS = db.Column(db.String(20)) 
    TIN = db.Column(db.String(20)) 
    Remarks = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'GSIS': self.GSIS,
            'PAGIBIG': self.PAGIBIG,
            'PHILHEALTH': self.PHILHEALTH,
            'SSS': self.SSS,
            'TIN': self.TIN,
            'Remarks': self.Remarks,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
  

# PDS Teacher Information
  
class FISPDS_TeacherInformation(db.Model):
    __tableName__ = 'FISPDS_TeacherInformation'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    information = db.Column(db.String(50)) 
    type = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'information': self.information,
            'type': self.type,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     


# PDS Additional Questions
  
class FISPDS_AdditionalQuestions(db.Model):
    __tableName__ = 'FISPDS_AdditionalQuestions'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    
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
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            
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
  
class FISPDS_CharacterReference(db.Model):
    __tableName__ = 'FISPDS_CharacterReference'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    full_Name = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'full_Name': self.full_Name,
            'is_delete': self.is_delete,
            
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
    
   
# PDS Signature
  
class FISPDS_Signature(db.Model):
    __tableName__ = 'FISPDS_Signature'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    wet_signature = db.Column(db.String(50)) 
    dict_certificate = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'wet_signature': self.wet_signature,
            'dict_certificate': self.dict_certificate,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility     
   
   
# LOGIN TOKEN
  
class FISLoginToken(db.Model):
    __tableName__ = 'FISLoginToken'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    access_token = db.Column(db.String)
    refresh_token = db.Column(db.String)
    is_delete = db.Column(db.Boolean, default=False) 

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            'AdminId': self.AdminId,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility
    
    
# FACULTY AND ADMIN SUBMODULES

# ------------------------------------------------
# FISEVALUATIONS
  
class FISEvaluations(db.Model):
    __tableName__ = 'FISEvaluations'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    FISfeedback = db.Column(db.String) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'FISfeedback': self.FISfeedback,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISAWARDS
  
class FISAwards(db.Model):
    __tableName__ = 'FISAwards'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    award_Name = db.Column(db.String) 
    date_received = db.Column(db.Date)
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'award_Name': self.award_Name,
            'date_received': self.date_received,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISQUALIFICATIONS
  
class FISQualifications(db.Model):
    __tableName__ = 'FISQualifications'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    Degree = db.Column(db.String(50)) 
    certification = db.Column(db.String(50)) 
    area_expertise = db.Column(db.String) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'Degree': self.Degree,
            'certification': self.certification,
            'area_expertise': self.area_expertise,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISPUBLICATIONS
  
class FISPublications(db.Model):
    __tableName__ = 'FISPublications'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    title = db.Column(db.String(50)) 
    type = db.Column(db.String(50)) 
    date_published = db.Column(db.Date)
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'title': self.title,
            'type': self.type,
            'date_published': self.date_published,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISCONFERENCES
  
class FISConferences(db.Model):
    __tableName__ = 'FISConferences'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    conference_Name = db.Column(db.String(50)) 
    date = db.Column(db.Date)
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'conference_Name': self.conference_Name,
            'date': self.date,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISANNOUNCEMENT
  
class FISAnnouncement(db.Model):
    __tableName__ = 'FISAnnouncement'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    title = db.Column(db.String(50)) 
    content = db.Column(db.String) 
    date = db.Column(db.Date)
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'title': self.title,
            'content': self.content,
            'date': self.date,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# RESEARCH PROJECTS
  
class FISResearchProjects(db.Model):
    __tableName__ = 'FISResearchProjects'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    project_title = db.Column(db.String(50)) 
    status = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'project_title': self.project_title,
            'status': self.status,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISADVISING
  
class FISAdvising(db.Model):
    __tableName__ = 'FISAdvising'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    student_id = db.Column(db.String(50)) 
    role = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'student_id': self.student_id,
            'role': self.role,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISMENTORING
  
class FISMentoring(db.Model):
    __tableName__ = 'FISMentoring'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    year = db.Column(db.String(50)) 
    course = db.Column(db.String(50)) 
    section = db.Column(db.String(50)) 
    number_students = db.Column(db.Integer) 
    type = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'year': self.year,
            'course': self.course,
            'section': self.section,
            'number_students': self.number_students,
            'type': self.type,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISCOMMITTEES
  
class FISCommittee(db.Model):
    __tableName__ = 'FISCommittee'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    FIScommittee_Name = db.Column(db.String(50)) 
    role = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'FIScommittee_Name': self.FIScommittee_Name,
            'role': self.role,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# COLLABORATION AND OPPORTUNITIES
  
class FISCollaborationOpportunities(db.Model):
    __tableName__ = 'FISCollaborationOpportunities'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    description = db.Column(db.String) 
    funding_source = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'description': self.description,
            'funding_source': self.funding_source,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# PROFESSIONAL DEVELOPMENT
  
class FISProfessionalDevelopment(db.Model):
    __tableName__ = 'FISProfessionalDevelopment'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    activity_type = db.Column(db.String(50)) 
    description = db.Column(db.String) 
    date = db.Column(db.Date) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'activity_type': self.activity_type,
            'description': self.description,
            'date': self.date,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# FISFEEDBACK
  
class FISFeedback(db.Model):
    __tableName__ = 'FISFeedback'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    FISfeedback_type = db.Column(db.String(50)) 
    content = db.Column(db.String) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'activity_type': self.activity_type,
            'FISfeedback_type': self.FISfeedback_type,
            'content': self.content,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# TEACHING ACTIVITIES
  
class FISTeachingActivities(db.Model):
    __tableName__ = 'FISTeachingActivities'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    code = db.Column(db.String(50)) 
    course = db.Column(db.String(50)) 
    section = db.Column(db.String(50)) 
    subject = db.Column(db.String(50)) 
    status = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'code': self.code,
            'course': self.course,
            'section': self.section,
            'subject': self.subject,
            'status': self.status,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# ASSIGNMENT TYPES
  
class FISAssignmentTypes(db.Model):
    __tableName__ = 'FISAssignmentTypes'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True) # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    course = db.Column(db.String(50)) 
    section = db.Column(db.String(50)) 
    subject = db.Column(db.String(50)) 
    activity = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'course': self.course,
            'section': self.section,
            'subject': self.subject,
            'activity': self.activity,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# TEACHING ASSIGNMENTS
  
class FISTeachingAssignments(db.Model):
    __tableName__ = 'FISTeachingAssignments'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID
    semester = db.Column(db.String(50)) 
    code = db.Column(db.String(50)) 
    course = db.Column(db.String(50)) 
    section = db.Column(db.String(50)) 
    number_students = db.Column(db.String(50)) 
    course_load = db.Column(db.String(50)) 
    course_type = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'semester': self.semester,
            'code': self.code,
            'course': self.course,
            'section': self.section,
            'number_students': self.number_students,
            'course_load': self.course_load,
            'course_type': self.course_type,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------

# ------------------------------------------------
# MANDATORY REQUIREMENTS
  
class FISMandatoryRequirements(db.Model):
    __tableName__ = 'FISMandatoryRequirements'

    id = db.Column(db.Integer, primary_key=True)  # DataID
    FacultyId = db.Column(db.Integer, db.ForeignKey('FISFaculty.FacultyId'), nullable=True)  # FacultyID
    # AdminId = db.Column(db.Integer, db.ForeignKey('FISAdmin.AdminId'), nullable=True)  # AdminID 
    requirement_item = db.Column(db.String(50)) 
    is_delete = db.Column(db.Boolean, default=False) 
    

    def to_dict(self):
        return {
            'id': self.id,
            'FacultyId': self.FacultyId,
            # 'AdminId': self.AdminId,
            'requirement_item': self.requirement_item,
            'is_delete': self.is_delete
        }
        
    def get_id(self):
        return str(self.id)  # Convert to string to ensure compatibility  

# ------------------------------------------------


def init_db(app):
    db.init_app(app)
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('FISFaculty'):
            db.create_all()
            # create_sample_data()
        
# #=====================================================================================================
# # INSERTING DATA
# def create_sample_data():
        
#  # Create and insert FISFaculty
 
# #     faculty_sample1 = FISFaculty(
# #         FacultyId='2020-00072-D-1',
# #         FacultyType='Full Time',
# #         Rank='Associate Professor II',
# #         Units = 8,
# #         Name='Alma Matter',
# #         FirstName='Palma',
# #         LastName='Matter',
# #         MiddleName='Bryant',
# #         MiddleInitial='B',
# #         NameExtension='',
# #         BirthDate= datetime.now(timezone.utc),
# #         DateHired= datetime.now(timezone.utc),
# #         Degree='Bachelor of Science in Computer Science',
# #         Remarks='',
# #         FacultyCode=91801,
# #         Honorific='N/A',
# #         Age=35,
# #         Email='alma123@gmail.com',
# #         Password=generate_Password_hash('alma123'),
# #         # Add more attributes here
# #         )
    
# #     faculty_sample2 = FISFaculty(
# #         FacultyId='2020-00073-D-1',
# #         FacultyType='Part Time',
# #         Rank='Instructor I',
# #         Units = 6,
# #         Name='Andrew Bardoquillo',
# #         FirstName='Andrew',
# #         LastName='Bardoquillo',
# #         MiddleName='Lucero',
# #         MiddleInitial='L',
# #         NameExtension='',
# #         BirthDate= datetime.now(timezone.utc),
# #         DateHired= datetime.now(timezone.utc),
# #         Degree='Master in Business Administration',
# #         Remarks='',
# #         FacultyCode=51295,
# #         Honorific='N/A',
# #         Age=26,
# #         Email='robertandrewb.up@gmail.com',
# #         Password=generate_Password_hash('plazma@123'),
# #         # Add more attributes here
# #         ) 
    
# #     faculty_sample3 = FISFaculty(
# #         FacultyId='2020-00076-D-4',
# #         FacultyType='Full Time',
# #         Rank='Instructor III',
# #         Units = 12,
# #         Name='Jason Derbis',
# #         FirstName='Jason',
# #         LastName='Derbis',
# #         MiddleName='Lucero',
# #         MiddleInitial='L',
# #         NameExtension='Jr.',
# #         BirthDate= datetime.now(timezone.utc),
# #         DateHired= datetime.now(timezone.utc),
# #         Degree='Master In Information Technology',
# #         Remarks='N/A',
# #         FacultyCode=81214,
# #         Honorific='N/A',
# #         Age=29,
# #         Email='sample123@gmail.com',
# #         Password=generate_Password_hash('plazma@123'),
# #         # Add more attributes here
# #         ) 
  
#     # # ADD  DATA
    
#     # db.session.add(admin_sample1)
#     # db.session.add(admin_sample2)
 
#     # # COMMIT 
    
#     # db.session.commit()
#     # db.session.close()
    
    