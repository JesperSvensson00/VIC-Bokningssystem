from fastapi import HTTPException, Header, Request
from fastapi.responses import FileResponse
from fastapi import FastAPI, Response
from pydantic import BaseModel

from helper import valid_email
from database import *
from bookedVisit import check_no_visits, checkIfBooked, insertBookedVisit, updateNrOfSpots

from dotenv import load_dotenv
import os

def setup_routes(app: FastAPI, cursor, conn):
    class LoginBody(BaseModel):
        email: str
    
    class CreateUserBody(BaseModel):
        email: str
        name: str
        admin: bool = False
    
    class UpdateUserBody(BaseModel):
        email: str = None
        name: str = None
        admin: bool = None
    
    class CreateMeetingBody(BaseModel):
        attendee_id: str = None
        title: str
        date: str
        start_time: str
        end_time: str
        length: int
        
    class BookingInfoBody(BaseModel):
        message: str

    class CreateGroupBody(BaseModel):
        name: str
        max_visit: int

    class CreateVisitBody(BaseModel):
        visit_title: str
        business_id: str
        date: str
        start_time: str
        end_time: str
        number_of_spots: int

    class CreateBusinessBody(BaseModel):
        address: str
        name: str
        info: str

    class UpdateBusinessBody(BaseModel):
        address: str
        name: str
        info: str
        
    class TestBody(BaseModel):
        val: str

        
    @app.get("/api/test")
    def test(testData: TestBody, req: Request):
        print(testData.val)
        print("Kaka: ", req.cookies)
        return {"message": f"Test route, val: {testData.val}"}

    @app.post("/api/login")
    def login(credentials: LoginBody, res: Response):
        print(credentials.email)
        user_data = get_user_by_email(credentials.email)
        if user_data == None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Sätt en cookie med användar-id, valid i 1 dag
        res.set_cookie(key="userId", value=user_data["id"], httponly=True, samesite="strict", max_age=60*60*24)
        res.headers["Access-Control-Allow-Credentials"] = "true"
        return {"id": user_data["id"], "name": user_data["name"], "admin": user_data["admin"]}
    
    
    @app.get("/api/user/{id}")
    def read_user(id: str, req: Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id)
        
        # Om användaren inte är admin och försöker hämta en annan användares data
        if str(req_user["id"]) != id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        user_data = get_user_by_id(id)
        return {"message": f"Get user {id}", "user": user_data}
    
    @app.post("/api/user")
    def post_user(userData: CreateUserBody, req: Request):
        req_user_id = req.cookies.get("userId")
        if userData.admin == True:
            req_user = authorizeUser(req_user_id)
            if req_user["admin"] == False:
                raise HTTPException(status_code=401, detail="Unauthorized, missing permission")
            
        # Kolla om användaren redan finns
        user_exists = get_user_by_email(userData.email)
        if user_exists != None:
            raise HTTPException(status_code=400, detail="Användaren finns redan")
        
        # Validera namnet
        if userData.name == None or len(userData.name) < 3:
            raise HTTPException(status_code=400, detail="Namnet du angav är för kort")
        
        # Validera e-postadressen
        if userData.email == None or not valid_email(userData.email):
            raise HTTPException(status_code=400, detail="Ogiltig e-postadress")
        
        user_id = create_user(userData.name, userData.email.lower(), userData.admin)
        
        user = {"id": user_id, "name": userData.name, "email": userData.email.lower(), "admin": False}
         
        # Create user in database
        return {"message": "User created", "user_id": user_id, "admin": userData.admin, "user": user}
    
    @app.put("/api/user/{id}")
    def update_user(userData: UpdateUserBody, id: str, req: Request):
        req_user_id = req.cookies.get("userId") # Kaka som skickas med i requesten är None om användaren inte är inloggad
        req_user = authorizeUser(req_user_id) # Om användaren inte är inloggad kastas en exception
        
        # Om användaren inte är admin måste den användaren som gör ändringen vara den som ska uppdateras
        if req_user["admin"] == False and req_user_id != id:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        # Det är bara admin som får ändra admin-status
        if userData.admin and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        # Om det inte finns någon data görs ingen ändring
        if userData.email == None and userData.name == None and userData.admin == None:
            raise HTTPException(status_code=400, detail="Ingen data att uppdatera")
        
        if userData.email != None and not valid_email(userData.email):
            raise HTTPException(status_code=400, detail="Ogiltig e-postadress")

        if userData.name != None and len(userData.name) < 3:
            raise HTTPException(status_code=400, detail="Namnet du angav är för kort")
        
        if userData.email != None:
            userData.email = userData.email.lower()
        
        # Skapa query för varje attribut som ska uppdateras
        nameClause = "name = %s," if userData.name != None else ""
        emailClause = "email = %s," if userData.email != None else ""
        adminClause = "admin = %s," if userData.admin != None else ""
        update_q = f"UPDATE UserTable SET {nameClause} {emailClause} {adminClause} WHERE userID = %s RETURNING *"
        update_q = update_q.replace(", WHERE", " WHERE") # Remove trailing comma if no data to update
        
        # Uppdaterar i databasen
        updatedParams = [param for param in [userData.name, userData.email, userData.admin, id] if param != None]
        cursor.execute(update_q, updatedParams)
        updatedUser = cursor.fetchone()
        
        # Om användaren inte fanns
        if updatedUser == None:
            raise HTTPException(status_code=404, detail="Användaren finns inte")
        
        conn.commit()
        
        return {"message": f"Update user {id} by user {req_user_id}", "user": updatedUser}
    
    @app.delete("/api/user/{identifier}")
    def delete_user(identifier: str, req: Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id) # Om användaren inte är inloggad kastas en exception
        
        # Om användaren inte är admin får den inte ta bort användare
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        # Checkar om identifier är en e-postadress eller användar-id
        if "@" in identifier:
            q = "SELECT userID FROM UserTable WHERE email = %s"
                
        elif "-" in identifier:
            q = "SELECT userID FROM UserTable WHERE userID = %s"
            
        else:
            raise HTTPException(status_code=400, detail="Ogiltigt format på användar-id eller e-postadress")
        
        cursor.execute(q, (identifier.lower(),))
        userID = cursor.fetchone()
        
        # Om användaren inte finns
        if userID == None:
            print("Ingen användare med email", identifier ,"finns registrerad")
            raise HTTPException(status_code=404, detail="Användaren finns inte")
        
        # Om användaren är inbokad på ett möte, ta bort bokningar först
        remove_user_query = "DELETE FROM bookedMeeting WHERE userID = %s"
        cursor.execute(remove_user_query, (userID,))
        update_availability_query = f"UPDATE availableMeeting SET available = True WHERE userID = %s"
        cursor.execute(update_availability_query, (userID,))
        conn.commit()
        
        # Om användaren är inbokad på ett studiebesök, ta bort bokningar först
        delete_query = "DELETE FROM bookedVisit WHERE userID = %s"
        cursor.execute(delete_query, (userID))
        update_visit = "UPDATE visit SET spots = spots + 1 WHERE userID = %s"
        cursor.execute(update_visit, (userID,))
        conn.commit()
        
        # Remove user if nothing have gone wrong
        query = "DELETE FROM UserTable WHERE userID = %s"
        cursor.execute(query, (userID,))
        print("Användaren med email",userID[0],"har tagits bort")
        conn.commit()
        
        return {"message": f"Användare {identifier} togs bort"}

    @app.get("/api/users")
    def get_users(req:Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id) # Om användaren inte är inloggad kastas en exception
        
        # Om användaren inte är admin får den inte se alla användare
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        query = "SELECT * FROM UserTable"
        cursor.execute(query)
        
        # Gör om data till en lista av dictionaries (lite skönare att använda i frontend)
        users = [{"id": data[0], "name": data[1], "email": data[2], "admin": data[3]} for data in cursor.fetchall()]
        
        return {"message": "All users", "users": users}
    
    @app.get("/api/admins")
    def get_admins(req:Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id)
        
        # Om användaren inte är admin får den inte se alla admins
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        query = "SELECT * FROM UserTable WHERE admin = True"
        cursor.execute(query)
        
        # Gör om data till en lista av dictionaries (lite skönare att använda i frontend)
        admins = [{"id": data[0], "name": data[1], "email": data[2], "admin": data[3]} for data in cursor.fetchall()]
        
        return {"message": "All admins", "admins": admins}
    
    @app.get("/api/admins/available")
    def read_admins(req: Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id)

        query = "select userid, name, email from usertable where userid in (select distinct userid from availablemeeting where available = true)"
        cursor.execute(query)
        
        # Gör om data till en lista av dictionaries (lite skönare att använda i frontend)
        admins = [{"id": data[0], "name": data[1], "email": data[2]} for data in cursor.fetchall()]
        
        return {"message": "Admins with meetings", "admins": admins}
    
    @app.get("/api/user/{id}/meetings")
    def get_meetings_for_user(id: str, req: Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id) # Om användaren inte är inloggad kastas en exception
        # Kolla om användaren är admin eller om det är användaren själv som hämtar möten
        if str(req_user["id"]) != id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        # Hämta möten för användaren
        meeting_query = f"""
                SELECT bookedmeeting.meetingid, visitdate, starttime, endtime, usertable.name, usertable.userid, bookedmeeting.message 
                FROM info 
                LEFT JOIN bookedmeeting ON bookedmeeting.meetingid = info.meetingid 
                LEFT JOIN availablemeeting ON availablemeeting.meetingid = info.meetingid
                LEFT JOIN usertable ON availablemeeting.userid = usertable.userid 
                WHERE bookedmeeting.userid = %s 
                ORDER BY visitdate, starttime
                """
        cursor.execute(meeting_query, (id,))
        meetings = cursor.fetchall()
    
        
        # Om admin kolla även dess skapade möten
        if req_user["admin"]:
            admin_meeting_query = f"""
                SELECT availablemeeting.meetingid, visitdate, starttime, endtime, usertable.name, usertable.userid, bookedmeeting.message
                FROM info
                LEFT JOIN availablemeeting ON availablemeeting.meetingid = info.meetingid
                LEFT JOIN bookedmeeting ON bookedmeeting.meetingid = info.meetingid
                LEFT JOIN usertable ON bookedmeeting.userid = usertable.userid 
                WHERE availablemeeting.userid = %s 
                ORDER BY visitdate, starttime
                """
            cursor.execute(admin_meeting_query, (id,))
            admin_meetings = cursor.fetchall()
            meetings += admin_meetings
        
        # Make data into a list of dictionaries
        meetingsData = []
        for meeting in meetings:
            meeting_id, visit_date, start_time, end_time, name, user_id, message = meeting
            booked_by = {"id": user_id, "name": name, "message": message} if user_id != None else {}
            meetingData = {"id": meeting_id, "date": visit_date, "start_time": start_time, "end_time": end_time, "booked_by": booked_by}
            meetingsData.append(meetingData) 
        
        return {"meetings": meetingsData}
    
    @app.get("/api/user/{id}/visits")
    def get_visits_for_user(id: str, req: Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id)
        
        # Kolla om användaren är admin eller om det är användaren själv som hämtar studiebesök
        if str(req_user["id"]) != id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        # Hämta studiebesök för användaren
        visit_query = f"""
        SELECT bookedvisit.visitid, visitDate, starttime, endtime, usertable.name, groups.name, business.name, title
                FROM visit
                LEFT JOIN bookedvisit ON bookedvisit.visitid = visit.visitid
                LEFT JOIN groupVisit ON groupVisit.visitid = visit.visitid
                LEFT JOIN usertable ON bookedvisit.userid = usertable.userid 
                LEFT JOIN business ON business.businessid = visit.businessid
                LEFT JOIN groups ON groupVisit.groupid = groups.groupid
                WHERE bookedvisit.userid = %s
                ORDER BY visitdate, starttime
                """
        cursor.execute(visit_query, (id,))
        visits = cursor.fetchall()
        
        # Make data into a list of dictionaries
        visitsData = []
        for visit in visits:
            visit_id, visit_date, start_time, end_time, name, group_name, business_name, title = visit
            visitData = {"id": visit_id, "date": visit_date, "start_time": start_time, "end_time": end_time, "name": name, "group_name": group_name, "business_name": business_name, "title": title}
            visitsData.append(visitData)
        
        return {"visits": visitsData}

    @app.get("/api/meetings/{creator_id}")
    def read_meetings(creator_id: str, req: Request):
        # Skicka tillbaka en lista med alla möten skapade av "creator"
        # För exempelvis admin att se alla möten som en användare skapat
        
        req_user_id = req.cookies.get("userId")
        get_user_by_id(creator_id) # Om användaren inte finns skickas ett fel
        
        # Bara en admin eller användaren själv får se alla möten som en användare skapat
        req_user = authorizeUser(req_user_id)
        if str(req_user["id"]) != creator_id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        
        query = '''
        SELECT AvailableMeeting.meetingid, AvailableMeeting.title, AvailableMeeting.available,  visitdate, starttime, endtime, UserTable.name 
        FROM Info
        LEFT JOIN availablemeeting ON availablemeeting.meetingid = info.meetingid
        LEFT JOIN UserTable ON AvailableMeeting.userid = UserTable.userid 
        WHERE AvailableMeeting.userid = %s 
        ORDER BY visitdate, starttime
        '''
        
        cursor.execute(query, (creator_id,))
        meetings = cursor.fetchall()

        meetings_data = [{"id": data[0], "title": data[1], "available": data[2], "date": data[3], "start_time": data[4], "end_time": data[5], "creator": data[6] } for data in meetings]
        return {"meetings": meetings_data}
        
    
    @app.get("/api/available-meetings/{identifier}")
    def read_available_meetings(identifier: str, req: Request):
        # Skicka tillbaka en lista med alla möten skapade av "creator" som är tillgängliga
        
        req_user_id = req.cookies.get("userId")
        
        # Kollar om identifier är en e-postadress eller så är det ett användar-id
        if "@" in identifier:
            creator_id = get_user_by_email(identifier)["id"]
            if creator_id == None:
                raise HTTPException(status_code=404, detail="Användaren finns inte")
        else:
            get_user_by_id(identifier)
            creator_id = identifier
        
        # Användaren måste vara inloggad för att se möten
        authorizeUser(req_user_id)
        
        
        query = '''
        SELECT AvailableMeeting.meetingid, AvailableMeeting.title, visitdate, starttime, endtime, UserTable.name 
        FROM Info
        LEFT JOIN AvailableMeeting ON availablemeeting.meetingid = info.meetingid
        LEFT JOIN UserTable ON AvailableMeeting.userid = UserTable.userid
        WHERE AvailableMeeting.userID = %s AND AvailableMeeting.available = True
        ORDER BY visitdate, starttime
        '''
        
        cursor.execute(query, (creator_id,))
        meetings = cursor.fetchall()

        meetings_data = [{"id": data[0], "title": data[1], "date": data[2], "start_time": data[3], "end_time": data[4], "creator": data[5] } for data in meetings]
        return {"meetings": meetings_data}
    
    @app.get("/api/meeting/{meeting_id}")
    def read_meeting(meeting_id: str, req: Request):
        # För att hämta information om ett möte
        req_user_id = req.cookies.get("userId")
        
        req_user = authorizeUser(req_user_id) # Om användaren inte är inloggad kastas en exception
        
        query = """
        SELECT AvailableMeeting.title, visitdate, starttime, endtime, UserTable.userID, UserTable.name, UserTable.email, bookedMeeting.userid
        FROM Info
        LEFT JOIN AvailableMeeting ON availablemeeting.meetingid = info.meetingid
        LEFT JOIN UserTable ON AvailableMeeting.userid = UserTable.userid
        LEFT JOIN bookedMeeting ON bookedMeeting.meetingid = info.meetingid
        WHERE AvailableMeeting.meetingid = %s
        """
        
        cursor.execute(query, (meeting_id,))
        meeting = cursor.fetchone()
        
        print(meeting[7])
        
        # Om mötet inte finns
        if meeting == None:
            raise HTTPException(status_code=404, detail="Mötet finns inte")
        
        creator_data = {"id": meeting[4], "name": meeting[5], "email": meeting[6]}
        if meeting[7] != None:
            booked_user = meeting[7] if req_user["admin"] else True
        else:
            booked_user = False
            
        meeting_data = {"id": meeting_id, 
                        "title": meeting[0], 
                        "date": meeting[1], 
                        "start_time": meeting[2], 
                        "end_time": meeting[3], 
                        "creator": creator_data,
                        "booked_user": booked_user
                        }
        
        return {"message": f"Get Meeting ID: {meeting_id}", "meeting_data": meeting_data}
    
    @app.post("/api/meeting")
    def create_meeting(meetingData: CreateMeetingBody, req: Request):
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten
        req_user = authorizeUser(req_user_id) # Om användaren inte är inloggad kastas en exception
        
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        if meetingData.title == None or len(meetingData.title) < 3:
            raise HTTPException(status_code=400, detail="Titeln du angav är för kort")
        
        # Validera att datumet inte har passerat och är korrekt
        date = date_format(meetingData.date)
        if meetingData.date == None or not date:
            raise HTTPException(status_code=400, detail="Felaktigt datum")
        
        # Kollar om tiden är i rätt format
        if meetingData.start_time == None or meetingData.end_time == None:
            raise HTTPException(status_code=400, detail="Du angav inte start- eller sluttid")
        
        start_time = convert_time(meetingData.start_time)
        end_time = convert_time(meetingData.end_time)
        if not start_time or not end_time:
            raise HTTPException(status_code=400, detail="Felaktigt format på start- eller sluttid")
        
        length = valid_length(meetingData.length)
        if meetingData.length == None or not length:
            raise HTTPException(status_code=400, detail="Felaktig längd på mötet")
        
        if meetingData.attendee_id is not None:
            if not get_user_by_id(meetingData.attendee_id):
                raise HTTPException(status_code=400, detail="Användaren du angav finns inte")
            creator_id = meetingData.attendee_id
        else:
            creator_id = req_user_id
        
        nr_meetings = slot2meeting(creator_id, date, start_time, end_time, length, meetingData.title)
        
        if nr_meetings == 0:
            return {"message": "Mötet kunde inte skapas, ingen tid tillgänglig", "nr_meetings": 0}
        else :
            return {"message": f"Nytt möte skapat, {nr_meetings} platser tillgängliga","nr_meetings": nr_meetings}
    
    @app.delete("/api/meeting/{meeting_id}")
    def delete_meeting(meeting_id: str, req: Request):
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten
        req_user = authorizeUser(req_user_id) # Om användaren inte är inloggad kastas en exception
        
        # Måste vara admin för att ta bort möte 
        # (kanske vill man lägga till att det är bara den som skapat mötet som kan göra det)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        # Ta bort mötet och cascade bort bookedMeeting om det finns
        delete_query = "DELETE FROM AvailableMeeting WHERE meetingID = %s"
        
        cursor.execute(delete_query, (meeting_id,))
        conn.commit()
        
        return {"message": f"Delete Meeting ID: {meeting_id}"}
    
    @app.post("/api/meeting/{meeting_id}/user/{user_id}")
    def add_user_to_meeting(bookingData: BookingInfoBody, meeting_id: str, user_id: str, req: Request):
        #För användaren själv eller admin att boka in en user på ett möte
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten

        #Kollar så att det är admin eller användaren själv som bokar
        req_user = authorizeUser(req_user_id)
        if str(req_user["id"]) != user_id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #Kollar så att mötet existerar
        query = "select meetingid from availablemeeting where meetingid = %s"
        cursor.execute(query, (meeting_id,))
        if cursor.fetchone()==None:
            raise HTTPException(status_code=401, detail="Det finns inget möte med detta mötes id")
        
        #Kollar så användaren som en försöker boka in finns
        if user_exists(user_id)==False:
            raise HTTPException(status_code=401, detail="Användare saknas")

        #Kollar så mötet går att boka
        query = "select available from availablemeeting where meetingid = %s"
        cursor.execute(query, (meeting_id,))
        if cursor.fetchone()[0]==False:
            raise HTTPException(status_code=409, detail="Detta möte är redan bokat")

        #Bokar in användaren
        booking = "INSERT INTO BookedMeeting VALUES (%s, %s, %s)"
        cursor.execute(booking, (meeting_id, user_id, bookingData.message))
        
        #Sätter så att mötet är bokat
        updateAM = "UPDATE AvailableMeeting SET available = False WHERE meetingID = %s"
        cursor.execute(updateAM, (meeting_id,))
        conn.commit()
        
        return {"message": f"Add user {user_id} to Meeting ID: {meeting_id} by user {req_user_id}"}
    
    @app.delete("/api/meeting/{meeting_id}/user/{user_id}")
    def remove_user_from_meeting(meeting_id: str, user_id: str, req: Request):
        #För att ta bort sig själv eller admin ta bort användare från möte
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten

        #Kollar så att det är admin eller användaren själv som tar bort bokning
        req_user = authorizeUser(req_user_id)
        if str(req_user["id"]) != user_id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #Kollar så att mötet existerar
        query = "select meetingid from availablemeeting where meetingid = %s"
        cursor.execute(query, (meeting_id,))
        if cursor.fetchone()==None:
            raise HTTPException(status_code=401, detail="Det finns inget möte med detta mötes id")
        
        #Kollar så användaren som en försöker som tar bort bokning finns
        if user_exists(user_id)==False:
            raise HTTPException(status_code=401, detail="Användare saknas")
        
        #Kollar så att användaren är inbokad på mötet
        query = "select userid from bookedmeeting where meetingid = %s"
        cursor.execute(query, (meeting_id,))
        true_user = cursor.fetchone()
        if true_user==None:
            raise HTTPException(status_code=401, detail="Ingen är bokad på detta möte")
        elif true_user[0]!=user_id:
            raise HTTPException(status_code=409, detail="Denna användare är inte inbokad på detta möte")
        
        #Tar bort användaren från mötet
        query = "delete from bookedmeeting where meetingid = %s"
        cursor.execute(query, (meeting_id,))

        #Uppdaterar available på mötet
        updateAM = "UPDATE AvailableMeeting SET available = True WHERE meetingID = %s"
        cursor.execute(updateAM, (meeting_id,))
        conn.commit()
    
        return {"message": f"Delete user {user_id} from Meeting ID: {meeting_id}"}

    @app.get("/api/groups")
    def get_groups(req: Request):
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten
        req_user = authorizeUser(req_user_id)

        query = "SELECT groupID, name FROM Groups"
        cursor.execute(query)
        groups = [{"id": data[0], "name": data[1]} for data in cursor.fetchall()]

        return {"message": "All groups", "groups": groups}
    
    @app.post("/api/group")
    def create_group(groupData: CreateGroupBody, req: Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Unauthorized, missing permission")
        
        check_query="select groupid from groups where name = %s"
        cursor.execute(check_query, (groupData.name,))
        group_id=cursor.fetchone()
        if group_id != None:
            raise HTTPException(status_code=400, detail="En grupp med detta namn finns redan")
        
        if groupData.name == None or len(groupData.name) < 3:
            raise HTTPException(status_code=400, detail="Namnet du angav är för kort")
        
        if groupData.max_visit == None or groupData.max_visit < 1:
            raise HTTPException(status_code=400, detail="Antalet tillåtna studiebesök måste vara 1 eller fler")
        
        insert_query = "INSERT INTO groups VALUES (default, %s, %s) RETURNING groupID"
        cursor.execute(insert_query, (groupData.name, groupData.max_visit))
        group_id = cursor.fetchone()[0]
        conn.commit()

        #TODO validate user och query för att skapa group
        return {"message": f"Created group {groupData.name}", "group_id":group_id}
    
    @app.delete("/api/group/{group_id}")
    def delete_group(group_id: str, req: Request):
        req_user_id = req.cookies.get("userId")
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Unauthorized, missing permission")
    
        # TODO validate user_id and get permission
        query_groupvisit = f'''DELETE FROM GroupVisit WHERE groupID = %s'''
        cursor.execute(query_groupvisit, (group_id,))
        query = f"DELETE FROM Groups WHERE groupID = '{group_id}'"
        cursor.execute(query)
        conn.commit()
        return {"message": f"Deleted group {group_id}"}
    
    @app.post("/api/group/{group_id}/visit")
    def create_visit(visitData: CreateVisitBody, group_id: str, req: Request):
        req_user_id = req.cookies.get("userId")  # Id för användaren som gör requesten
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Unauthorized, missing permission")
        
        if visitData.visit_title == None or len(visitData.visit_title) < 3:
            raise HTTPException(status_code=400, detail="Titeln du angav är för kort")
        
        # Validera att datumet inte har passerat och är korrekt
        if visitData.date == None or not date_format(visitData.date):
            raise HTTPException(status_code=400, detail="Felaktigt datum")
        
        #Osäker hur jag ska kolla att tiden inte är för kort
        if visitData.start_time == None or visitData.end_time == None or not time_format(visitData.start_time, visitData.end_time):
            raise HTTPException(status_code=400, detail="Tiderna du angav är felaktiga")
        
        if visitData.number_of_spots == None or visitData.number_of_spots < 1:
            raise HTTPException(status_code=400, detail="För få antal platser")
        
        insert_visit = 'INSERT INTO Visit VALUES (Default, %s, %s, %s, %s, %s, %s, %s) RETURNING VisitID'
        
        cursor.execute(insert_visit, (visitData.business_id, visitData.date, visitData.start_time, visitData.end_time, visitData.number_of_spots, req_user_id, visitData.visit_title))
        conn.commit()
    
        visitID = cursor.fetchone()[0]
        insert_groupVisit = 'INSERT INTO groupVisit VALUES (%s, %s)'
        cursor.execute(insert_groupVisit, (group_id, visitID))
        conn.commit()

        # För att skapa ett studiebesök i angiven grupp
        #TODO validate user och query för att skapa visit
        return {"message": f"Created visit {visitData.visit_title}"}
    
    @app.get("/api/group/{group_id}/visits")
    def get_visits(group_id: str, req: Request):
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten
        # För att hämta alla studiebesök i en grupp
        authorizeUser(req_user_id)
        query = f'''
        SELECT visit.visitID, title, visitDate, starttime, endtime, spots, business.name
        FROM visit
        INNER JOIN GroupVisit ON groupVisit.visitid = visit.visitid
        INNER JOIN Business ON Business.businessID = visit.businessID 
        WHERE GroupVisit.groupID = %s
        ORDER BY visit.visitDate '''

        cursor.execute(query, (group_id,))
        visits = [{"id": data[0], "title": data[1], "date": data[2], "start_time": data[3], "end_time": data[4],"spots": data[5], "business": data[6]} for data in cursor.fetchall()]

        # Exempel data
        #sample_business = {"id": "1234", "name": "MålarN", "address": "Målargatan 1", "info": "Teknisk målerifirma"}
        #visits = [{"id": "1234", "title": "Visit 1", "date": "2024-06-30", "start_time": "11:00", "end_time": "13:00", "spots": 3, "business": sample_business},
        #          {"id": "5421", "title": "Kul besök", "date": "2024-02-04", "start_time": "12:30", "end_time": "13:30", "spots": 12, "business": sample_business}]
        return {"visits": visits}
    
    @app.get("/api/visit/{visit_id}")
    def get_visit(visit_id: str, req: Request):
        # För att hämta information om ett studiebesök
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten
        req_user = authorizeUser(req_user_id)
        
        # Om användaren inte är admin och försöker hämta denna data
        # if req_user["admin"] == False:
        #     raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #Kollar så att mötet finns
        if visit_exists(visit_id)==False:
            raise HTTPException(status_code=404, detail="Studiebesöket finns inte")

        #Hämtar information om studiebesöket
        visit_query = "select title, visitdate, starttime, endtime, spots from visit where visitid = %s"
        cursor.execute(visit_query, (visit_id,)) 
        title, visit_date, start_time, end_time, spots = cursor.fetchone()

        #Hämtar information om företaget
        business_query = "select businessid, adress, name, info from business where businessid = (select businessid from visit where visitid = %s)"
        cursor.execute(business_query, (visit_id,)) 
        business_data = cursor.fetchone()
        business = {"id": business_data[0], "address": business_data[1], "name": business_data[2], "info": business_data[3]}

        #Hämtar information om användarna som är inbokade
        users_query = "select usertable.userid, name, email from usertable join bookedvisit on usertable.userid = bookedvisit.userid where bookedvisit.visitid = %s;"
        cursor.execute(users_query, (visit_id,)) 
        users = [{"id": user_data[0], "name": user_data[1], "email": user_data[2]} for user_data in cursor.fetchall()]

        #Skapar en dict att returnera
        visit_data = {"id": visit_id, "title": title, "date": visit_date, "start_time": start_time, "end_time": end_time, "spots": spots, "business": business, "attendees": users}

        # Exempel data
        #sample_business = {"id": "1234", "name": "MålarN", "address": "Målargatan 1", "info": "Teknisk målerifirma"}
        #user1 = {"id": "1234", "name": "Kalle", "email": "kalle@k.se"}
        #user2 = {"id": "5421", "name": "Anna", "email": "anna.kanna@vattenkanna.se"}
        #visit_data = {"id": visit_id, "title": "Kul besök", "date": "2024-02-04", "start_time": "12:30", "end_time": "13:30", "spots": 12, "business": sample_business, "attendees": [user1, user2]}
        return {"visit": visit_data}
    
    @app.delete("/api/visit/{visit_id}") 
    def delete_visit(visit_id: str, req: Request):
        # För att ta bort ett studiebesök
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten
        
        # Om användaren inte är admin och försöker ta bort ett studiebesök
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #kollar så studiebesöket finns
        if visit_exists(visit_id)==False:
            raise HTTPException(status_code=404, detail="Studiebesöket finns inte")

        #tar bort studiebesöket
        delete_query = "delete from visit where visitid = %s"
        cursor.execute(delete_query, (visit_id,))
        conn.commit()

        return {"message": f"Deleted visit {visit_id}"}
    
    @app.post("/api/visit/{visit_id}/user/{user_id}")
    def book_visit(visit_id: str, user_id: str, req: Request):
        #För att boka in en användare på ett studiebesök, både för användaren själv och admin
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten

        #kollar så att studebesöket finns
        if visit_exists(visit_id)==False:
            raise HTTPException(status_code=404, detail="Studiebesöket finns inte")
        
        #Kollar så användaren som en försöker boka in finns
        if user_exists(user_id)==False:
            raise HTTPException(status_code=401, detail="Användare saknas")

        #kollar så att det antingen är användaren själv som försöker boka eller admin
        req_user = authorizeUser(req_user_id)
        if str(req_user["id"]) != user_id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")

        #Kollar så att användaren inte har bokat för många studebesök i denna grupp
        group_query = "select groupid from groupvisit where visitid = %s"
        cursor.execute(group_query, (visit_id,))
        group_id=cursor.fetchone()
        able2book = check_no_visits(group_id, user_id)
        if not able2book:
            raise HTTPException(status_code=409, detail="Du har redan bokat in dig på max antal bokningar")
    
        #kollar så att användaren inte redan är bokad på studebesöket
        if checkIfBooked(visit_id, user_id):
            raise HTTPException(status_code=409, detail="Du är redan inbokad på detta studiebesök")
        
        #Kollar så att det finns lediga platser på studebesöket
        spots_available_query = "select spots from visit where visitid = %s"
        cursor.execute(spots_available_query, (visit_id,))
        number_of_spots=cursor.fetchone()
        if number_of_spots[0] <= 0:
            raise HTTPException(status_code=409, detail="Det finns inga lediga platser för detta studiebesök")

        #bokar in användaren och uppdaterar antalet platser
        insertBookedVisit(visit_id, user_id)
        updateNrOfSpots(visit_id)

        return {"message": f"Booked visit {visit_id} for user {user_id}"}
    
    @app.delete("/api/visit/{visit_id}/user/{user_id}")
    def cancel_visit(visit_id: str, user_id: str, req: Request):
        # För att avboka ett studiebesök, både för användaren själv och admin
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten

        #Kollar så användaren som en försöker boka in finns
        if user_exists(user_id)==False:
            raise HTTPException(status_code=401, detail="Användare saknas")
        
        #kollar så att studebesöket finns
        if visit_exists(visit_id)==False:
            raise HTTPException(status_code=404, detail="Studiebesöket finns inte")

        #kollar så att användaren är inbokad på mötet
        query = "select userid from bookedvisit where visitid = %s and userid = %s"
        cursor.execute(query, (visit_id, user_id))
        user=cursor.fetchone()
        if user==None:
            raise HTTPException(status_code=404, detail="Användaren är inte inbokat på studebesöket")

        #kollar så att det antingen är användaren själv som försöker boka eller admin
        req_user = authorizeUser(req_user_id)
        if str(req_user["id"]) != user_id and req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #Tar bort användaren från studiebesöket
        delete_query="delete from bookedvisit where visitid = %s and userid = %s"
        cursor.execute(delete_query, (visit_id, user_id))
        conn.commit()

        return {"message": f"Cancelled visit {visit_id} for user {user_id}"}
    
    @app.post("/api/business")
    def create_business(business_data: CreateBusinessBody, req: Request):
        req_user_id = req.cookies.get("userId")

        # Om användaren inte är admin och försöker skapa en business
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #kollar så att företaget inte redan finns
        if business_exists_by_name(business_data.name):
            raise HTTPException(status_code=409, detail="Ett företag med detta namn finns redan")
        
        #skapar företag
        insertBusiness = "INSERT INTO Business (name, adress, info) VALUES (%s, %s, %s)"
        cursor.execute(insertBusiness, (business_data.name, business_data.address, business_data.info))
        conn.commit()

        return {"message": f"Created Business {business_data.name}"}
    
    @app.put("/api/business/{business_id}")
    def update_business(business_data: UpdateBusinessBody, business_id: str, req: Request):
        req_user_id = req.cookies.get("userId")
        
        #Kollar så användaren är admin
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #kollar så att företaget finns
        if business_exists_by_id(business_id)==False:
            raise HTTPException(status_code=401, detail="Företaget finns inte")
        
        #uppdaterar företaget
        update_query = "UPDATE Business SET name = %s, adress = %s, info = %s WHERE businessID = %s"
        cursor.execute(update_query, (business_data.name, business_data.address, business_data.info, business_id))
        conn.commit()

        return {"message": f"Updated business {business_id} by user {req_user_id}"}
    
    @app.get("/api/business/{business_id}")
    def get_business(business_id: str, req: Request):
        #För att hämta info om ett företag
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten

        #Kollar så användaren är admin
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #kollar så att företaget finns
        if business_exists_by_id(business_id)==False:
            raise HTTPException(status_code=401, detail="Företaget finns inte")
        
        #hämtar info om företaget och lägger i dict
        info_query = "select adress, name, info from business where businessid = %s"
        cursor.execute(info_query, (business_id,))
        address, name, info=cursor.fetchone()
        business_info={"id": business_id, "name": name, "address": address, "info": info}
        
        return {"business": business_info} 
    
    @app.delete("/api/business/{business_id}")
    def delete_business(business_id: str, req: Request):
        #För att ta bort en business
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten

        # Om användaren inte är admin och försöker ta bort en business
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")
        
        #kollar så att företaget finns
        if business_exists_by_id(business_id)==False:
            raise HTTPException(status_code=401, detail="Företaget finns inte")

        #tar bort företaget
        delete_query="delete from business where businessid = %s"
        cursor.execute(delete_query, (business_id,))
        conn.commit()
        
        return {"message": f"Deleted business {business_id}"}

    @app.get("/api/businesses")
    def get_businesses(req: Request):
        #För att få ut info om alla företag
        req_user_id = req.cookies.get("userId") # Id för användaren som gör requesten

        #Kollar så användaren är admin
        req_user = authorizeUser(req_user_id)
        if req_user["admin"] == False:
            raise HTTPException(status_code=401, detail="Du saknar behörighet för att utföra denna åtgärd")

        #tar ut info om alla företag och lägger i en dict
        query = "select businessid, name, adress, info from business"
        cursor.execute(query)
        businesses = [{"id": data[0], "name": data[1], "address": data[2], "info": data[3]} for data in cursor.fetchall()]
        
        return {"businesses": businesses}