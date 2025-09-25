"""
Configuration settings for POSH Video Generation System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Video Generation Settings
    VIDEO_DURATION_SECONDS = 8
    TARGET_TOTAL_DURATION = (60, 90)  # Min and max duration in seconds
    VIDEO_RESOLUTION = "720p"
    
    # Model Configuration
    SCENARIO_MODEL = "gemini-1.5-flash"  # For breaking down scenarios
    VIDEO_MODEL = "veo-3.0-generate-001"    # For video generation
    
    # Output Configuration
    OUTPUT_DIR = "generated_videos"
    TEMP_DIR = "temp_scenes"
    
    # Scene Configuration
    MIN_SCENES = TARGET_TOTAL_DURATION[0] // VIDEO_DURATION_SECONDS  # ~7-8 scenes
    MAX_SCENES = TARGET_TOTAL_DURATION[1] // VIDEO_DURATION_SECONDS  # ~11-12 scenes
    
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        return True
