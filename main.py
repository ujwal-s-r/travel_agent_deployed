"""
FastAPI Backend for Tourism AI Agent
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from tourism_agent import create_tourism_agent_with_tools
from schemas import TourismResponse

# Create FastAPI app
app = FastAPI(
    title="Tourism AI Agent API",
    description="Multi-agent tourism system with weather and places information",
    version="1.0.0"
)

# Startup validation
@app.on_event("startup")
async def startup_event():
    """Validate required environment variables on startup"""
    mistral_key = os.getenv("mistral_api_key")
    if not mistral_key or mistral_key.strip() == "":
        print("⚠️  WARNING: mistral_api_key environment variable is not set!")
        print("⚠️  The API will not work properly without this key.")
        print("⚠️  Please set mistral_api_key in your Railway environment variables.")
    else:
        print("✓ mistral_api_key is configured")
        print(f"✓ API starting on port {os.environ.get('PORT', '8000')}")
    print("✓ Tourism AI Agent is starting...")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Request/Response models
class TripRequest(BaseModel):
    query: str
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"query": "Bangalore"},
                {"query": "Hey am planning to go for trip to Manali plan me 3 other places near too"}
            ]
        }


class AttractionWithCoords(BaseModel):
    name: str
    latitude: float
    longitude: float


class ChatResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None
    
    # Structured data fields
    place: Optional[str] = None
    has_weather: Optional[bool] = None
    has_places: Optional[bool] = None
    
    # Coordinates
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Weather
    temperature: Optional[float] = None
    precipitation_chance: Optional[int] = None
    
    # Attractions
    attractions: Optional[List[str]] = None
    attractions_with_coords: Optional[List[AttractionWithCoords]] = None


# Routes
@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("templates/index.html")


@app.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests"""
    from fastapi import Response
    return Response(status_code=204)


@app.get("/health")
async def health_check():
    """Health check endpoint with configuration status"""
    mistral_configured = bool(os.getenv("mistral_api_key") and os.getenv("mistral_api_key").strip())
    
    return {
        "status": "healthy" if mistral_configured else "degraded",
        "service": "Tourism AI Agent",
        "version": "1.0.0",
        "configuration": {
            "mistral_api_key": "configured" if mistral_configured else "missing",
            "port": os.environ.get("PORT", "8000")
        },
        "message": "All systems operational" if mistral_configured else "API key not configured - service will not work"
    }


@app.post("/plan-trip", response_model=ChatResponse)
async def plan_trip(request: TripRequest):
    """
    Plan trip endpoint - accepts natural language query or place name
    
    Args:
        request: TripRequest containing query (can be place name or natural language)
        
    Returns:
        ChatResponse with weather and tourist attractions
    """
    try:
        # Validate API key is configured
        if not os.getenv("mistral_api_key") or os.getenv("mistral_api_key").strip() == "":
            return ChatResponse(
                response="The API is not properly configured. Please contact the administrator.",
                success=False,
                error="Missing mistral_api_key environment variable. Please configure it in Railway."
            )
        
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Create tourism agent and get trip information
        tourism_agent = create_tourism_agent_with_tools()
        result = tourism_agent.run(request.query)
        
        return ChatResponse(
            response=result.message,
            success=result.success,
            error=result.error,
            place=result.place,
            has_weather=result.has_weather,
            has_places=result.has_places,
            latitude=result.latitude,
            longitude=result.longitude,
            temperature=result.temperature,
            precipitation_chance=result.precipitation_chance,
            attractions=result.attractions,
            attractions_with_coords=[
                AttractionWithCoords(
                    name=attr.name,
                    latitude=attr.latitude,
                    longitude=attr.longitude
                ) for attr in result.attractions_with_coords
            ] if result.attractions_with_coords else None
        )
        
    except Exception as e:
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request.",
            success=False,
            error=str(e)
        )


@app.get("/api/info")
async def get_info():
    """Get API information and usage"""
    return {
        "name": "Tourism AI Agent API",
        "version": "1.0.0",
        "description": "Multi-agent tourism system providing weather and tourist attractions",
        "endpoints": {
            "/plan-trip": {
                "method": "POST",
                "description": "Get weather and attractions for a place",
                "input": {"place": "string (e.g., 'Bangalore', 'Paris')"},
                "output": "Weather info + Tourist attractions"
            },
            "/health": {
                "method": "GET",
                "description": "Health check endpoint"
            }
        },
        "example_request": {
            "place": "Bangalore"
        },
        "example_response": {
            "response": "In Bangalore it's currently 24°C with a chance of 35% to rain. And these are the places you can go,\nLalbagh\nBangalore Palace\n...",
            "success": True,
            "place": "Bangalore",
            "temperature": 24.0,
            "precipitation_chance": 35,
            "attractions": ["Lalbagh", "Bangalore Palace", "..."]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
