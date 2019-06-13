import unicodecsv
with open("Enrollments.csv","rb") as fp:
    freader=unicodecsv.DictReader(fp)
    enroll=list(freader)
with open("engagement.csv","rb") as fp:
    freader=unicodecsv.DictReader(fp)
    engage=list(freader)
with open("proj.csv","rb") as fp:
    freader=unicodecsv.DictReader(fp)
    proj=list(freader)


from datetime import datetime
def parsedate(date):
    if date=="":
        return None
    else:
        return datetime.strptime(date,"%Y-%m-%d")
def parseday(day):
    if day=="":
        return None
    else:
        return float(day)
for enrollment in enroll:
    enrollment['days_to_cancel']=parseday(enrollment['days_to_cancel'])
    enrollment['cancel_date']=parsedate(enrollment['cancel_date'])
    enrollment['join_date']=parsedate(enrollment['join_date'])
    enrollment['is_udacity']=enrollment['is_udacity']=="True"
    enrollment['is_canceled']=enrollment['is_canceled']=="True"

for enrollment in engage:
    enrollment['utc_date']=parsedate(enrollment['utc_date'])
    enrollment['num_courses_visited'] = int(float(enrollment['num_courses_visited']))
    enrollment['total_minutes_visited']=float(enrollment['total_minutes_visited'])
    enrollment['lessons_completed']=int(float(enrollment['lessons_completed']))
    enrollment['projects_completed']=int(float(enrollment['projects_completed']))

for enrollment in proj:
    enrollment['creation_date']=parsedate(enrollment['creation_date'])
    enrollment['completion_date']=parsedate(enrollment['completion_date'])


print("The Number of Enrollments:",len(enroll),"\nNumber of engagements:",len(engage),"\nNumber of Project Submissions:",len(proj))
print("\n")

unique_enrolled_students = set()
#students may have enrolled first, then cancelled and enrolled again,

for enrollment in enroll:
    unique_enrolled_students.add(enrollment['account_key'])
print("Number of Unique Enrollments:",len(unique_enrolled_students))

def engagee(engage):
    unique_engagement_students = set()
    for engagement_record in engage:
        unique_engagement_students.add(engagement_record['account_key'])
    return unique_engagement_students

unique_engagement_students=engagee(engage)
print("Unique Engagements:",len(unique_engagement_students))



unique_project_submitters = set()
for submission in proj:
    unique_project_submitters.add(submission['account_key'])
print("Unique Project Submissions:",len(unique_project_submitters))

#Check for who enrolled and and not engaged
print("who enrolled and and not engaged\n")
for enrollment in enroll:
    student = enrollment['account_key']
    if student not in engage:
        break

#Check for number of people who enrolled and not engaged
num_problem_students = 0
for enrollment in enroll:
    student = enrollment['account_key']
    if (student not in unique_engagement_students and 
            enrollment['join_date'] != enrollment['cancel_date']):
        print(enrollment)
        num_problem_students += 1
print("\n")
print("Number of people who enrolled and not engaged",num_problem_students)
print("\n")
#check for test accounts, remove them
udacity_testaccc=set()
for enrool in enroll:
    if enrool["is_udacity"]==True:
        udacity_testaccc.add(enrool["account_key"])
print("Udacity test accounts:",udacity_testaccc)

def remov(data):
    origaccc=[]
    for datag in data:
        if datag["account_key"] not in udacity_testaccc:
            origaccc.append(datag)
    return origaccc

noUdEnroll=remov(enroll)
noUdEngage=remov(engage)
noUdproj=remov(proj)
print("\n")
print("NUmber of Enrollments,Engagements,Project Submissions without Udacity Test accounts:",len(noUdEnroll),len(noUdEngage),len(noUdproj))
print("\n")
#Check for students succesfully paid and joined
paid_students = {}
for enrollment in noUdEnroll:
    if (not enrollment['is_canceled'] or
            enrollment['days_to_cancel'] > 7):
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
        if (account_key not in paid_students or
                enrollment_date > paid_students[account_key]):
            paid_students[account_key] = enrollment_date
print("\n")
print("Paid and Joined",len(paid_students))
print("\n")
print("Check for the students engagement in one week")
print("check that student's data of submitted project sucessfully vs Not Done")


def within_one_week(join_date, engagement_date):
    time_delta = engagement_date - join_date
    return time_delta.days < 7 and time_delta.days >= 0 

def remove_free_trial_cancels(data):
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data

