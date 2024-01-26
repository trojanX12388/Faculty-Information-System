import requests

# Your API endpoint
url = 'https://pupqcfis-com.onrender.com/api/all/FISFaculty'


# Make a GET request to the API with the API key in the headers
response = requests.get(url)

if response.status_code == 200:
    # Process the API response data
    api_data = response.json()
    print("Success Fetch api data:" + str(response.status_code))
    
    # RETURNING SPECIFIC DATA FROM ALL FACULTIES
    
    # Extracting faculty_account_ids into a list
    faculty_account_ids = list(api_data['Faculties'].keys())

    # Fetching Specific data for each faculty
    for faculty_id in faculty_account_ids:
        faculty_info = api_data['Faculties'][faculty_id]
        faculty_rank = faculty_info['Rank']
        faculty_name = faculty_info['LastName']
        faculty_email = faculty_info['Email']
        faculty_PDS_Personal_Details = faculty_info['FISPDS_PersonalDetails']
        faculty_PDS_Contact_Details = faculty_info['FISPDS_ContactDetails']

        print("\nFaculty ID:", faculty_id)
        print("Rank:", faculty_rank)
        print("Name:", faculty_name)
        print("Email:", faculty_email)
        print("FISPDS_PersonalDetails:", faculty_PDS_Personal_Details)
        print("FISPDS_ContactDetails:", faculty_PDS_Contact_Details)

    
    # RETURNING API DATA FROM EACH ATTRIBUTES

    print("\n\nEXAMPLE FETCH\n")
    print("FACULTY DATA")
    print(api_data['Faculties']['10009'])
    print("\n\nFACULTY SPECIFIC DATA")
    print(api_data['Faculties']['10012']['LastName'])
    print(api_data['Faculties']['10012']['Email'])
    print(api_data['Faculties']['10012']['Rank'])
    
else:
    print("Failed to fetch data. Status code:", response.status_code)
    



