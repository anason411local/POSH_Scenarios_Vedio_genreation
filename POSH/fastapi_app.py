"""
FastAPI Application for POSH Video Generation System
Simple web interface with HTML frontend
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import os
import json
import time
from datetime import datetime
from pathlib import Path
import uuid

# Import our modules
from workflow import POSHVideoWorkflow
from models import POSHScenario
from config import Config

# Initialize FastAPI app
app = FastAPI(
    title="POSH Video Generation System",
    description="Prevention of Sexual Harassment Training Video Generator",
    version="1.0.0"
)

# Global storage for generation sessions
generation_sessions: Dict[str, Dict[str, Any]] = {}

# Request/Response Models
class ScenarioRequest(BaseModel):
    scenario_text: str
    session_id: Optional[str] = None

class GenerationStatus(BaseModel):
    session_id: str
    status: str  # "processing", "completed", "error"
    progress: float
    current_step: str
    processed_scenario: Optional[Dict] = None
    video_summary: Optional[Dict] = None
    error_message: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

# Ensure directories exist
def ensure_directories():
    """Ensure all required directories exist"""
    directories = [Config.OUTPUT_DIR, Config.TEMP_DIR, "static", "static/css", "static/js"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

ensure_directories()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>POSH Video Generation System</title>
        <link rel="stylesheet" href="/static/css/styles.css">
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎬 POSH Video Generation System</h1>
                <p>Prevention of Sexual Harassment Training Video Generator</p>
                <p class="subtitle">Powered by Gemini 2.5 Flash + Veo 3.0 + Indian Cultural Context</p>
            </header>

            <div class="main-content">
                <!-- Step 1: Scenario Input -->
                <section id="input-section" class="section">
                    <h2>📝 Step 1: Enter Your POSH Scenario</h2>
                    
                    <div class="example-selector">
                        <label for="example-select">Choose an example scenario:</label>
                        <select id="example-select">
                            <option value="">Select an example...</option>
                            <option value="inappropriate-comments">Inappropriate Comments</option>
                            <option value="unwanted-advances">Unwanted Advances</option>
                            <option value="hostile-environment">Hostile Work Environment</option>
                        </select>
                    </div>

                    <textarea 
                        id="scenario-input" 
                        placeholder="Describe a realistic Indian workplace scenario involving sexual harassment, including the inappropriate behavior, affected parties, and the proper resolution process..."
                        rows="8"
                    ></textarea>

                    <button id="generate-btn" class="primary-btn">
                        🚀 Generate POSH Training Videos
                    </button>
                </section>

                <!-- Step 2: Processing Status -->
                <section id="processing-section" class="section" style="display: none;">
                    <h2>⏳ Step 2: Processing Your Scenario</h2>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div id="progress-fill" class="progress-fill"></div>
                        </div>
                        <div id="progress-text" class="progress-text">0% - Starting...</div>
                    </div>
                    <div id="current-step" class="current-step"></div>
                </section>

                <!-- Step 3: Scene Breakdown -->
                <section id="scenario-section" class="section" style="display: none;">
                    <h2>📋 Step 3: AI-Generated Scene Breakdown</h2>
                    <div id="scenario-details"></div>
                </section>

                <!-- Step 4: Generated Videos -->
                <section id="videos-section" class="section" style="display: none;">
                    <h2>🎬 Step 4: Generated Videos</h2>
                    <div id="video-summary"></div>
                    <div id="video-list"></div>
                </section>

                <!-- Error Section -->
                <section id="error-section" class="section error-section" style="display: none;">
                    <h2>❌ Error</h2>
                    <div id="error-message"></div>
                    <button id="retry-btn" class="secondary-btn">Try Again</button>
                </section>
            </div>

            <!-- Sidebar -->
            <aside class="sidebar">
                <h3>💡 Tips for Better Scenarios</h3>
                <ul>
                    <li>Be specific about Indian workplace setting</li>
                    <li>Include authentic character names and backgrounds</li>
                    <li>Describe inappropriate behavior clearly</li>
                    <li>Mention proper resolution process</li>
                    <li>Keep it realistic and educational</li>
                </ul>

                <h3>⚙️ Configuration</h3>
                <div class="config-info">
                    <p><strong>Video Duration:</strong> 8 seconds per scene</p>
                    <p><strong>Target Total:</strong> 60-90 seconds</p>
                    <p><strong>Resolution:</strong> 720p</p>
                    <p><strong>Cultural Context:</strong> Indian Workplace</p>
                </div>
            </aside>
        </div>

        <script src="/static/js/app.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/api/generate", response_model=GenerationStatus)
async def start_generation(request: ScenarioRequest, background_tasks: BackgroundTasks):
    """Start video generation process"""
    if not request.scenario_text.strip():
        raise HTTPException(status_code=400, detail="Scenario text is required")
    
    if len(request.scenario_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Scenario too short. Please provide more details (at least 50 characters)")
    
    # Generate session ID
    session_id = request.session_id or str(uuid.uuid4())
    
    # Initialize session
    generation_sessions[session_id] = {
        "status": "processing",
        "progress": 0.0,
        "current_step": "Starting video generation...",
        "processed_scenario": None,
        "video_summary": None,
        "error_message": None,
        "start_time": datetime.now().isoformat(),
        "end_time": None
    }
    
    # Start background task
    background_tasks.add_task(generate_videos_background, session_id, request.scenario_text)
    
    return GenerationStatus(
        session_id=session_id,
        status="processing",
        progress=0.0,
        current_step="Starting video generation...",
        start_time=generation_sessions[session_id]["start_time"]
    )

@app.get("/api/status/{session_id}", response_model=GenerationStatus)
async def get_generation_status(session_id: str):
    """Get the status of a generation session"""
    if session_id not in generation_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = generation_sessions[session_id]
    return GenerationStatus(
        session_id=session_id,
        status=session["status"],
        progress=session["progress"],
        current_step=session["current_step"],
        processed_scenario=session["processed_scenario"],
        video_summary=session["video_summary"],
        error_message=session["error_message"],
        start_time=session["start_time"],
        end_time=session["end_time"]
    )

@app.get("/api/video/{filename}")
async def get_video(filename: str):
    """Serve video files"""
    video_path = Path(Config.TEMP_DIR) / filename
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=filename
    )

@app.get("/api/examples")
async def get_examples():
    """Get example scenarios"""
    examples = {
        "inappropriate-comments": """A senior manager, Rajesh Kumar, frequently makes inappropriate comments about female employees' appearance during team meetings in the Mumbai office. Priya Sharma, a junior marketing executive from Chennai, feels uncomfortable when Rajesh comments on her traditional Indian outfits and makes suggestive remarks about her appearance. Other team members, including Amit from Delhi and Sneha from Bangalore, notice the behavior but are unsure how to respond appropriately. The scenario demonstrates how Priya documents the incidents using proper POSH protocols, seeks support from HR representative Mrs. Meera Gupta, and how colleagues can appropriately intervene while respecting Indian workplace hierarchies. It shows the proper escalation process, the importance of creating a safe workplace environment, and the consequences of harassment. The scenario concludes with Rajesh receiving appropriate disciplinary action and the team participating in additional POSH training to prevent future incidents.""",
        
        "unwanted-advances": """During a company retreat in Goa, department head Vikram Mehta repeatedly asks junior software developer Kavya Reddy out for drinks despite being politely declined multiple times. Vikram, who is from a traditional Gujarati family, implies that career advancement might be affected by her refusal, saying things like 'You know, Kavya, team players who join company events tend to get better appraisals.' The situation escalates when he starts sending inappropriate WhatsApp messages after office hours. Kavya, who comes from a conservative South Indian family, feels conflicted about reporting her senior. The scenario shows how she seeks help from trusted colleague Arjun Singh, documents the incidents with screenshots and written notes, and reports to HR manager Sunita Joshi. It demonstrates the proper investigation process, support systems available to employees including counseling, and the consequences of such behavior in Indian corporate culture.""",
        
        "hostile-environment": """Team lead Rohit Agarwal consistently makes sexist jokes and comments during meetings in the Pune office, often referencing Indian cultural stereotypes about women's roles. He frequently interrupts female team members like Neha Patel and Riya Das, dismissing their technical contributions with comments like 'Maybe the ladies should focus on documentation while men handle the coding.' When confronted by senior developer Ananya Iyer, Rohit dismisses concerns claiming it's just humor and that 'Indian women are too sensitive these days.' The scenario shows how affected employees including Neha, Riya, and Ananya band together, document incidents with specific dates and witnesses, and escalate through proper channels to HR head Deepak Sharma. It demonstrates the investigation process led by external consultant Ms. Rashida Khan, interim measures to protect employees including team restructuring, and comprehensive remedial action including sensitivity training and policy updates."""
    }
    
    return examples

