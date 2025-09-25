"""
Data models for POSH Video Generation System
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class AudioScript(BaseModel):
    """Audio script for a scene"""
    dialogue: str = Field(description="Spoken dialogue for the scene")
    sound_effects: Optional[str] = Field(default=None, description="Background sound effects with volume levels")
    tone: str = Field(default="professional", description="Tone of voice with emotional characteristics and delivery details")
    background_narration: Optional[str] = Field(default=None, description="Optional contextual voice-over or educational narration")
    audio_transitions: Optional[str] = Field(default=None, description="How audio connects to previous/next scenes")

class Scene(BaseModel):
    """Individual scene in a POSH scenario"""
    scene_number: int = Field(description="Sequential scene number")
    visual_description: str = Field(description="Detailed visual description for video generation")
    audio_script: AudioScript = Field(description="Audio components for the scene")
    duration_seconds: int = Field(default=8, description="Duration of the scene")
    setting: str = Field(description="Location/setting of the scene")
    characters: List[str] = Field(description="Characters present in the scene")
    continuity_notes: Optional[str] = Field(default=None, description="How this scene connects to previous/next scenes")

class POSHScenario(BaseModel):
    """Complete POSH scenario broken down into scenes"""
    title: str = Field(description="Title of the POSH scenario")
    description: str = Field(description="Brief description of the scenario")
    scenes: List[Scene] = Field(description="List of scenes in the scenario")
    total_duration: int = Field(description="Total estimated duration in seconds")
    learning_objectives: List[str] = Field(description="Key learning points from this scenario")

class VideoGenerationRequest(BaseModel):
    """Request for generating a video from a scene"""
    scene: Scene
    output_filename: str
    
class VideoGenerationResult(BaseModel):
    """Result of video generation"""
    scene_number: int
    video_path: str
    success: bool
    error_message: Optional[str] = None
    generation_time: Optional[float] = None
