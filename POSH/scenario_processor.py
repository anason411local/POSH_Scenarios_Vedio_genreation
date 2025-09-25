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
You are an expert in creating educational POSH (Prevention of Sexual Harassment) training scenarios. 

Your task is to break down a user-provided POSH scenario into multiple scenes, each lasting exactly 8 seconds, to create a comprehensive 60-90 second educational video.

USER SCENARIO: {user_scenario}

Requirements:
1. Create {min_scenes}-{max_scenes} scenes (8 seconds each) for a total of 60-90 seconds
2. Each scene should have:
   - Detailed visual description suitable for video generation
   - Professional dialogue with appropriate tone
   - Clear setting and character information
   - Educational value related to POSH

3. Ensure the scenario:
   - Is educational and appropriate for workplace training
   - Shows realistic workplace situations
   - Demonstrates proper/improper behavior clearly
   - Includes diverse characters and settings
   - Has a clear learning objective

4. For audio scripts:
   - Use professional, clear language
   - Include natural dialogue
   - Specify tone and delivery
   - Add relevant sound effects where appropriate

IMPORTANT: Return ONLY valid JSON in your response. No explanatory text before or after the JSON.

Return your response in exactly this JSON format:
{{
    "title": "Descriptive title for the scenario",
    "description": "Brief description of the scenario",
    "learning_objectives": ["Learning point 1", "Learning point 2", "Learning point 3"],
    "scenes": [
        {{
            "scene_number": 1,
            "visual_description": "Detailed description of what should be shown visually in this 8-second scene",
            "setting": "Specific location/setting",
            "characters": ["Character 1", "Character 2"],
            "audio_script": {{
                "dialogue": "Exact words to be spoken",
                "sound_effects": "Background sounds or effects",
                "tone": "professional"
            }},
            "duration_seconds": 8
        }}
    ],
    "total_duration": 72
}}

Focus on creating realistic, educational scenarios that help viewers understand POSH principles and appropriate workplace behavior.
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
            
            # Convert to Pydantic models
            scenes = []
            for scene_data in scenario_data["scenes"]:
                audio_script = AudioScript(**scene_data["audio_script"])
                scene = Scene(
                    scene_number=scene_data["scene_number"],
                    visual_description=scene_data["visual_description"],
                    audio_script=audio_script,
                    duration_seconds=scene_data.get("duration_seconds", 8),
                    setting=scene_data["setting"],
                    characters=scene_data["characters"]
                )
                scenes.append(scene)
            
            scenario = POSHScenario(
                title=scenario_data["title"],
                description=scenario_data["description"],
                scenes=scenes,
                total_duration=scenario_data["total_duration"],
                learning_objectives=scenario_data["learning_objectives"]
            )
            
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
        # Check duration
        if not (Config.TARGET_TOTAL_DURATION[0] <= scenario.total_duration <= Config.TARGET_TOTAL_DURATION[1]):
            raise ValueError(f"Scenario duration {scenario.total_duration}s not within target range {Config.TARGET_TOTAL_DURATION}")
        
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
