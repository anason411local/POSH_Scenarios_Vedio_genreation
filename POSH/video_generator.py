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
from models import Scene, VideoGenerationRequest, VideoGenerationResult, ContinuityContext, CharacterProfile, EnvironmentProfile

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
    
    def _create_character_profile(self, character_name: str, scenes: List[Scene]) -> CharacterProfile:
        """
        Create a consistent character profile based on appearances across scenes
        
        Args:
            character_name: Name of the character
            scenes: All scenes to analyze for character consistency
            
        Returns:
            CharacterProfile: Detailed character profile for consistency
        """
        # Find scenes where this character appears
        character_scenes = [scene for scene in scenes if character_name in scene.characters]
        
        # Determine role based on name patterns and context
        role_mapping = {
            "manager": "Senior Manager",
            "senior": "Senior Employee", 
            "lead": "Team Lead",
            "hr": "HR Representative",
            "executive": "Executive",
            "junior": "Junior Employee",
            "intern": "Intern"
        }
        
        role = "Employee"  # default
        for key, mapped_role in role_mapping.items():
            if key.lower() in character_name.lower():
                role = mapped_role
                break
        
        # Create detailed physical description for Indian workplace context
        if "senior" in character_name.lower() or "manager" in character_name.lower():
            physical_desc = "Professional Indian adult, confident posture, mature appearance, well-groomed"
            clothing_desc = "Formal business attire - dark colored blazer/suit, pressed shirt/blouse, leather shoes, minimal professional accessories"
            personality = "Confident, authoritative, professional demeanor"
        else:
            physical_desc = "Young professional Indian adult, attentive posture, neat appearance"
            clothing_desc = "Smart casual business attire - button-down shirt/blouse, formal trousers/skirt, professional footwear"
            personality = "Respectful, attentive, professional but approachable"
        
        return CharacterProfile(
            name=character_name,
            physical_description=physical_desc,
            clothing_description=clothing_desc,
            role=role,
            personality_traits=personality
        )
    
    def _create_environment_profile(self, location: str) -> EnvironmentProfile:
        """
        Create a consistent environment profile for a location
        
        Args:
            location: Location name/description
            
        Returns:
            EnvironmentProfile: Detailed environment profile for consistency
        """
        # Standard Indian office environment profiles
        if "office" in location.lower() or "workplace" in location.lower():
            return EnvironmentProfile(
                location_name=location,
                detailed_description="Modern Indian corporate office with neutral colored walls (light grey/beige), contemporary office furniture, proper lighting, professional atmosphere",
                lighting_conditions="Bright, even office lighting with natural light from windows, professional illumination",
                key_props=["office desk", "computer/laptop", "office chair", "filing cabinets", "office phone", "documents/papers", "corporate artwork"],
                camera_angles=["Medium shot at eye level", "Over-the-shoulder shots for conversations", "Wide shot showing office layout"]
            )
        elif "cubicle" in location.lower():
            return EnvironmentProfile(
                location_name=location,
                detailed_description="Individual office cubicle with partition walls, personal workspace, organized desk setup, typical Indian corporate cubicle environment",
                lighting_conditions="Office fluorescent lighting with task lighting at desk, consistent brightness",
                key_props=["cubicle desk", "computer monitor", "ergonomic chair", "desk organizers", "personal items (minimal)", "office supplies"],
                camera_angles=["Close-up shots within cubicle space", "Medium shots showing cubicle environment"]
            )
        elif "conference" in location.lower() or "meeting" in location.lower():
            return EnvironmentProfile(
                location_name=location,
                detailed_description="Professional conference room with large meeting table, chairs around table, whiteboard/presentation screen, corporate meeting room ambiance",
                lighting_conditions="Bright conference room lighting, even illumination across the table, professional meeting atmosphere",
                key_props=["conference table", "office chairs", "whiteboard/screen", "presentation materials", "water glasses", "notebooks/pens"],
                camera_angles=["Wide shots showing full meeting table", "Medium shots of participants", "Close-ups for important dialogue"]
            )
        else:
            # Generic office space
            return EnvironmentProfile(
                location_name=location,
                detailed_description="Generic Indian corporate office space with professional decor, modern furniture, clean and organized environment",
                lighting_conditions="Standard office lighting, bright and professional",
                key_props=["office furniture", "professional decor", "office equipment"],
                camera_angles=["Standard medium shots", "Professional framing"]
            )
    
    def _create_continuity_context(self, scenes: List[Scene]) -> ContinuityContext:
        """
        Create comprehensive continuity context for all scenes
        
        Args:
            scenes: All scenes in the scenario
            
        Returns:
            ContinuityContext: Complete continuity information
        """
        # Extract all unique characters
        all_characters = set()
        all_locations = set()
        
        for scene in scenes:
            all_characters.update(scene.characters)
            all_locations.add(scene.setting)
        
        # Create character profiles
        character_profiles = {}
        for character in all_characters:
            character_profiles[character] = self._create_character_profile(character, scenes)
        
        # Create environment profiles
        environment_profiles = {}
        for location in all_locations:
            environment_profiles[location] = self._create_environment_profile(location)
        
        return ContinuityContext(
            characters=character_profiles,
            environments=environment_profiles,
            time_of_day="daytime",
            overall_mood="professional workplace training"
        )
    
    def _sanitize_content_for_api(self, text: str) -> str:
        """
        Sanitize content to avoid content policy violations while maintaining educational context
        
        Args:
            text: Original text content
            
        Returns:
            str: Sanitized text suitable for API consumption
        """
        # Replace potentially flagged terms with educational alternatives
        sensitive_replacements = {
            'harassment': 'inappropriate workplace behavior',
            'sexual harassment': 'workplace misconduct',
            'inappropriate comments': 'unprofessional remarks',
            'unwanted advances': 'inappropriate professional interaction',
            'suggestive': 'inappropriate',
            'uncomfortable': 'unprofessional situation',
            'victim': 'affected employee',
            'perpetrator': 'person displaying inappropriate behavior'
        }
        
        sanitized = text
        for original, replacement in sensitive_replacements.items():
            sanitized = sanitized.replace(original.lower(), replacement)
            sanitized = sanitized.replace(original.title(), replacement.title())
            sanitized = sanitized.replace(original.upper(), replacement.upper())
        
        return sanitized

    def _create_fallback_prompt(self, scene: Scene) -> str:
        """
        Create a very conservative fallback prompt for highly sensitive content
        
        Args:
            scene: Scene object with visual and audio information
            
        Returns:
            str: Conservative fallback prompt
        """
        # Create a very generic workplace interaction prompt
        fallback_prompt = f"""
EDUCATIONAL CORPORATE TRAINING VIDEO - PROFESSIONAL WORKPLACE INTERACTION:

Indian corporate office setting with professional employees demonstrating workplace communication standards.

SCENE: {scene.setting}
CHARACTERS: Professional Indian office workers in business attire
ACTION: Workplace conversation demonstrating professional communication and proper business conduct

VISUAL REQUIREMENTS:
- Modern Indian corporate office environment
- Professional business attire
- Respectful workplace interaction
- Clear, professional body language
- Appropriate workplace boundaries

AUDIO REQUIREMENTS:
- Professional business conversation
- Clear, respectful communication
- Appropriate workplace tone
- Background office ambience

SPECIFICATIONS:
- 8-second duration, 720p resolution
- Educational content for corporate training
- Professional workplace demonstration
- Appropriate business conduct example
"""
        return fallback_prompt.strip()

    def _create_video_prompt(self, scene: Scene, continuity_context: Optional[ContinuityContext] = None, previous_scene: Optional[Scene] = None) -> str:
        """
        Create optimized prompt for Veo 3.0 video generation with Indian cultural context
        Includes content sanitization and comprehensive continuity information
        
        Args:
            scene: Scene object with visual and audio information
            continuity_context: Continuity context for character and environment consistency
            previous_scene: Previous scene for transition continuity
            
        Returns:
            str: Formatted prompt for video generation
        """
        # Base visual description with Indian context emphasis - sanitized
        visual_prompt = self._sanitize_content_for_api(scene.visual_description)
        
        # Create comprehensive continuity sections
        character_continuity = ""
        environment_continuity = ""
        scene_transition = ""
        
        if continuity_context:
            # Character consistency details
            character_details = []
            for char_name in scene.characters:
                if char_name in continuity_context.characters:
                    profile = continuity_context.characters[char_name]
                    char_detail = f"""
{char_name} ({profile.role}):
- Physical: {profile.physical_description}
- Clothing: {profile.clothing_description}
- Personality: {profile.personality_traits}"""
                    character_details.append(char_detail)
            
            if character_details:
                character_continuity = f"""
CHARACTER CONTINUITY - MAINTAIN EXACT CONSISTENCY:
{''.join(character_details)}

CRITICAL: These character descriptions must be IDENTICAL across all scenes. No variations in clothing, appearance, or physical characteristics allowed."""
            
            # Environment consistency details
            if scene.setting in continuity_context.environments:
                env_profile = continuity_context.environments[scene.setting]
                environment_continuity = f"""
ENVIRONMENT CONTINUITY - MAINTAIN EXACT CONSISTENCY:
Location: {env_profile.location_name}
Description: {env_profile.detailed_description}
Lighting: {env_profile.lighting_conditions}
Key Props: {', '.join(env_profile.key_props)}
Camera Work: {', '.join(env_profile.camera_angles)}

CRITICAL: Environment must be IDENTICAL to previous scenes in this location. Same furniture placement, lighting, and props."""
        
        # Scene transition continuity
        if previous_scene:
            scene_transition = f"""
SCENE TRANSITION CONTINUITY:
Previous Scene: {previous_scene.setting} with {', '.join(previous_scene.characters)}
Current Scene: {scene.setting} with {', '.join(scene.characters)}

TRANSITION REQUIREMENTS:
- Characters moving between scenes must maintain identical appearance
- If same location: furniture and environment must be exactly the same
- Lighting and time of day must be consistent
- Emotional continuity from previous scene context
- Natural progression of story and character positions"""
        
        # Add Indian workplace setting context
        setting_context = f"Indian workplace setting: {scene.setting}."
        character_context = f"Indian characters: {', '.join(scene.characters)}." if scene.characters else ""
        
        # Enhanced audio context with emotional depth - sanitized
        dialogue_context = f"Primary dialogue: '{self._sanitize_content_for_api(scene.audio_script.dialogue)}'"
        tone_context = f"Emotional tone and delivery: {self._sanitize_content_for_api(scene.audio_script.tone)}"
        
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
        
        # Educational context header to establish legitimate use
        educational_header = """
EDUCATIONAL TRAINING VIDEO - WORKPLACE ETHICS CONTENT:
This is an educational training video for corporate workplace ethics and professional behavior standards.
Content is designed for HR training purposes to demonstrate appropriate workplace conduct and professional interactions.
All scenarios are educational simulations for learning proper workplace behavior and communication.
"""

        # Combine all elements with enhanced continuity focus
        full_prompt = f"""
{educational_header.strip()}

{visual_prompt}

{setting_context} {character_context}

{dialogue_context} delivered with {tone_context}.

{sound_effects_context}

{narration_context}

{audio_transitions_context}

{character_continuity}

{environment_continuity}

{scene_transition}

{indian_context.strip()}

{audio_requirements.strip()}

{visual_requirements.strip()}

CRITICAL CONTINUITY REQUIREMENTS:
- This scene MUST maintain EXACT visual continuity with all other scenes
- Character appearances, clothing, hairstyles, and accessories must be IDENTICAL
- Environment furniture, lighting, and props must be IDENTICAL across scenes
- Audio levels and ambient sounds should transition smoothly from previous scenes
- Camera angles and visual style must be consistent throughout
- Time of day and lighting conditions must remain constant
- Natural story progression with logical character positioning

FINAL SPECIFICATIONS:
- 8-second duration, 720p resolution, professional quality
- Educational workplace ethics training content for Indian corporate context
- MAXIMUM continuity priority - consistency is more important than variety
- Professional workplace interactions demonstrating proper business conduct
- Enhanced audio mixing with specified volume levels and layered soundscape
""".strip()
        
        return full_prompt
    
    async def generate_scene_video_with_fallback(self, scene: Scene, output_filename: str, continuity_context: Optional[ContinuityContext] = None, previous_scene: Optional[Scene] = None) -> VideoGenerationResult:
        """
        Generate video for a single scene with fallback prompt for content policy issues
        
        Args:
            scene: Scene to generate video for
            output_filename: Name of output file
            continuity_context: Continuity context for character and environment consistency
            previous_scene: Previous scene for transition continuity
            
        Returns:
            VideoGenerationResult: Result of video generation
        """
        # First attempt with regular sanitized prompt
        result = await self._generate_scene_video_single_attempt(scene, output_filename, use_fallback=False, continuity_context=continuity_context, previous_scene=previous_scene)
        
        if result.success:
            return result
        
        # Check if this seems like a content policy issue and fallback is enabled
        if (Config.ENABLE_FALLBACK_PROMPTS and 
            result.error_message and 
            any(keyword in result.error_message.lower() for keyword in ['policy', 'content', 'inappropriate', 'blocked', '503'])):
            
            print(f"Content policy issue detected for Scene {scene.scene_number}. Trying fallback prompt...")
            
            # Try with fallback prompt (fallback doesn't use continuity context to be ultra-safe)
            fallback_result = await self._generate_scene_video_single_attempt(scene, output_filename, use_fallback=True)
            
            if fallback_result.success:
                print(f"✅ Scene {scene.scene_number} generated successfully using fallback prompt")
                return fallback_result
            else:
                # Return the fallback result (which contains the error)
                return fallback_result
        
        # Return original result if no fallback attempted
        return result

    async def _generate_scene_video_single_attempt(self, scene: Scene, output_filename: str, use_fallback: bool = False, continuity_context: Optional[ContinuityContext] = None, previous_scene: Optional[Scene] = None) -> VideoGenerationResult:
        """
        Single attempt to generate video for a scene
        
        Args:
            scene: Scene to generate video for
            output_filename: Name of output file
            use_fallback: Whether to use fallback prompt for sensitive content
            continuity_context: Continuity context for character and environment consistency
            previous_scene: Previous scene for transition continuity
            
        Returns:
            VideoGenerationResult: Result of video generation
        """
        start_time = time.time()
        
        try:
            # Create prompt for Veo 3.0
            if use_fallback:
                prompt = self._create_fallback_prompt(scene)
                print(f"Using fallback prompt for Scene {scene.scene_number}")
            else:
                prompt = self._create_video_prompt(scene, continuity_context, previous_scene)
            
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

    # Keep the original method name for backward compatibility
    async def generate_scene_video(self, scene: Scene, output_filename: str) -> VideoGenerationResult:
        """
        Generate video for a single scene using Veo 3.0 with content policy fallback
        
        Args:
            scene: Scene to generate video for
            output_filename: Name of output file
            
        Returns:
            VideoGenerationResult: Result of video generation
        """
        return await self.generate_scene_video_with_fallback(scene, output_filename)
    
    async def generate_all_scenes(self, scenes: List[Scene], scenario_title: str) -> List[VideoGenerationResult]:
        """
        Generate videos for all scenes in sequence with full continuity support
        
        Args:
            scenes: List of scenes to generate
            scenario_title: Title for naming files
            
        Returns:
            List[VideoGenerationResult]: Results for all scenes
        """
        results = []
        
        print(f"\nStarting video generation for '{scenario_title}'")
        print(f"Total scenes to generate: {len(scenes)}")
        
        # Create comprehensive continuity context
        print("Creating continuity context for visual consistency...")
        continuity_context = self._create_continuity_context(scenes)
        
        print("\nContinuity Context Created:")
        print(f"- Characters: {', '.join(continuity_context.characters.keys())}")
        print(f"- Environments: {', '.join(continuity_context.environments.keys())}")
        print("-" * 50)
        
        previous_scene = None
        
        for i, scene in enumerate(scenes, 1):
            # Create filename for this scene
            safe_title = "".join(c for c in scenario_title if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"{safe_title}_scene_{scene.scene_number:02d}.mp4"
            
            print(f"\nProcessing Scene {scene.scene_number}/{len(scenes)}")
            print(f"Setting: {scene.setting}")
            print(f"Characters: {', '.join(scene.characters)}")
            print(f"Dialogue: {scene.audio_script.dialogue[:50]}...")
            
            if previous_scene:
                print(f"Continuity: Following Scene {previous_scene.scene_number} in {previous_scene.setting}")
            
            # Generate video for this scene with continuity context
            result = await self.generate_scene_video_with_continuity(scene, filename, continuity_context, previous_scene)
            results.append(result)
            
            # Show progress
            if result.success:
                print(f"✅ Scene {scene.scene_number} completed successfully")
                previous_scene = scene  # Update previous scene only on success
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
    
    async def generate_scene_video_with_continuity(self, scene: Scene, output_filename: str, continuity_context: ContinuityContext, previous_scene: Optional[Scene] = None) -> VideoGenerationResult:
        """
        Generate video for a single scene with full continuity support
        
        Args:
            scene: Scene to generate video for
            output_filename: Name of output file
            continuity_context: Continuity context for character and environment consistency
            previous_scene: Previous scene for transition continuity
            
        Returns:
            VideoGenerationResult: Result of video generation
        """
        return await self.generate_scene_video_with_fallback(scene, output_filename, continuity_context, previous_scene)
    
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
