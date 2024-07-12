import psycopg2
import os
from datetime import *

from dotenv import load_dotenv

load_dotenv(override=True)
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST )

# Anslut till databasen
#conn = psycopg2.connect(host='localhost', user='postgres', password='felicia', dbname='vic') #använd denna och kommentera bort de två styckena över om du inte joxat med env grejer (jag har inte gjort det hehe)
cursor = conn.cursor()

def close_db():
    # Stäng cursor och anslutning när du är klar
    cursor.close()
    conn.close()

def available(groupName, groupId):
    visitDict = {}
    #Lägg till att endast se tider som inte har passerat
    today = date.today()
    #Where visitDate => dagens
    allVisits = availableVisits(groupId)

    if not allVisits:
        print(f"Företaget ({groupName}) har inga bokningsbara tider.")
    else:
        print(f"TILLGÄNGLIGA STUDIEBESÖK HOS {groupName.upper()}")
        print("-" * 50)
        print(f"{'Index'}   {'Titel':<{20}}  {'Företag'}  {'Datum'}      {'Starttid'}   {'Sluttid'}   {'Platser'}")
        
        for i, visit in enumerate(allVisits, start=1):
            visitID, businessID, visitDate, starttime, endtime, spots, userID, title , businessName= visit
            print(f"  {i}    {title:<{20}} {businessName} {visitDate}   {starttime}   {endtime}   {spots}")
            visitDict[i] = visitID
    return visitDict

def availableVisits(groupId):
    availableQuery = f'''
        SELECT visit.visitID, visit.businessID, visitDate, starttime, endtime, spots, userID, title, business.name
        FROM visit
        INNER JOIN GroupVisit ON groupVisit.visitid = visit.visitid
        INNER JOIN Business ON Business.businessID = visit.businessID 
        WHERE GroupVisit.groupID = %s
        ORDER BY visit.visitDate 
    '''
    cursor.execute(availableQuery, (groupId,))
    return cursor.fetchall()

def loginStudent():
    email = input("Ange din email: ")
    while '@' not in email:
        email = input("Ange din email: ")

    userID = getUserID(email)

    if userID == None:
        namn = input("Ange för och efternamn: ")
        insertNewUser(namn, email)
        userID = getUserID(email)
    else:
        return userID[0]

def getUserID(email):
    register = f'''SELECT userID FROM UserTable WHERE email = %s '''
    cursor.execute(register, (email,))
    return cursor.fetchone()

def insertNewUser(namn,email):
    newUser = f'''INSERT INTO UserTable VALUES (default, %s, %s, false)'''
    cursor.execute(newUser, (namn, email))
    conn.commit()

def bookVisit(student_id=""):
    print(f"{'='*30}\nBOKA IN DIG PÅ ETT STUDIEBESÖK\n{'='*30}")
    groupOptions = getDistinctGroups()
    print("Följande grupper har bokningsbara tider:")
    i = 1
    for option in groupOptions:
        print(str(i)+". "+option[0])
        i+=1
    while True:
        groupInput = input("Vad vill du gå på för studiebesök? Ange index för gruppen:\n")
        if not groupInput.isdigit() or int(groupInput) < 1 or int(groupInput) > len(groupOptions):
            print("Ange ett giltigt index.")
        else:
            break
    groupIndex = int(groupInput)
    groupName = groupOptions[groupIndex - 1][0] 
    groupID = getGroupID(groupName)
    visitdict = available(groupName, groupID)
    able2book = check_no_visits(groupID, student_id)

    while True:
        chosen = input("Ange index för det studiebesök du vill boka: ")
        if not chosen.isdigit() or int(chosen) not in visitdict:
            print("Ange ett giltigt index.")
        else:
            break
    if not able2book:
        print("\nDu har redan bokat in dig på max antal bokningar")
        print("Du måste avboka ett besök innan du kan boka ett nytt")
        return
    visitID = visitdict.get(int(chosen))
    
    if student_id=="": 
        studentID = loginStudent()
    else:
        studentID = student_id
    user_exist = checkIfBooked(visitID, studentID)
    
    if user_exist:
        print("Du är redan inbokad på detta studiebesök")
        return
    else:
        insertBookedVisit(visitID, studentID)
        updateNrOfSpots(visitID)
        print("Studiebesöket är bokat!")

def getDistinctGroups():
    groupOptionsQuery = "SELECT DISTINCT Groups.name FROM Groups JOIN groupVisit ON Groups.groupID = groupVisit.groupID"
    cursor.execute(groupOptionsQuery)
    return cursor.fetchall()

def getGroupID(groupName):
    groupQuery = f"SELECT groupID FROM Groups WHERE name = %s"
    cursor.execute(groupQuery, (groupName,))
    return cursor.fetchone()[0]

def checkIfBooked(visitID, studentID):
    already_booked = f'''SELECT Usertable.userID FROM UserTable INNER JOIN BookedVisit ON Usertable.userID = BookedVisit.UserID WHERE visitID = %s AND bookedVisit.UserID = %s'''
    cursor.execute(already_booked, (visitID, studentID))
    return cursor.fetchone()

def insertBookedVisit(visitID, studentID):
    booking = f'''INSERT INTO BookedVisit VALUES (%s, %s)'''
    cursor.execute(booking, (visitID, studentID))
    conn.commit()

def updateNrOfSpots(visitID):
    updateVisit = f'''UPDATE Visit SET spots = spots - 1 WHERE visitID = %s'''
    cursor.execute(updateVisit, (visitID,))
    conn.commit()

def check_no_visits(group_id, user_id):
    max_visit = getMaxNrOfVisits(group_id)
    booked_visit = getNrOfBookedVisits(group_id, user_id)
    if booked_visit >= max_visit:
        return False
    else:
        return True

def getMaxNrOfVisits(group_id): 
    max_group = f'''SELECT maxvisit FROM Groups WHERE groupID = %s'''
    cursor.execute(max_group, (group_id,))
    return cursor.fetchone()[0]

def getNrOfBookedVisits(group_id, user_id):
    booked_visits = f'''SELECT count(userID) FROM BookedVisit INNER JOIN GroupVisit ON
    GroupVisit.visitID = BookedVisit.visitID WHERE GroupVisit.groupID = %s AND
    BookedVisit.userID = %s'''
    cursor.execute(booked_visits, (group_id, user_id))
    return cursor.fetchone()[0]

def main():
    bookVisit()

if __name__=="__main__":
    main()

    close_db()
