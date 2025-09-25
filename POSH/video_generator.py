"""
Video Generator using Google Veo 3.0
Generates individual 8-second videos for each scene
"""
import os
import time
import asyncio
from typing import List, Optional
from pathlib import Path
from google import genai
from config import Config
from models import Scene, VideoGenerationRequest, VideoGenerationResult

class VideoGenerator:
    def __init__(self):
        """Initialize the video generator with Gemini client"""
        Config.validate()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure output directories exist"""
        Path(Config.OUTPUT_DIR).mkdir(exist_ok=True)
        Path(Config.TEMP_DIR).mkdir(exist_ok=True)
    
    def _create_video_prompt(self, scene: Scene) -> str:
        """
        Create optimized prompt for Veo 3.0 video generation with Indian cultural context
        
        Args:
            scene: Scene object with visual and audio information
            
        Returns:
            str: Formatted prompt for video generation
        """
        # Base visual description with Indian context emphasis
        visual_prompt = scene.visual_description
        
        # Add Indian workplace setting context
        setting_context = f"Indian workplace setting: {scene.setting}."
        character_context = f"Indian characters: {', '.join(scene.characters)}." if scene.characters else ""
        
        # Enhanced audio context with emotional depth
        dialogue_context = f"Primary dialogue: '{scene.audio_script.dialogue}'"
        tone_context = f"Emotional tone and delivery: {scene.audio_script.tone}"
        
        # Background audio context with volume specifications
        sound_effects_context = ""
        if scene.audio_script.sound_effects:
            sound_effects_context = f"Layered background audio: {scene.audio_script.sound_effects}"
        
        # Background narration context
        narration_context = ""
        if scene.audio_script.background_narration:
            narration_context = f"Voice-over narration: '{scene.audio_script.background_narration}'"
        
        # Audio transitions for continuity
        audio_transitions_context = ""
        if scene.audio_script.audio_transitions:
            audio_transitions_context = f"Audio continuity: {scene.audio_script.audio_transitions}"
        
        # Visual continuity context
        continuity_context = ""
        if scene.continuity_notes:
            continuity_context = f"Scene continuity requirements: {scene.continuity_notes}"
        
        # Indian cultural context for appropriate workplace behavior
        indian_context = """
INDIAN CULTURAL CONTEXT:
- Authentic Indian office environment with typical Indian corporate settings
- Characters with realistic Indian appearances, diverse regional backgrounds
- Traditional Indian business attire mixed with modern corporate wear
- Natural Indian workplace dynamics, hierarchies, and communication styles
- Realistic Indian office interiors: modern furniture, typical lighting, Indian corporate aesthetics
- Authentic body language and gestures common in Indian professional interactions
"""
        
        # Enhanced audio requirements with specific volume mixing
        audio_requirements = """
ENHANCED AUDIO REQUIREMENTS:
- DIALOGUE QUALITY: Crystal clear conversational dialogue with natural Indian English pronunciation
  * Include realistic speech patterns: breathing, natural pauses, speech rhythms
  * Add authentic Indian English accent variations and regional pronunciations
  * Incorporate emotional voice characteristics as specified in tone requirements
  * Include natural conversation elements: hesitations, interruptions, overlapping speech

- LAYERED BACKGROUND AUDIO with precise volume mixing:
  * Primary dialogue: 100% volume (always clear and prominent)
  * Office ambience base layer: 15-25% volume (continuous, subtle atmosphere)
  * Specific action sounds: 30-45% volume (keyboard typing, paper rustling, footsteps)
  * Environmental sounds: 10-20% volume (air conditioning, distant conversations)
  * Transitional sounds: 25-35% volume (door opening, phone rings, chair movement)

- ADVANCED CONVERSATIONAL AUDIO:
  * Include non-verbal sounds: sighs, throat clearing, nervous laughter, pen clicking
  * Add realistic interruptions and natural conversation flow
  * Specify breathing patterns and emotional vocal responses
  * Include contextual sound reactions (chair creaking when someone shifts uncomfortably)

- AUDIO CONTINUITY BETWEEN SCENES:
  * Maintain consistent ambient sound levels across scenes
  * Use audio bridges for smooth transitions (continuing conversations, ongoing background sounds)
  * Include realistic audio perspective changes (closer/farther, different room acoustics)
  * Ensure background sounds flow naturally from scene to scene
"""
        
        # Enhanced visual requirements with continuity focus
        visual_requirements = """
VISUAL CONTINUITY & REALISM REQUIREMENTS:
- SCENE CONTINUITY: Maintain consistent visual elements across scenes
  * Character clothing, hairstyles, and accessories must remain identical throughout
  * Consistent lighting conditions and camera angles for visual flow
  * Logical character positioning and movement progression between scenes
  * Environmental consistency (desk arrangements, background elements, time of day)

- MAXIMUM REALISM: Organic, natural character movements and expressions
  * Authentic Indian faces with diverse regional features and natural skin tones
  * Realistic office lighting and professional cinematic camera work
  * Natural, unforced interactions between characters with authentic body language
  * Authentic Indian workplace clothing and professional styling

- VISUAL STORYTELLING: Professional video quality with seamless narrative flow
  * Smooth visual transitions that support story progression
  * Consistent visual style and composition throughout all scenes
  * Natural character reactions and emotional expressions matching the audio tone
