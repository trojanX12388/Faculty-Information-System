import requests
from addict import Dict

api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJrZXkiOiJjNmYzMDFjZTg3OWE0M2YwOWMyZWYyZjUzODk1YjY1OSJ9.L0Xs2-s2hAhnOuUEyciVLPHOHDtH3OAeC_UgoMP3X64'

access = requests.get(f"http://127.0.0.1:8000/api/all/faculty_data?token={api_key}")

data = access.json()


# SAMPLE FETCH SPECIFIC FACULTY DATA THROUGH ID

id = "2020-00073-D-1"

for j in data['FIS_data'][0]['faculty']:
    try:
        for i in j[id]:
                print('id:',id),
                print('First Name : ',i['first_name'])
                print('Last Name : ',i['last_name'])
                print('Middle Name : ',i['middle_name'])
                print('Email : ',i['email'])
                print('Age : ',i['age'])
                print('Employee Code : ',i['employee_code'])
                print('Remarks : ',i['remarks'])
                print('Honorific : ',i['honorific'])
                print('Sex : ',i['PDS_Data']['PDS_Personal_Details'][0]['sex'])
                print('Religion : ',i['PDS_Data']['PDS_Personal_Details'][0]['religion'])
                print("\n")
                
    except:
        pass
         