paid_enrollments = remove_free_trial_cancels(noUdEnroll)
paid_engagement = remove_free_trial_cancels(noUdEngage)
paid_submissions = remove_free_trial_cancels(noUdproj)
print("\n")
print("After paying Enrollments:",len(paid_enrollments))
print("After paying Engagements:",len(paid_engagement))
print("After paying Submissions:",len(paid_submissions))
print("\n")
#Checking how many engagement records 
paid_engagement_in_first_week = []
for engagement_record in paid_engagement:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_record_date = engagement_record['utc_date']

    if within_one_week(join_date, engagement_record_date):
         paid_engagement_in_first_week.append(engagement_record)

print("Paid people's engagements in first week:",len(paid_engagement_in_first_week))

#to count working days
for engagement_record in paid_engagement:
    if engagement_record['num_courses_visited'] > 0:
        engagement_record['has_visited'] = 1
    else:
        engagement_record['has_visited'] = 0


#store each user account with all enagagement records
from collections import defaultdict

def group_data(data, key_name):
    grouped_data = defaultdict(list)
    for data_point in data:
        key = data_point[key_name]
        grouped_data[key].append(data_point)
    return grouped_data

engagement_by_account = group_data(paid_engagement_in_first_week,
                                   'account_key')

def sum_grouped_items(grouped_data, field_name):
    summed_data = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
        summed_data[key] = total
    return summed_data

total_minutes_by_account = sum_grouped_items(engagement_by_account,
                                             'total_minutes_visited')


import matplotlib.pyplot as plt
import numpy as np
def describe_data(data):
    print('Mean:', np.mean(data))
    print('Standard deviation:', np.std(data))
    print('Minimum:', np.min(data))
    print('Maximum:', np.max(data))
print("Total Minutes watched:")    
describe_data(list(total_minutes_by_account.values()))
print("Lessons Completed")
lessons_completed_by_account = sum_grouped_items(engagement_by_account,
                                                 'lessons_completed')
describe_data(list(lessons_completed_by_account.values()))
print("Days Visited")
days_visited_by_account = sum_grouped_items(engagement_by_account,
                                            'has_visited')
describe_data(list(days_visited_by_account.values()))

#A project submission Student's after performance

subway_project_lesson_keys = ['746169184', '3176718735']

pass_subway_project = set()

for submission in paid_submissions:
    project = submission['lesson_key']
    rating = submission['assigned_rating']    

    if ((project in subway_project_lesson_keys) and
            (rating == 'PASSED' or rating == 'DISTINCTION')):
        pass_subway_project.add(submission['account_key'])

print('Number of students submitted and passsed',len(pass_subway_project))

passing_engagement = []
non_passing_engagement = []

for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] in pass_subway_project:
        passing_engagement.append(engagement_record)
    else:
        non_passing_engagement.append(engagement_record)

print("Passing students Engagements:",len(passing_engagement))
print("Non Passing Students Engagements:",len(non_passing_engagement))

##Describes all data regarding Minutes ,lessons,visits
##
##
passing_engagement_by_account = group_data(passing_engagement,
                                           'account_key')
non_passing_engagement_by_account = group_data(non_passing_engagement,
                                               'account_key')
print("\n")
print("Minutes")
print('non-passing students:')

non_passing_minutes = sum_grouped_items(
    non_passing_engagement_by_account,
    'total_minutes_visited'
)

describe_data(list(non_passing_minutes.values()))

print('passing students:')

passing_minutes = sum_grouped_items(
    passing_engagement_by_account,
    'total_minutes_visited'
)
describe_data(list(passing_minutes.values()))
print("\n")
print("lessons")
print('non-passing students:')
          
non_passing_lessons = sum_grouped_items(
    non_passing_engagement_by_account,
    'lessons_completed'
)
describe_data((list(non_passing_lessons.values())))

print('passing students:')
              
passing_lessons = sum_grouped_items(
    passing_engagement_by_account,
    'lessons_completed'
)
describe_data((list(passing_lessons.values())))
print("\n")
print("Visits")
print('non-passing students:')
              
non_passing_visits = sum_grouped_items(
    non_passing_engagement_by_account, 
    'has_visited'
)
describe_data((list(non_passing_visits.values())))

print('passing students:')
              
passing_visits = sum_grouped_items(
    passing_engagement_by_account,
    'has_visited'
)
describe_data((list(passing_visits.values())))
##
##
##
import matplotlib.pyplot as plt
import seaborn as sns

plt.hist(non_passing_visits.values(), bins=8)
plt.xlabel('Number of days')
plt.title('Distribution of classroom visits in the first week ' + 
          'for students who do not pass the subway project')



















