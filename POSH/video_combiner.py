"""
Video Combiner for POSH Scenarios - Simplified Version
Since videos will be reviewed individually, this module is simplified
to just provide information about generated videos
"""
import os
from typing import List, Optional
from pathlib import Path
from config import Config
from models import POSHScenario, VideoGenerationResult

class VideoCombiner:
    def __init__(self):
        """Initialize the video combiner (simplified version)"""
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure output directories exist"""
        Path(Config.OUTPUT_DIR).mkdir(exist_ok=True)
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Get basic information about a video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            dict: Video information
        """
        try:
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                return {
                    'exists': True,
                    'file_size': file_size,
                    'file_size_mb': file_size / (1024 * 1024),
                    'path': video_path
                }
            else:
                return {'exists': False, 'path': video_path}
        except Exception as e:
            return {'error': str(e), 'path': video_path}
    
    def organize_scene_videos(
        self, 
        results: List[VideoGenerationResult], 
        scenario: POSHScenario
    ) -> dict:
        """
        Organize scene videos for individual review
        
        Args:
            results: List of video generation results
            scenario: POSH scenario information
            
        Returns:
            dict: Information about all generated videos
        """
        print(f"\n📁 Organizing scene videos for '{scenario.title}'...")
        
        # Get successful results
        successful_results = [r for r in results if r.success]
        successful_results.sort(key=lambda x: x.scene_number)
        
        video_info = {
            'scenario_title': scenario.title,
            'scenario_description': scenario.description,
            'total_scenes': len(scenario.scenes),
            'successful_scenes': len(successful_results),
            'failed_scenes': len(results) - len(successful_results),
            'learning_objectives': scenario.learning_objectives,
            'videos': []
        }
        
        # Collect info for each successful video
        for result in successful_results:
            scene = next((s for s in scenario.scenes if s.scene_number == result.scene_number), None)
            
            video_details = {
                'scene_number': result.scene_number,
                'video_path': result.video_path,
                'generation_time': result.generation_time,
                'setting': scene.setting if scene else 'Unknown',
                'characters': scene.characters if scene else [],
                'dialogue': scene.audio_script.dialogue if scene else '',
                'visual_description': scene.visual_description if scene else '',
                'file_info': self.get_video_info(result.video_path)
            }
            
            video_info['videos'].append(video_details)
        
        return video_info
    
    def print_video_summary(self, video_info: dict):
        """
        Print a summary of all generated videos
        
        Args:
            video_info: Video information dictionary
        """
        print("\n" + "="*60)
        print("🎬 GENERATED VIDEOS SUMMARY")
        print("="*60)
        print(f"Scenario: {video_info['scenario_title']}")
        print(f"Total Scenes: {video_info['total_scenes']}")
        print(f"Successfully Generated: {video_info['successful_scenes']}")
        
        if video_info['failed_scenes'] > 0:
            print(f"Failed: {video_info['failed_scenes']}")
        
        print(f"\nLearning Objectives:")
        for i, obj in enumerate(video_info['learning_objectives'], 1):
            print(f"  {i}. {obj}")
        
        print(f"\n📁 Individual Scene Videos:")
        print("-" * 40)
        
        total_size = 0
        for video in video_info['videos']:
            file_info = video['file_info']
            if file_info.get('exists'):
                size_mb = file_info.get('file_size_mb', 0)
                total_size += size_mb
                print(f"Scene {video['scene_number']:2d}: {os.path.basename(video['video_path'])}")
                print(f"          Setting: {video['setting']}")
                print(f"          Characters: {', '.join(video['characters'])}")
                print(f"          Dialogue: {video['dialogue'][:50]}...")
                print(f"          File Size: {size_mb:.1f} MB")
                print(f"          Path: {video['video_path']}")
                print()
        
        print(f"Total Size: {total_size:.1f} MB")
        print("="*60)
    
    def create_video_list_file(self, video_info: dict, output_dir: str = None) -> str:
        """
        Create a text file listing all generated videos with details
        
        Args:
            video_info: Video information dictionary
            output_dir: Output directory (defaults to Config.OUTPUT_DIR)
            
        Returns:
            str: Path to the created list file
        """
        if output_dir is None:
            output_dir = Config.OUTPUT_DIR
        
        # Create safe filename
        safe_title = "".join(c for c in video_info['scenario_title'] if c.isalnum() or c in (' ', '-', '_')).strip()
        list_filename = f"{safe_title}_video_list.txt"
        list_path = os.path.join(output_dir, list_filename)
        
        with open(list_path, 'w', encoding='utf-8') as f:
            f.write(f"POSH Training Scenario: {video_info['scenario_title']}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Description: {video_info['scenario_description']}\n\n")
            
            f.write("Learning Objectives:\n")
            for i, obj in enumerate(video_info['learning_objectives'], 1):
                f.write(f"  {i}. {obj}\n")
            f.write("\n")
            
            f.write(f"Generated Videos ({video_info['successful_scenes']}/{video_info['total_scenes']} scenes):\n")
            f.write("-" * 40 + "\n\n")
            
            for video in video_info['videos']:
                f.write(f"Scene {video['scene_number']}: {video['setting']}\n")
                f.write(f"File: {video['video_path']}\n")
                f.write(f"Characters: {', '.join(video['characters'])}\n")
                f.write(f"Dialogue: {video['dialogue']}\n")
                f.write(f"Visual: {video['visual_description']}\n")
                if video['generation_time']:
                    f.write(f"Generation Time: {video['generation_time']:.1f} seconds\n")
                f.write("\n" + "-" * 30 + "\n\n")
        
        print(f"📄 Video list saved to: {list_path}")
        return list_path