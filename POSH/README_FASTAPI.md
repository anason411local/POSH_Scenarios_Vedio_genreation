# POSH Video Generation System - FastAPI Version

A modern web application for generating educational POSH (Prevention of Sexual Harassment) training videos using FastAPI and simple HTML/JavaScript frontend.

## 🚀 **NEW: FastAPI Web Interface**

The system now includes a modern FastAPI web interface as an alternative to Streamlit, offering:

- **Better Performance**: Faster response times and lower resource usage
- **Simple HTML/CSS/JS**: Clean, responsive interface without framework dependencies
- **REST API**: Full API access for integration with other systems
- **Real-time Updates**: WebSocket-like polling for live progress updates
- **Mobile Friendly**: Responsive design that works on all devices

## 🏗️ **Architecture**

```
FastAPI Backend (Python)
├── REST API Endpoints
├── Background Task Processing
├── Video File Serving
└── Session Management

HTML/CSS/JS Frontend
├── Responsive UI
├── Real-time Progress Updates
├── Video Player Integration
└── Example Scenarios
```

## 🚀 **Quick Start with FastAPI**

### 1. Install Dependencies
```bash
conda activate POSH
pip install fastapi uvicorn[standard] python-multipart
```

### 2. Start the FastAPI Server

#### Option A: Using the Launcher Script (Recommended)
```bash
python run_fastapi.py
# OR double-click run_fastapi.bat (Windows)
# OR ./run_fastapi.sh (Linux/Mac)
```

#### Option B: Direct Uvicorn Command
```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 **API Endpoints**

### Main Endpoints
- `GET /` - Serve the web interface
- `POST /api/generate` - Start video generation
- `GET /api/status/{session_id}` - Get generation status
- `GET /api/video/{filename}` - Serve video files
- `GET /api/examples` - Get example scenarios

### Example API Usage

#### Start Video Generation
```bash
curl -X POST "http://localhost:8000/api/generate" \
     -H "Content-Type: application/json" \
     -d '{"scenario_text": "Your POSH scenario here..."}'
```

#### Check Status
```bash
curl "http://localhost:8000/api/status/your-session-id"
```

## 🎨 **Frontend Features**

### User Interface
- **Clean Design**: Modern, professional interface
- **Indian Context**: Culturally appropriate examples and content
- **Progress Tracking**: Real-time updates during video generation
- **Video Player**: Built-in HTML5 video player for all generated scenes

### Example Scenarios
- **Inappropriate Comments**: Manager making inappropriate remarks
- **Unwanted Advances**: Supervisor implying career consequences
- **Hostile Environment**: Sexist jokes and dismissive behavior

### Interactive Elements
- **Scenario Input**: Large text area with validation
- **Example Selector**: Pre-loaded realistic Indian workplace scenarios
- **Progress Bar**: Visual progress indicator with status messages
- **Video Gallery**: Individual scene players with metadata

## 🔧 **Configuration**

All configuration remains the same as the original system:
- Indian cultural context and authentic workplace scenarios
- Enhanced audio with layered background sounds
- Scene continuity for smooth narrative flow
- 8-second scenes targeting 60-90 second total duration

## 📁 **File Structure**

```
POSH/
├── fastapi_app.py           # FastAPI application
├── run_fastapi.py           # FastAPI launcher script
├── run_fastapi.bat          # Windows launcher
├── run_fastapi.sh           # Linux/Mac launcher
├── static/                  # Frontend assets
│   ├── css/
│   │   └── styles.css       # Application styles
│   └── js/
│       └── app.js           # Frontend JavaScript
├── scenario_processor.py    # Enhanced with Indian context
├── video_generator.py       # Enhanced with continuity
├── models.py               # Enhanced data models
└── workflow.py             # LangGraph orchestration
```

## 🌟 **Advantages over Streamlit**

### Performance
- **Faster Startup**: No heavy framework loading
- **Lower Memory**: Minimal resource usage
- **Better Scaling**: Handle multiple concurrent users

### User Experience
- **Responsive Design**: Works perfectly on mobile devices
- **Real-time Updates**: Smooth progress tracking without page refreshes
- **Better Video Playback**: Native HTML5 video controls

### Development
- **API First**: Easy integration with other systems
- **Simple Frontend**: Standard HTML/CSS/JS - no framework lock-in
- **Better Debugging**: Clear separation of frontend and backend

## 🚦 **Status Monitoring**

The FastAPI version includes comprehensive status tracking:

```json
{
  "session_id": "uuid-here",
  "status": "processing|completed|error",
  "progress": 0.75,
  "current_step": "Generating videos with Veo 3.0...",
  "processed_scenario": {...},
  "video_summary": {...},
  "start_time": "2025-09-27T14:30:00",
  "end_time": "2025-09-27T14:35:00"
}
```

## 🔄 **Migration from Streamlit**

If you were using the Streamlit version:

1. **Stop Streamlit**: Press Ctrl+C to stop the Streamlit server
2. **Install FastAPI**: `pip install fastapi uvicorn[standard] python-multipart`
3. **Start FastAPI**: `python run_fastapi.py`
4. **Access**: Go to http://localhost:8000 instead of http://localhost:8501

All your enhanced features (Indian cultural context, scene continuity, enhanced audio) are preserved!

## 🎬 **Enhanced Features Included**

- ✅ **Indian Cultural Context**: Authentic workplace scenarios, names, and settings
- ✅ **Scene Continuity**: Smooth visual and narrative flow between scenes
- ✅ **Enhanced Audio**: Layered background sounds with volume control
- ✅ **Realistic Characters**: Organic Indian professionals with natural behaviors
- ✅ **Advanced Audio Features**: Emotional voice characteristics and regional accents

---

**The FastAPI version provides a superior user experience while maintaining all the advanced POSH video generation capabilities!** 🚀