async def generate_videos_background(session_id: str, scenario_text: str):
    """Background task to generate videos"""
    try:
        session = generation_sessions[session_id]
        
        # Update progress
        session["current_step"] = "Initializing workflow..."
        session["progress"] = 0.1
        
        # Initialize workflow
        workflow = POSHVideoWorkflow()
        
        # Update progress
        session["current_step"] = "Processing scenario with Gemini 2.5 Flash..."
        session["progress"] = 0.2
        
        # Run workflow
        result = await workflow.run_workflow(scenario_text)
        
        # Update session with results
        if result.get("error_message"):
            session["status"] = "error"
            session["error_message"] = result["error_message"]
            session["current_step"] = "Error occurred"
            session["progress"] = 0.0
        else:
            session["status"] = "completed"
            session["processed_scenario"] = result.get("processed_scenario").__dict__ if result.get("processed_scenario") else None
            session["video_summary"] = result.get("video_summary", {})
            session["current_step"] = "Completed successfully!"
            session["progress"] = 1.0
        
        session["end_time"] = datetime.now().isoformat()
        
    except Exception as e:
        session = generation_sessions[session_id]
        session["status"] = "error"
        session["error_message"] = f"Unexpected error: {str(e)}"
        session["current_step"] = "Error occurred"
        session["progress"] = 0.0
        session["end_time"] = datetime.now().isoformat()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        Config.validate()
        return {"status": "healthy", "message": "POSH Video Generation System is running"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

