import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

from starlette.responses import FileResponse

from routes import setup_routes
from database import connect_to_database

app = FastAPI()

load_dotenv(override=True)
PRODUCTION = os.getenv('PRODUCTION', default="false")

if not PRODUCTION == "true":
    print("Running in development mode") 
    HOST = os.getenv('VITE_SERVER_HOST', default="localhost")
    FRONTEND_PORT = os.getenv('VITE_FRONTEND_PORT', default="5173")

    origins = [f"http://{HOST}:{FRONTEND_PORT}"]  # Allow all origins for development (replace with specific origins for production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow used methods
        allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin", "Cookie", "userId"],  # Allow all headers for development (replace with specific headers for production)
    )
else:
    print("Running in production mode")

app.mount("/static", StaticFiles(directory="public"), name="static")

# Connect to database
cursor, conn = connect_to_database()

# Setup routes
setup_routes(app, cursor, conn)

# Catch all
@app.get("/api/{path:path}")
def catch_api(path):
    return {"error": f"Route /api/{path} does not exist"}

# Mount VUE app
try:
    @app.get("/{full_path:path}", include_in_schema=False)
    async def index(request: Request, full_path: str):
        if not full_path.startswith("assets"):
            return FileResponse("../frontend/dist/index.html")
        else:
            return FileResponse(f"../frontend/dist/{full_path}")
    
except:
    print("!!! Could not mount VUE app. Make sure you have run 'npm run build' in the frontend directory. !!!")



if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv(override=True)

    # Get environment variables
    SERVER_PORT = os.getenv('VITE_SERVER_PORT', default="8000")
    SERVER_HOST = os.getenv('VITE_SERVER_HOST', default="localhost")
    uvicorn.run(app, host=SERVER_HOST, port=int(SERVER_PORT))