"""
        
        # Combine all elements with enhanced continuity focus
        full_prompt = f"""
{visual_prompt}

{setting_context} {character_context}

{dialogue_context} delivered with {tone_context}.

{sound_effects_context}

{narration_context}

{audio_transitions_context}

{continuity_context}

{indian_context.strip()}

{audio_requirements.strip()}

{visual_requirements.strip()}

CRITICAL CONTINUITY REQUIREMENTS:
- This scene MUST maintain visual and audio continuity with adjacent scenes
- Character appearances, clothing, and environmental details must be consistent
- Audio levels and ambient sounds should transition smoothly from previous scenes
- Ensure natural story progression and logical scene flow

FINAL SPECIFICATIONS:
- 8-second duration, 720p resolution, professional quality
- Educational POSH training content for Indian workplace context
- Maximum authenticity, realism, and seamless continuity in all aspects
- Natural, organic character interactions with realistic workplace scenario
- Enhanced audio mixing with specified volume levels and layered soundscape
""".strip()
        
        return full_prompt
    
    async def generate_scene_video(self, scene: Scene, output_filename: str) -> VideoGenerationResult:
        """
        Generate video for a single scene using Veo 3.0
        
        Args:
            scene: Scene to generate video for
            output_filename: Name of output file
            
        Returns:
            VideoGenerationResult: Result of video generation
        """
        start_time = time.time()
        
        try:
            # Create prompt for Veo 3.0
            prompt = self._create_video_prompt(scene)
            
            print(f"Generating video for Scene {scene.scene_number}...")
            print(f"Prompt: {prompt[:100]}...")
            
            # Generate video using Veo 3.0
            operation = self.client.models.generate_videos(
                model=Config.VIDEO_MODEL,
                prompt=prompt,
            )
            
            # Poll for completion
            print(f"Waiting for Scene {scene.scene_number} video generation...")
            while not operation.done:
                print(f"Scene {scene.scene_number}: Still processing...")
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
            # Download the generated video
            generated_video = operation.response.generated_videos[0]
            output_path = os.path.join(Config.TEMP_DIR, output_filename)
            
            # Download and save video
            self.client.files.download(file=generated_video.video)
            generated_video.video.save(output_path)
            
            generation_time = time.time() - start_time
            
            print(f"Scene {scene.scene_number} generated successfully in {generation_time:.2f} seconds")
            
            return VideoGenerationResult(
                scene_number=scene.scene_number,
                video_path=output_path,
                success=True,
                generation_time=generation_time
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            error_msg = f"Error generating Scene {scene.scene_number}: {str(e)}"
            print(error_msg)
            
            return VideoGenerationResult(
                scene_number=scene.scene_number,
                video_path="",
                success=False,
                error_message=error_msg,
                generation_time=generation_time
            )
    
    async def generate_all_scenes(self, scenes: List[Scene], scenario_title: str) -> List[VideoGenerationResult]:
        """
        Generate videos for all scenes in sequence
        
        Args:
            scenes: List of scenes to generate
            scenario_title: Title for naming files
            
        Returns:
            List[VideoGenerationResult]: Results for all scenes
        """
        results = []
        
        print(f"\nStarting video generation for '{scenario_title}'")
        print(f"Total scenes to generate: {len(scenes)}")
        print("-" * 50)
        
        for i, scene in enumerate(scenes, 1):
            # Create filename for this scene
            safe_title = "".join(c for c in scenario_title if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_title}_scene_{scene.scene_number:02d}.mp4"
            
            print(f"\nProcessing Scene {scene.scene_number}/{len(scenes)}")
            print(f"Setting: {scene.setting}")
            print(f"Characters: {', '.join(scene.characters)}")
            print(f"Dialogue: {scene.audio_script.dialogue[:50]}...")
            
            # Generate video for this scene
            result = await self.generate_scene_video(scene, filename)
            results.append(result)
            
            # Show progress
            if result.success:
                print(f"✅ Scene {scene.scene_number} completed successfully")
            else:
                print(f"❌ Scene {scene.scene_number} failed: {result.error_message}")
        
        # Summary
        successful = sum(1 for r in results if r.success)
        total_time = sum(r.generation_time or 0 for r in results)
        
        print(f"\n" + "="*50)
        print(f"Video Generation Summary:")
        print(f"Successful scenes: {successful}/{len(scenes)}")
        print(f"Total generation time: {total_time:.2f} seconds")
        print(f"Average time per scene: {total_time/len(scenes):.2f} seconds")
        print("="*50)
        
        return results
    
    def get_successful_videos(self, results: List[VideoGenerationResult]) -> List[str]:
        """
        Get list of successfully generated video file paths
        
        Args:
            results: List of generation results
            
        Returns:
            List[str]: Paths to successful video files
        """
        return [result.video_path for result in results if result.success and result.video_path]
    
    def cleanup_temp_files(self, keep_successful: bool = True):
        """
        Clean up temporary files
        
        Args:
            keep_successful: Whether to keep successfully generated videos
        """
        temp_dir = Path(Config.TEMP_DIR)
        if temp_dir.exists():
            for file in temp_dir.glob("*.mp4"):
                if not keep_successful:
                    file.unlink()
                    print(f"Deleted: {file}")
        print("Temporary files cleaned up.")
