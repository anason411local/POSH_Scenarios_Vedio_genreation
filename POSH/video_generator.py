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
        Create optimized prompt for Veo 3.0 video generation
        
        Args:
            scene: Scene object with visual and audio information
            
        Returns:
            str: Formatted prompt for video generation
        """
        # Base visual description
        visual_prompt = scene.visual_description
        
        # Add character and setting context
        setting_context = f"Setting: {scene.setting}."
        character_context = f"Characters: {', '.join(scene.characters)}." if scene.characters else ""
        
        # Add audio/dialogue context
        dialogue_context = f"Audio dialogue: '{scene.audio_script.dialogue}'"
        tone_context = f"Tone: {scene.audio_script.tone}"
        
        # Add POSH-specific context for appropriate workplace behavior
        posh_context = "Professional workplace environment, appropriate business attire, respectful interactions."
        
        # Combine all elements
        full_prompt = f"""
{visual_prompt}

{setting_context} {character_context}

{dialogue_context} spoken in a {tone_context} manner.

{posh_context}

High quality, realistic, professional workplace scenario for educational training purposes. 8-second duration, 720p resolution.
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
