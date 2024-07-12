import psycopg2
from dotenv import load_dotenv
import os

def createTables(cursor, conn):
    extension = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'
    cursor.execute(extension)
    
    userTable = f'''CREATE TABLE UserTable(
    userID UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name varchar NOT NULL,
    email varchar unique NOT NULL CHECK(email LIKE '%@%'),
    admin boolean NOT NULL   
    )'''
    cursor.execute(userTable)

    business = f'''CREATE TABLE IF NOT EXISTS Business(
    businessID UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    adress varchar NOT NULL,
    name varchar NOT NULL,
    info varchar)'''

    cursor.execute(business)

    visit = f'''CREATE TABLE IF NOT EXISTS Visit (
    visitID UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    businessID UUID NOT NULL,
    constraint fk_businessID FOREIGN KEY (businessID) REFERENCES Business(businessID) ON DELETE CASCADE,
    visitDate date NOT NULL,
    starttime time NOT NULL,
    endtime time NOT NULL CHECK (endtime > starttime),
    spots Integer NOT NULL CHECK (spots >= 0), 
    userID uuid NOT NULL,
    constraint fk_userID FOREIGN KEY (userID) REFERENCES UserTable(userID) ON DELETE CASCADE,
    title varchar NOT NULL
    )'''
    cursor.execute(visit)


    groups = f'''CREATE TABLE IF NOT EXISTS groups(
    groupID UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name varchar unique NOT NULL,
    maxvisit Integer NOT NULL CHECK (maxvisit >= 1)
    )'''
    cursor.execute(groups)
    
    groupVisit = f'''CREATE TABLE IF NOT EXISTS groupVisit(
    groupID UUID NOT NULL,
    visitID UUID,
    PRIMARY KEY(groupID, visitID),
    constraint fk_groupID foreign key (groupID) references Groups(groupID) on delete cascade,
    constraint fk_visitID foreign key (visitID) references Visit(visitID) on delete cascade
    )'''
    cursor.execute(groupVisit)

    bookedVisit = f'''CREATE TABLE IF NOT EXISTS BookedVisit(
    visitID UUID,
    userID UUID,
    PRIMARY KEY(visitID, userID),
    constraint fk_userID foreign key (userID) references UserTable(userID) on delete cascade,
    constraint fk_visitID foreign key (visitID) references Visit(VisitID) on delete cascade
    )'''

    cursor.execute(bookedVisit)

    availableMeeting = f'''CREATE TABLE IF NOT EXISTS AvailableMeeting(
    meetingID UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    available boolean NOT NULL,
    userID uuid NOT NULL,
    constraint fk_userID foreign key (userID) references UserTable(userID),
    title varchar NOT NULL
    )'''

    cursor.execute(availableMeeting)

    bookedMeeting = f'''CREATE TABLE IF NOT EXISTS BookedMeeting (
    meetingID UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    userID uuid NOT NULL,
    CONSTRAINT fk_meetingID FOREIGN KEY (meetingID) REFERENCES AvailableMeeting(meetingID) ON DELETE CASCADE,
    CONSTRAINT fk_userID FOREIGN KEY (userID) REFERENCES UserTable(userID) ON DELETE CASCADE,
    message varchar
    )'''

    cursor.execute(bookedMeeting)

    info = f'''CREATE TABLE IF NOT EXISTS Info (
    meetingID UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    visitDate date NOT NULL,
    starttime time NOT NULL,
    endtime time NOT NULL,
    constraint fk_meetingID foreign key (meetingID) references AvailableMeeting(meetingID) on delete cascade
    )'''
    cursor.execute(info)
    conn.commit()

def drop(cursor, conn):
    tables = [
        "BookedMeeting",
        "Info",
        "AvailableMeeting",
        "BookedVisit",
        "Visit",
        "groups",
        "GroupVisit",
        "Business",
        "UserTable"
    ]
    
    for table in tables:
        query = f"DROP TABLE IF EXISTS {table} CASCADE;"
        cursor.execute(query)
    
    conn.commit()

