# Pvk-ViCan-bokningsystem

## Postgres databas

Ladda ned och installera postgreSQL från https://www.postgresql.org/download/.
För att skapa en databas kan du öppna "pgAdmin" och sedan trycka på "Add server". I servern kan du därefter skapa en databas eller använda standarddatabasen "postgres".

## Köra python

### Virtual environment (venv)

För att göra det smidigare att köra projektet med alla libraries så kan man med för del använda en virtual environment (venv). Detta är dock inget krav och nedanstående ska fungera ändå men det är inte säkert.

För att skapa en virtual environment följ följande steg:

- Kör `python -m venv myenv` i projektmappen, "myenv" kan bytas ut till godtyckligt namn. Det borde skapas en mapp som heter .myenv, detta är den virtuella miljön.
- För att starta venv kör `myenv\Scripts\activate` för windows eller `source .myenv/bin/activate` för mac. Det borde nu stå i terminalen "(myenv) C:\din\path". Du kan nu fortsätta med stegen nedan.
- För att avluta skriver duy `deactivate`

För att ladda ned alla bibliotek kör kommandot: `pip install -r requirements.txt`

Du behöver även skapa en fil som heter ".env" och som ser ut ungefär så här:

```
DB_NAME = "postgres" # Namn på databasen som du skapade
DB_USER = "postgres" # Postgres är default om du inte bytt
DB_PASSWORD = "ditt lösenord" # Lösenordet du valde vid installationen av postgreSQL
DB_HOST = "localhost" # Default

# VITE för att använda i frontend
VITE_SERVER_PORT = "8000"
VITE_FRONTEND_PORT = "9080"
VITE_SERVER_HOST = "localhost"
```

För att använda dessa variabler skriver du på följande sätt:

```python
load_dotenv(override=True) # Överst i programmet
variabel_x = os.getenv('variabel_x') # För varje variabel, du kan även andvända os.getenv('variabel_x') direkt
```

## Köra FastAPI backend

Se till att installerat alla bibliotek med `pip install -r requirements.txt`. Där efter navigera till mappen "backend" och kör kommandot: `uvicorn main:app --reload`. Flaggan "reload" gör att när ändringar görs så startar servern om. Man kan också köra `python main.py` direkt men då kan man inte använda reload.

## Köra VUE frontend

Navigera till mappen "fronted". Kör kommandot `npm install`, om npm inte är installerat, ladda ned [node.js](https://nodejs.org/en). Därefter kan du köra `npm run dev`, då borde då få upp en länk typ `localhost:5173` och då sak allt funka. Men för att sidan ska kunna kommunicera med backend behöver du starta FastAPI servern, se ovan, och ha följande miljövariabler i .env-filen:

```
VITE_SERVER_PORT = "8000" # Porten, dvs det som står efter ":", som backend(FastAPI) körs på
VITE_FRONTEND_PORT = "9080" # Porten som frontend körs på
VITE_SERVER_HOST = "localhost" # Gemensam address för backend och frontend
```

Så för att allt ska funka behöver två terminalfönster köras, en med FastAPI och en med VUE.

För att "bygga" projektet ska du köra `npm run build`, i frontend mappen då skapas en index.html fil med tillhörande filer i mappen "dist". För att sedan komma åt sidan startar du FastAPI servern med `python main.py`, se mer ovan, och ansluter till den. För att den ska fungera korrekt i production läget behöver du ange det i .env-filen på detta sätt:

```
PRODUCTION = "true"
```

När du kör i production behöver du bara ett terminal fönster, FastAPI servern.
