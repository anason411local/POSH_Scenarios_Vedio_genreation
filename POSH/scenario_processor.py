"""
Scenario Processor using Gemini 2.5 Flash
Breaks down POSH scenarios into multiple 8-second scenes
"""
import json
from typing import List
from google import genai
from langchain.schema import BaseMessage
from langchain.prompts import PromptTemplate
from config import Config
from models import POSHScenario, Scene, AudioScript

class ScenarioProcessor:
    def __init__(self):
        """Initialize the scenario processor with Gemini client"""
        Config.validate()
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.scenario_prompt = self._create_scenario_prompt()
    
    def _create_scenario_prompt(self) -> PromptTemplate:
        """Create the prompt template for scenario breakdown"""
        template = """
You are an expert in creating educational POSH (Prevention of Sexual Harassment) training scenarios specifically for Indian workplace contexts.

Your task is to break down a user-provided POSH scenario into multiple scenes, each lasting exactly 8 seconds, to create a comprehensive educational video with a MAXIMUM of 8 scenes.

USER SCENARIO: {user_scenario}

CULTURAL CONTEXT REQUIREMENTS:
- ALL scenarios must reflect authentic Indian workplace environments and cultural contexts
- Use Indian names, settings, and cultural references appropriate for corporate India
- Reflect diverse Indian backgrounds (different regions, languages, but dialogue in English/Hindi as appropriate)
- Include authentic Indian office environments, dress codes, and workplace dynamics
- Show realistic Indian corporate hierarchies and communication styles
- Incorporate cultural nuances like respectful address forms (Sir/Madam), Indian festivals/occasions if relevant

CHARACTER REQUIREMENTS:
- Create organic, realistic characters with authentic Indian names and backgrounds
- Each character should have distinct personality traits, speaking styles, and backgrounds
- Include diverse representation across gender, age, seniority levels, and regional backgrounds
- Characters should behave naturally and authentically as real Indian professionals would
- Show realistic emotional responses and cultural communication patterns

Requirements:
1. Create EXACTLY {max_scenes} scenes or fewer (8 seconds each) - NEVER exceed {max_scenes} scenes
2. Each scene should have:
   - Detailed visual description suitable for video generation with Indian office settings
   - Professional dialogue with appropriate cultural tone and context
   - Clear Indian workplace setting and authentic character information
   - Educational value related to POSH in Indian context

3. Ensure the scenario:
   - Is educational and appropriate for Indian workplace training
   - Shows realistic Indian workplace situations and dynamics
   - Demonstrates proper/improper behavior clearly within Indian cultural context
   - Includes diverse Indian characters and authentic office settings
   - Has a clear learning objective relevant to Indian workplace culture

4. For audio scripts:
   - Use professional, culturally appropriate language (mix of English with occasional Hindi terms if natural)
   - Include natural dialogue that reflects how Indians actually speak in professional settings
   - Specify emotional tone, pitch, and delivery style (confident, nervous, assertive, hesitant, etc.)
   - Add contextual background sounds: office ambience, phone rings, keyboard typing, air conditioning, corridor sounds, etc.
   - Include background voice/narration where it adds educational context
   - Specify volume levels and audio layering (dialogue prominent, background subtle)

SCENE CONTINUITY REQUIREMENTS:
- CRITICAL: Ensure smooth visual and narrative continuity between consecutive scenes
- Each scene should logically flow from the previous scene (character positions, clothing consistency, time progression)
- Maintain consistent character appearances, clothing, and environmental details across all scenes
- Use transitional elements: characters moving between locations, time progression indicators, consistent lighting
- Ensure story progression feels natural and connected, not disjointed
- Reference previous scene elements when appropriate (e.g., "continuing the conversation from the previous scene")
- Maintain consistent camera angles and visual style throughout the scenario

ENHANCED AUDIO REQUIREMENTS:
- Dialogue should include rich emotional depth with specific voice characteristics:
  * Nervous: "voice trembling slightly, hesitant pauses, lower volume"
  * Confident: "clear articulation, steady pace, authoritative tone"
  * Uncomfortable: "awkward pauses, throat clearing, uncertain inflection"
  * Supportive: "warm tone, reassuring pace, empathetic delivery"
  * Angry: "raised volume, sharp consonants, faster pace"
  * Professional: "measured tone, clear pronunciation, appropriate volume"

- Background audio layers (specify volume levels as percentages):
  * Primary dialogue: 100% volume (clear and prominent)
  * Office ambience: 15-25% volume (subtle but present)
  * Specific sounds: 30-40% volume (keyboard typing, phone rings, footsteps)
  * Environmental sounds: 10-20% volume (air conditioning, distant conversations)

- Contextual audio continuity between scenes:
  * Audio should transition smoothly between scenes
  * Maintain consistent ambient sound levels
  * Use audio bridges (continuing conversations, ongoing background sounds)
  * Include realistic audio perspective changes (closer/farther from speakers)

- Advanced conversational audio specifications:
  * Include breathing patterns, natural pauses, and speech rhythms
  * Specify accent variations and regional Indian English pronunciations
  * Add realistic interruptions, overlapping speech, and natural conversation flow
  * Include non-verbal sounds: sighs, throat clearing, paper rustling, chair movement

CRITICAL REQUIREMENTS FOR JSON RESPONSE:
- ALL fields are REQUIRED and must not be null or empty
- Every scene MUST have a valid "dialogue" field with actual text
- Every scene MUST have all required audio_script fields
- Return ONLY valid JSON in your response. No explanatory text before or after the JSON.

Return your response in exactly this JSON format:
{{
    "title": "Descriptive title for the scenario",
    "description": "Brief description of the scenario",
    "learning_objectives": ["Learning point 1", "Learning point 2", "Learning point 3"],
    "scenes": [
        {{
            "scene_number": 1,
            "visual_description": "Detailed description of what should be shown visually in this 8-second scene, including Indian office environment, authentic character appearances, clothing, and realistic workplace setting",
            "setting": "Specific Indian workplace location/setting",
            "characters": ["Character 1 (with Indian name and brief background)", "Character 2 (with Indian name and brief background)"],
            "continuity_notes": "How this scene connects to previous/next scenes (character positions, clothing, time flow, environmental consistency)",
            "audio_script": {{
                "dialogue": "Exact words to be spoken with natural Indian professional communication style",
                "sound_effects": "Detailed layered background sounds with volume percentages: office ambience (20%), keyboard typing (35%), phone rings (40%), air conditioning (15%)",
                "tone": "Specific emotional voice characteristics with delivery details (e.g., 'nervous with voice trembling slightly, hesitant pauses, lower volume' or 'confident with clear articulation, steady pace, authoritative tone')",
                "background_narration": "Optional contextual voice-over or educational narration if needed",
                "audio_transitions": "How audio connects to previous/next scenes (continuing sounds, volume changes, perspective shifts)"
            }},
            "duration_seconds": 8
        }}
    ],
    "total_duration": 72
}}

Focus on creating authentic, realistic Indian workplace scenarios that help viewers understand POSH principles within Indian cultural context and appropriate workplace behavior. Ensure maximum realism and organic character interactions.
"""
        return PromptTemplate(
            template=template,
            input_variables=["user_scenario", "min_scenes", "max_scenes"]
        )
    
    async def process_scenario(self, user_scenario: str) -> POSHScenario:
        """
        Process user scenario and break it down into scenes
        
        Args:
            user_scenario: User-provided POSH scenario description
            
        Returns:
            POSHScenario: Structured scenario with scenes
        """
        try:
            # Generate the prompt
            prompt = self.scenario_prompt.format(
                user_scenario=user_scenario,
                min_scenes=Config.MIN_SCENES,
                max_scenes=Config.MAX_SCENES
            )
            
            # Call Gemini 2.5 Flash
            response = self.client.models.generate_content(
                model=Config.SCENARIO_MODEL,
                contents=prompt
            )
            
            print(f"Raw response: {response.text[:200]}...")  # Debug output
            
            # Clean and parse the JSON response
            response_text = response.text.strip()
            
            # Remove any markdown formatting if present
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            if not response_text:
                raise ValueError("Empty response from Gemini API")
            
            try:
                scenario_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON. Raw response: {response_text}")
                raise ValueError(f"Invalid JSON response: {e}")
            
            # Validate required top-level fields
            if "scenes" not in scenario_data or not scenario_data["scenes"]:
                raise ValueError("No scenes found in AI response")
            
            if "title" not in scenario_data:
                scenario_data["title"] = "POSH Training Scenario"
                print("⚠️  Missing title, using default")
            
            if "description" not in scenario_data:
                scenario_data["description"] = "Educational POSH training scenario for workplace behavior"
                print("⚠️  Missing description, using default")
            
            if "learning_objectives" not in scenario_data:
                scenario_data["learning_objectives"] = [
                    "Understand appropriate workplace behavior",
                    "Recognize inappropriate conduct",
                    "Learn proper reporting procedures"
                ]
                print("⚠️  Missing learning objectives, using defaults")
            
            # Convert to Pydantic models
            scenes = []
            scene_data_list = scenario_data["scenes"]
            
            # Enforce maximum 8 scenes limit
            if len(scene_data_list) > Config.MAX_SCENES:
                print(f"⚠️  AI generated {len(scene_data_list)} scenes, truncating to maximum {Config.MAX_SCENES} scenes")
                scene_data_list = scene_data_list[:Config.MAX_SCENES]
            
            for i, scene_data in enumerate(scene_data_list):
                # Skip invalid scene data
                if not scene_data or not isinstance(scene_data, dict):
                    print(f"⚠️  Scene {i+1} has invalid data, skipping")
                    continue
                
                # Ensure audio_script exists
                if "audio_script" not in scene_data or not scene_data["audio_script"]:
                    print(f"⚠️  Scene {i+1} missing audio_script, creating default")
                    scene_data["audio_script"] = {
                        "dialogue": "Professional workplace conversation",
                        "sound_effects": "Office ambience (20%)",
                        "tone": "professional and respectful"
                    }
                
                # Validate and fix audio_script data
                audio_data = scene_data["audio_script"]
                
                # Ensure dialogue is not None or empty
                if not audio_data.get("dialogue") or audio_data.get("dialogue") is None:
                    print(f"⚠️  Scene {i+1} has missing dialogue, using default")
                    audio_data["dialogue"] = "Professional workplace conversation"
                
                # Ensure other required fields have defaults
                audio_data["sound_effects"] = audio_data.get("sound_effects") or "Office ambience (20%), keyboard typing (15%)"
                audio_data["tone"] = audio_data.get("tone") or "professional and respectful"
                audio_data["background_narration"] = audio_data.get("background_narration")
                audio_data["audio_transitions"] = audio_data.get("audio_transitions")
                
                try:
                    audio_script = AudioScript(**audio_data)
                except Exception as e:
                    print(f"⚠️  Error creating AudioScript for scene {i+1}: {e}")
                    # Create a minimal valid audio script
                    audio_script = AudioScript(
                        dialogue="Professional workplace conversation",
                        sound_effects="Office ambience (20%)",
                        tone="professional and respectful"
                    )
                
                # Validate and fix other scene fields
                visual_description = scene_data.get("visual_description", "")
                if not visual_description or visual_description is None:
                    visual_description = "Professional Indian office environment with workplace interaction"
                    print(f"⚠️  Scene {i+1} has missing visual description, using default")
                
                setting = scene_data.get("setting", "")
                if not setting or setting is None:
                    setting = "Indian corporate office"
                    print(f"⚠️  Scene {i+1} has missing setting, using default")
                
                characters = scene_data.get("characters", [])
                if not characters or characters is None:
                    characters = ["Employee 1", "Employee 2"]
                    print(f"⚠️  Scene {i+1} has missing characters, using default")
                
                scene = Scene(
                    scene_number=i + 1,  # Renumber scenes to be sequential
                    visual_description=visual_description,
                    audio_script=audio_script,
                    duration_seconds=scene_data.get("duration_seconds", 8),
                    setting=setting,
                    characters=characters,
                    continuity_notes=scene_data.get("continuity_notes")
                )
                scenes.append(scene)
            
            # Ensure we have at least one scene
            if not scenes:
                print("⚠️  No valid scenes generated, creating a default scene")
                default_audio = AudioScript(
                    dialogue="This is an educational POSH training scenario demonstrating appropriate workplace behavior.",
                    sound_effects="Office ambience (20%)",
                    tone="professional and educational"
                )
                default_scene = Scene(
                    scene_number=1,
                    visual_description="Professional Indian corporate office environment with employees demonstrating appropriate workplace conduct and communication.",
                    audio_script=default_audio,
                    duration_seconds=8,
                    setting="Indian corporate office",
                    characters=["Employee 1", "Employee 2"],
                    continuity_notes="Opening scene establishing professional workplace environment"
                )
                scenes.append(default_scene)
            
            # Calculate actual total duration based on final scene count
            actual_total_duration = len(scenes) * Config.VIDEO_DURATION_SECONDS
            
            scenario = POSHScenario(
                title=scenario_data["title"],
                description=scenario_data["description"],
                scenes=scenes,
                total_duration=actual_total_duration,
                learning_objectives=scenario_data["learning_objectives"]
            )
            
            print(f"✅ Scenario processed: '{scenario.title}' with {len(scenes)} scenes ({actual_total_duration}s total)")
            
            return scenario
            
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Response text: {response_text}")
            raise ValueError(f"Failed to parse scenario response: {e}")
        except KeyError as e:
            print(f"Missing required field in response: {e}")
            print(f"Response data: {scenario_data}")
            raise ValueError(f"Invalid response format - missing field: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise RuntimeError(f"Error processing scenario: {e}")
    
    def validate_scenario(self, scenario: POSHScenario) -> bool:
        """
        Validate that the scenario meets requirements
        
        Args:
            scenario: The processed scenario
            
        Returns:
            bool: True if valid, raises exception if not
        """
        # Check duration (more flexible since we enforce max 8 scenes)
        expected_duration = len(scenario.scenes) * Config.VIDEO_DURATION_SECONDS
        if scenario.total_duration != expected_duration:
            print(f"⚠️  Duration mismatch: expected {expected_duration}s, got {scenario.total_duration}s. Correcting...")
            scenario.total_duration = expected_duration
        
        # Check scene count
        if not (Config.MIN_SCENES <= len(scenario.scenes) <= Config.MAX_SCENES):
            raise ValueError(f"Scene count {len(scenario.scenes)} not within target range {Config.MIN_SCENES}-{Config.MAX_SCENES}")
        
        # Check each scene
        for scene in scenario.scenes:
            if scene.duration_seconds != Config.VIDEO_DURATION_SECONDS:
                raise ValueError(f"Scene {scene.scene_number} duration {scene.duration_seconds}s != {Config.VIDEO_DURATION_SECONDS}s")
            
            if not scene.visual_description.strip():
                raise ValueError(f"Scene {scene.scene_number} missing visual description")
            
            if not scene.audio_script.dialogue.strip():
                raise ValueError(f"Scene {scene.scene_number} missing dialogue")
        
        return True
    
    def get_scenario_summary(self, scenario: POSHScenario) -> str:
        """Get a formatted summary of the scenario"""
        summary = f"""
POSH Scenario: {scenario.title}
Description: {scenario.description}
Total Duration: {scenario.total_duration} seconds
Number of Scenes: {len(scenario.scenes)}

Learning Objectives:
{chr(10).join(f"• {obj}" for obj in scenario.learning_objectives)}

Scenes:
{chr(10).join(f"Scene {scene.scene_number}: {scene.setting} - {scene.visual_description[:100]}..." for scene in scenario.scenes)}
"""
        return summary.strip()
