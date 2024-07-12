import psycopg2
import os
from datetime import *
from dotenv import load_dotenv
import uuid

from fastapi import HTTPException

conn = None
cursor = None

def connect_to_database():
    global conn, cursor
    
    # Load environment variables from .env file
    load_dotenv(override=True)

    # Get environment variables
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )
        cursor = conn.cursor()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        raise
    
    return cursor, conn

def close_database_connection():
    global conn, cursor
    
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def get_user_by_email(email):
    email = email.lower()
    register = "SELECT userID, name, admin, email FROM UserTable WHERE email = %s"
    cursor.execute(register, (email,))
    data = cursor.fetchone()
    if data==None:
        return None
    userData = {
        "id": data[0],
        "name": data[1],
        "admin": data[2],
        "email": data[3]
        }
    return userData

def get_user_by_id(user_id):
    if is_valid_uuid(user_id) == False:
        raise HTTPException(status_code=401, detail="Ogiltigt användar-id")
    
    register = "SELECT userID, name, admin, email FROM UserTable WHERE userID = %s"
    cursor.execute(register, (user_id,))
    data = cursor.fetchone()

    if data==None:
        raise HTTPException(status_code=401, detail="Användare saknas")
    
    userData = {
        "id": data[0],
        "name": data[1],
        "admin": data[2],
        "email": data[3]
        }
    
    return userData

def user_exists(user_id):
    if is_valid_uuid(user_id) == False:
        raise HTTPException(status_code=401, detail="Ogiltigt användar-id")
    
    query = "SELECT userID, name, admin FROM UserTable WHERE userID = %s"
    cursor.execute(query, (user_id,))
    data = cursor.fetchone()

    if data==None:
        return False
    else:
        return True

def create_user(name, email, admin):
    query = "INSERT INTO UserTable (name, email, admin) VALUES (%s, %s, %s) RETURNING userID"
    cursor.execute(query, (name, email, admin))
    user_id = cursor.fetchone()[0]
    
    conn.commit()
    
    return user_id

def authorizeUser(req_user_id):
    if req_user_id == None:
        raise HTTPException(status_code=401, detail="Saknar användar-id i cookies")
    
    # Validate the user which tries to create an admin user
    req_user_data = get_user_by_id(req_user_id)
    if req_user_data == None:
        raise HTTPException(status_code=401, detail="Ogiltig användare-id i cookies")
    
    return req_user_data

def visit_exists(visit_id):
    check_query = f'''select visitid from visit where visitid = %s'''
    cursor.execute(check_query, (visit_id,))
    if cursor.fetchone() == None:
        return False
    else:
        return True
    
def business_exists_by_name(business_name):
    check_query = f'''select businessid from business where name = %s'''
    cursor.execute(check_query, (business_name,))
    if cursor.fetchone() == None:
        return False
    else:
        return True
    
def business_exists_by_id(business_id):
    check_query = f'''select businessid from business where businessid = %s'''
    cursor.execute(check_query, (business_id,))
    if cursor.fetchone() == None:
        return False
    else:
        return True
    
def date_format(chosenDate):
    todaysDate = datetime.now().date()
    if len(chosenDate) == 10 and chosenDate[4] == chosenDate[7] == "-" and chosenDate[:4].isdigit() and chosenDate[5:7].isdigit() and chosenDate[8:].isdigit():
            chosenDate = datetime.strptime(chosenDate, "%Y-%m-%d").date()
            if chosenDate < todaysDate:
                return False
            else:
                return chosenDate
    else:
        return False
    
def valid_length(length):
    if length > 0:
        return timedelta(minutes=length)
    else:
        return None

def convert_time(time_input):
    if len(time_input) == 5 and time_input[2] == ":" and time_input[:2].isdigit() and time_input[3:].isdigit():
        if 00 <= int(time_input[:2]) <= 23 and 00 <= int(time_input[3:]) <= 59:
            return datetime.strptime(time_input, "%H:%M").time()
        else:
            return False
    else:
        return False

def time_format(startTime, endTime):
        if len(startTime) == 5 and startTime[2] == ":" and startTime[:2].isdigit() and startTime[3:].isdigit():
            if 00 <= int(startTime[:2]) <= 23 and 00 <= int(startTime[3:]) <= 59:
                startTime = datetime.strptime(startTime, "%H:%M").time()
            else:
                return False
        else:
            return False
        
        if len(endTime) == 5 and endTime[2] == ":" and endTime[:2].isdigit() and endTime[3:].isdigit():
            if 00 <= int(endTime[:2]) <= 23 and 00 <= int(endTime[3:]) <= 59:
                endTime = datetime.strptime(endTime, "%H:%M").time()
            else:
                return False
        else:
            return False
        
        return accepted_time(startTime, endTime)
    
def accepted_time(start, end):
    if start < end:
        return True
    else:
        return False
    
def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def slot2meeting(user, datum, start_time, end_time, duration, title):
    
    start_delta = timedelta(hours=start_time.hour, minutes=start_time.minute)
    end_delta = timedelta(hours=end_time.hour, minutes=end_time.minute)
    available_time = end_delta - start_delta
    
    end_time_delta = start_delta + duration
    
    if available_time >= duration and end_time_delta <= end_delta:
        insert_meeting = f"INSERT INTO AvailableMeeting VALUES (Default, True, %s, %s) RETURNING meetingId"
        cursor.execute(insert_meeting, (user, title ))
        meetingId = cursor.fetchone()[0]
        
        total_time_hours, total_time_minutes = divmod(end_time_delta.seconds, 3600)
        new_end_time = time(total_time_hours, total_time_minutes // 60)
        
        
        insert_info = f"INSERT INTO Info VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_info, (meetingId, datum, start_time.strftime("%H:%M:%S"), new_end_time.strftime("%H:%M:%S")))
        conn.commit()
        # print(f"Nytt möte: datum {datum} starttid {start_time}, sluttid {new_end_time}, längd {duration}")

        return slot2meeting(user, datum, new_end_time, end_time, duration, title)+1
    else:
        return 0