def insertTestData(cursor, conn):
    
    userUUIDs = [
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a05',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a06'
    ]
    
    businessUUIDs = [
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a07',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a08',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a09',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a10',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    ]
    
    visitUUIDs = [
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a16',
    ]
    
    meetingUUIDs = [
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a17',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a18',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a19',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a20',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a21',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a23',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a24',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a25',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a26'
    ]
    
    groupUUIDs = [
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a27',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a28',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a29',
        'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a30'
    ]
    
    testCase = f'''
    INSERT INTO UserTable VALUES ('{userUUIDs[0]}', 'Adam Andersson', 'adam@andersson.se', false);
    INSERT INTO UserTable VALUES ('{userUUIDs[1]}', 'Bertil Berntsson', 'bertil.b@gmail.com', true);
    INSERT INTO UserTable VALUES ('{userUUIDs[2]}', 'Cecilia Carlsson', 'carlsson123@gmail.com', false);
    INSERT INTO UserTable VALUES ('{userUUIDs[3]}', 'Denise Danielsson', 'denise.dan@kth.se', false);
    INSERT INTO UserTable VALUES ('{userUUIDs[4]}', 'Elin Einarsson', 'einarsson.elin@gmail.com', false);
    INSERT INTO UserTable VALUES ('{userUUIDs[5]}', 'Adam In', 'a@vic.se', true);
    
    INSERT INTO Business VALUES ('{businessUUIDs[0]}','valhallavägen','kth', 'info om studiebesöket');
    INSERT INTO Business VALUES ('{businessUUIDs[1]}','vägen', 'microsoft', 'IT-företag');
    INSERT INTO Business VALUES ('{businessUUIDs[2]}', 'adress','google', 'Ni får se hur vi jobbar');
    INSERT INTO Business VALUES ('{businessUUIDs[3]}','adress', 'oracle', 'Vi jobbar med java');
    INSERT INTO Business VALUES ('{businessUUIDs[4]}','vägen', 'If', 'Försäkringsbolag');

    INSERT INTO Visit VALUES ('{visitUUIDs[0]}', '{businessUUIDs[0]}', '2024-02-06', '12:00:00', '14:00:00', 1, '{userUUIDs[1]}', 'besök på kth');
    INSERT INTO Visit VALUES ('{visitUUIDs[1]}', '{businessUUIDs[1]}', '2024-02-01', '11:00:00', '16:00:00', 3, '{userUUIDs[1]}', 'besök microsoft');
    INSERT INTO Visit VALUES ('{visitUUIDs[2]}', '{businessUUIDs[1]}', '2024-02-01', '11:00:00', '16:00:00', 3, '{userUUIDs[1]}', 'besök microsoft');
    INSERT INTO Visit VALUES ('{visitUUIDs[3]}', '{businessUUIDs[3]}', '2024-02-06', '12:00:00', '14:00:00', 12, '{userUUIDs[1]}', 'besök google');


    INSERT INTO BookedVisit VALUES ('{visitUUIDs[0]}', '{userUUIDs[0]}');
    INSERT INTO BookedVisit VALUES ('{visitUUIDs[1]}', '{userUUIDs[2]}');
    INSERT INTO BookedVisit VALUES ('{visitUUIDs[2]}', '{userUUIDs[3]}');
    INSERT INTO BookedVisit VALUES ('{visitUUIDs[3]}', '{userUUIDs[4]}');

    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[0]}', True, '{userUUIDs[1]}','Tillgänglig för alla');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[1]}', True, '{userUUIDs[1]}','För alla');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[2]}', False, '{userUUIDs[1]}', 'För alla');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[3]}', True, '{userUUIDs[1]}','Redovisningar');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[4]}', False, '{userUUIDs[1]}', 'DD1367');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[5]}', True, '{userUUIDs[1]}','DD1367');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[6]}', True, '{userUUIDs[1]}','Redovisning');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[7]}', False, '{userUUIDs[1]}','DD1367' );
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[8]}', True, '{userUUIDs[1]}', 'DD1367');
    INSERT INTO AvailableMeeting VALUES ('{meetingUUIDs[9]}', False, '{userUUIDs[1]}','Exjobb');

    INSERT INTO BookedMeeting VALUES('{meetingUUIDs[2]}', '{userUUIDs[0]}', 'Redovisning kurs DD1367');
    INSERT INTO BookedMeeting VALUES('{meetingUUIDs[4]}', '{userUUIDs[2]}', 'Vill gå igenom inlämning');
    INSERT INTO BookedMeeting VALUES('{meetingUUIDs[7]}', '{userUUIDs[3]}', 'Opponering');
    INSERT INTO BookedMeeting VALUES('{meetingUUIDs[9]}', '{userUUIDs[4]}', 'Redovisning');

    INSERT INTO Info VALUES('{meetingUUIDs[0]}', '2024-02-07', '12:00:00', '12:30:00');
    INSERT INTO Info VALUES('{meetingUUIDs[1]}', '2024-02-07', '12:30:00', '13:00:00');
    INSERT INTO Info VALUES('{meetingUUIDs[2]}', '2024-02-10', '10:00:00', '10:15:00');
    INSERT INTO Info VALUES('{meetingUUIDs[3]}', '2024-02-10', '10:15:00', '10:30:00');
    INSERT INTO Info VALUES('{meetingUUIDs[4]}', '2024-02-10', '10:30:00', '10:45:00');
    INSERT INTO Info VALUES('{meetingUUIDs[5]}', '2024-02-17', '12:00:00', '12:30:00');
    INSERT INTO Info VALUES('{meetingUUIDs[6]}', '2024-02-17', '12:30:00', '13:00:00');
    INSERT INTO Info VALUES('{meetingUUIDs[7]}', '2024-02-11', '10:00:00', '10:15:00');
    INSERT INTO Info VALUES('{meetingUUIDs[8]}', '2024-02-11', '10:15:00', '10:30:00');
    INSERT INTO Info VALUES('{meetingUUIDs[9]}', '2024-02-11', '10:30:00', '10:45:00');

    INSERT INTO Groups VALUES('{groupUUIDs[0]}', 'DD1310', 2);
    INSERT INTO Groups VALUES('{groupUUIDs[1]}', 'DD1311', 2);
    INSERT INTO Groups VALUES('{groupUUIDs[2]}', 'DD1312', 2);
    INSERT INTO Groups VALUES('{groupUUIDs[3]}', 'DD1313', 1);

    INSERT INTO GroupVisit VALUES ('{groupUUIDs[0]}', '{visitUUIDs[0]}');
    INSERT INTO GroupVisit VALUES ('{groupUUIDs[0]}', '{visitUUIDs[1]}');
    INSERT INTO GroupVisit VALUES ('{groupUUIDs[1]}', '{visitUUIDs[1]}');
    INSERT INTO GroupVisit VALUES ('{groupUUIDs[2]}', '{visitUUIDs[2]}');
    INSERT INTO GroupVisit VALUES ('{groupUUIDs[2]}', '{visitUUIDs[3]}');
    '''    

    cursor.execute(testCase)
    conn.commit()

def run(cursor, conn):
    print("Dropping tables")
    drop(cursor, conn)
    
    print("Creating tables")
    createTables(cursor, conn)
    
    print("Inserting test data")
    insertTestData(cursor, conn)

def connect_to_database():
    # Load environment variables from .env file
    load_dotenv(override=True)

    # Get environment variables
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')


    conn = psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
    cursor = conn.cursor()
    return cursor, conn

def main():
    cursor, conn = connect_to_database()
    
    run(cursor, conn)
    
    # Stäng cursor och anslutning när du är klar
    cursor.close()
    conn.close()
    
    print("DB setup completed")

if __name__ == "__main__":
    main()