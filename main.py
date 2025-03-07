http://127.0.0.1:8000/run_crew/0from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import importlib
import uvicorn
import glob
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Check if OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY not found in environment variables. Please set it in the .env file.")

app = FastAPI(title="CrewAccess API")

# List to store available crews
crews = [
    {"id": 0, "name": "marketing_crew", "description": "Access the marketing_crew functionality"},
    {"id": 1, "name": "sales_crew", "description": "Access the sales_crew functionality"}
]

@app.get("/")
def read_root():
    return {
        "message": "Welcome to CrewAccess API",
        "available_crews": [f"{crew['id']}: {crew['name']}" for crew in crews],
        "usage": "To run a crew, use: /run_crew/{crew_id}?topic=your_topic"
    }

@app.get("/crews")
def get_crews():
    return {"crews": crews}

@app.get("/run_crew/{crew_id}")
def run_crew(crew_id: int, topic: str = Query(None)):
    # Find the requested crew
    crew_info = next((crew for crew in crews if crew["id"] == crew_id), None)
    
    # If crew not found, return error with available crews
    if not crew_info:
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": f"No crew assigned for ID {crew_id}",
                "available_crews": [f"{crew['id']}: {crew['name']}" for crew in crews]
            }
        )
    
    # If topic is not provided, return the crew information
    if topic is None:
        return JSONResponse(
            status_code=200,
            content=crew_info
        )
    
    # Process the crew based on ID
    try:
        result = None
        
        if crew_id == 0:
            # Marketing crew
            from crews.marketing.marketing import run_marketing_crew
            result = run_marketing_crew(topic)
        elif crew_id == 1:
            # Sales crew
            from crews.sales.sales import run_sales_crew
            result = run_sales_crew(topic)
        
        # Return result in consistent format
        return {
            "status": "success",
            "crew_id": crew_id,
            "topic": topic,
            "result": result
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error executing crew: {str(e)}",
                "example": f"/run_crew/{crew_id}?topic=Digital%20Marketing"
            }
        )

if __name__ == "__main__":
    print("Starting CrewAccess API...")
    print("Available crews:")
    for crew in crews:
        print(f"  {crew['id']}: {crew['name']} - {crew['description']}")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)