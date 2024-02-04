import requests

response = requests.get('https://univ-ems.onrender.com/api/extension-programs')

if response.status_code == 200:
    programs = response.json()
else:
    print('error')


print("Extension Programs:", end=' ')
for program in programs:
    print(program['Name'], end=', ')


print('\n\nDetailed Information for each Extension Program')
for program in programs:
    print('Extension Program Id:', program['ExtensionProgramId'])
    print('Extension Program:', program['Name'])
    print('Rationale:', program['Rationale'])
    print('ImageUrl:', program['ImageUrl']) # html w/ jinja:  <img src="{{ program['ImageUrl'] }}">
    print('Agenda:', program['Agenda']['AgendaName']) 
    print('Course/Program:', program['Program']['ProgramName'])
    print('Projects under', program['Name'], 'program:')
    if program['Projects']:
        for project in program['Projects']:
            print('\tProject Id:', project['ProjectId'])
            print('\tProject Title: ', project['Title'])
            print('\tImplementer:', project['Implementer'])
            print('\tProject Team:', end=' ')
            for id in project['ProjectTeam']:
                print(project['ProjectTeam'][id], end=', ')
            print('\n\tTarget Group:', project['TargetGroup'])
            print('\tProject Type:', project['ProjectType'])
            print('\tStart Date', project['StartDate'])
            print('\tEnd Date', project['EndDate'])
            print('\tProposed Budget:', project['ProposedBudget'])
            print('\tApproved Budget:', project['ApprovedBudget'])
            print('\tFund Type:', project['FundType'])
            print('\tImpact Statement:', project['ImpactStatement']) # using jinja: {{ project['ImpactStatement']|safe }}
            print('\tObjectives:', project['Objectives']) # using jinja: {{ project['Objectives']|safe }}
            print('\tStatus:', project['Status'])
            print('\tImageUrl:', project['ImageUrl']) # html w/ jinja:  <img src="{{ project['ImageUrl'] }}">
            print('\tProject Proposal:', project['ProjectProposalUrl']) # Link for document file
            print('\tLead Proponent:', project['LeadProponent']['FirstName'], project['LeadProponent']['LastName'])
            print('\tCollaborator:', project['Collaborator']['Organization'])
            print('\tActivities under', project['Title'], 'project:')
            if project['Activity']:
                for activity in project['Activity']:
                    print('\t\tActivity Id:', activity['ActivityId'])
                    print('\t\tActivity Name', activity['ActivityName'])
                    print('\t\tDate:', activity['Date'])
                    print('\t\tDescription', activity['Description'])
                    print('\t\tLocation:', activity['Location'])
                    print('\t\tImage Url:', activity['ImageUrl'])
                    print('\t\tSpeaker:', end=' ')
                    for id in activity['Speaker']:
                        print(activity['Speaker'][id], end=', ')
            else:
                print('\t\tNo activities under this project')
            print('\n')
    else:
        print('\tNo projects under this program')


# Fetch project for specific faculty
        
first_name = 'Alma'
last_name = 'Fernandez'

projects_list = []

print("Projects of", first_name, last_name)
for project in program['Projects']:
    if project['LeadProponent']['FirstName'] == first_name and project['LeadProponent']['LastName'] == last_name:
        projects_list.append(project)

for project in projects_list:
    print('Project Id:', project['ProjectId'])
    print('Project Title: ', project['Title'])
    print('Implementer:', project['Implementer'])
    print('Project Team:', end=' ')
    for id in project['ProjectTeam']:
        print(project['ProjectTeam'][id], end=', ')
    print('\nTarget Group:', project['TargetGroup'])
    print('Project Type:', project['ProjectType'])
    print('Start Date', project['StartDate'])
    print('End Date', project['EndDate'])
    print('Proposed Budget:', project['ProposedBudget'])
    print('Approved Budget:', project['ApprovedBudget'])
    print('Fund Type:', project['FundType'])
    print('Impact Statement:', project['ImpactStatement']) # using jinja: {{ project['ImpactStatement']|safe }}
    print('Objectives:', project['Objectives']) # using jinja: {{ project['Objectives']|safe }}
    print('Status:', project['Status'])
    print('ImageUrl:', project['ImageUrl']) # html w/ jinja:  <img src="{{ project['ImageUrl'] }}">
    print('Project Proposal:', project['ProjectProposalUrl']) # Link for document file
    print('Collaborator:', project['Collaborator']['Organization'])
    print('Activities under', project['Title'], 'project:')
    if project['Activity']:
        for activity in project['Activity']:
            print('\tActivity Id:', activity['ActivityId'])
            print('\tActivity Name', activity['ActivityName'])
            print('\tDate:', activity['Date'])
            print('\tDescription', activity['Description'])
            print('\tLocation:', activity['Location'])
            print('\tImage Url:', activity['ImageUrl'])
            print('\tSpeaker:', end=' ')
            for id in activity['Speaker']:
                print(activity['Speaker'][id], end=', ')
    else:
        print('\tNo activities under this project')
    print('\n')