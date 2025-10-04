"""
Streamlit Web Interface for POSH Video Generation System
Beautiful, interactive interface for generating POSH training videos
"""
import streamlit as st
import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
import time

# Import our modules
from workflow import POSHVideoWorkflow
from models import POSHScenario, Scene, AudioScript, VideoGenerationResult
from config import Config

# Configure Streamlit page
st.set_page_config(
    page_title="POSH Video Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    .scene-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    .video-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = None
    if 'processed_scenario' not in st.session_state:
        st.session_state.processed_scenario = None
    if 'generation_results' not in st.session_state:
        st.session_state.generation_results = []
    if 'video_summary' not in st.session_state:
        st.session_state.video_summary = {}
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False
    if 'generation_mode' not in st.session_state:
        st.session_state.generation_mode = "automatic"  # "automatic" or "custom"
    if 'custom_scene_result' not in st.session_state:
        st.session_state.custom_scene_result = None

def display_header():
    """Display the main header"""
    st.markdown('<h1 class="main-header">🎬 POSH Video Generation System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Prevention of Sexual Harassment Training Video Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Powered by Gemini 2.5 Flash + Veo 3.0 + LangGraph</p>', unsafe_allow_html=True)
    st.markdown("---")

def display_sidebar():
    """Display the sidebar with information and controls"""
    with st.sidebar:
        st.header("📋 How It Works")
        
        if st.session_state.generation_mode == "automatic":
            st.markdown("""
            **🤖 Automatic Mode:**
            
            **Step 1:** Enter your POSH scenario
            
            **Step 2:** AI breaks it into 8-second scenes
            
            **Step 3:** Veo 3.0 generates individual videos
            
            **Step 4:** Review each scene video
            """)
        else:
            st.markdown("""
            **🎯 Custom Scene Mode:**
            
            **Step 1:** Set video duration (5-15 seconds)
            
            **Step 2:** Describe the visual scene in detail
            
            **Step 3:** Add system instructions (optional)
            
            **Step 4:** Generate targeted video with Veo 3.0
            """)
        
        st.header("💡 Tips")
        
        if st.session_state.generation_mode == "automatic":
            st.markdown("""
            **For Better Scenarios:**
            • Be specific about workplace setting
            • Include character descriptions
            • Describe inappropriate behavior clearly
            • Mention proper resolution process
            • Keep it realistic and educational
            """)
        else:
            st.markdown("""
            **For Better Custom Scenes:**
            • Be very specific about character actions and expressions
            • Include detailed visual descriptions of the workplace setting
            • Describe the inappropriate behavior clearly and realistically
            • Specify camera angles and visual focus in system instructions
            • Add cultural context and authentic Indian workplace details
            • Use system instructions for technical requirements (lighting, sound, etc.)
            """)
        
        st.header("⚙️ Configuration")
        st.info(f"**Video Duration:** {Config.VIDEO_DURATION_SECONDS} seconds per scene")
        
        if st.session_state.generation_mode == "automatic":
            st.info(f"**Maximum Scenes:** {Config.MAX_SCENES} scenes (64 seconds max)")
        else:
            st.info(f"**Custom Duration:** 5-15 seconds (user configurable)")
            
        st.info(f"**Resolution:** {Config.VIDEO_RESOLUTION}")
        
        # Mode indicator
        mode_emoji = "🤖" if st.session_state.generation_mode == "automatic" else "🎯"
        mode_name = "Automatic" if st.session_state.generation_mode == "automatic" else "Custom"
        st.success(f"{mode_emoji} **Current Mode:** {mode_name}")
        
        # Quick mode switch
        if st.button(f"Switch to {'Custom' if st.session_state.generation_mode == 'automatic' else 'Automatic'} Mode", key="sidebar_switch"):
            st.session_state.generation_mode = "custom" if st.session_state.generation_mode == "automatic" else "automatic"
            st.rerun()

def get_scenario_input():
    """Get scenario input from user"""
    st.header("📝 Step 1: Choose Generation Mode")
    
    # Mode selection
    mode = st.radio(
        "Select how you want to generate videos:",
        ["🤖 Automatic Full Scenario", "🎯 Custom Single Scene"],
        horizontal=True
    )
    
    st.session_state.generation_mode = "automatic" if "Automatic" in mode else "custom"
    
    if st.session_state.generation_mode == "automatic":
        return get_automatic_scenario_input()
    else:
        return get_custom_scene_input()

def get_automatic_scenario_input():
    """Get automatic scenario input from user"""
    st.subheader("🤖 Automatic Full Scenario Generation")
    st.info("The AI will break down your scenario into 8 scenes and generate all videos automatically.")
    
    # Example scenarios
    example_scenarios = {
        "Select an example...": "",
        "Inappropriate Comments": """A senior manager, John, frequently makes inappropriate comments about female employees' appearance during team meetings. Sarah, a junior marketing executive, feels uncomfortable when John comments on her clothing and makes suggestive remarks. Other team members notice the behavior but are unsure how to respond. The scenario demonstrates how Sarah documents the incidents, seeks support from HR, and how colleagues can appropriately intervene. It shows the proper escalation process, the importance of creating a safe workplace environment, and the consequences of harassment. The scenario concludes with John receiving appropriate disciplinary action and the team participating in additional POSH training to prevent future incidents.""",
        "Unwanted Advances": """During a company retreat, a department head repeatedly asks a junior employee out for drinks despite being politely declined multiple times. The situation escalates when the senior employee implies that career advancement might be affected by the refusal. The scenario shows how the junior employee seeks help from trusted colleagues, documents the incidents, and reports to HR. It demonstrates the proper investigation process, support systems available to employees, and the consequences of such behavior.""",
        "Hostile Work Environment": """A team lead consistently makes sexist jokes and comments during meetings, creating an uncomfortable atmosphere for female team members. When confronted, the lead dismisses concerns and claims it's just humor. The scenario shows how affected employees band together, document incidents, and escalate through proper channels. It demonstrates the investigation process, interim measures to protect employees, and comprehensive remedial action."""
    }
    
    # Example selector
    selected_example = st.selectbox(
        "Choose an example scenario or write your own:",
        list(example_scenarios.keys())
    )
    
    # Text area for scenario input
    default_text = example_scenarios.get(selected_example, "")
    scenario_text = st.text_area(
        "Enter your POSH scenario description:",
        value=default_text,
        height=200,
        placeholder="Describe a realistic workplace scenario involving sexual harassment, including the inappropriate behavior, affected parties, and the proper resolution process..."
    )
    
    return scenario_text

def get_custom_scene_input():
    """Get custom scene input from user"""
    st.subheader("🎯 Custom Single Scene Generation")
    st.info("Create a specific scene with your own instructions and details. Perfect for targeted training content.")
    
    # Custom scene form
    with st.form("custom_scene_form"):
        st.markdown("**Scene Configuration**")
        
        duration = st.number_input(
            "Duration (seconds)",
            min_value=5,
            max_value=15,
            value=8,
            help="Video duration in seconds"
        )
        
        st.markdown("**Visual Description**")
        visual_description = st.text_area(
            "Visual Scene Description",
            placeholder="Describe exactly what should happen visually in this scene. Include character actions, expressions, camera angles, workplace setting, etc.\n\nExample: 'In a modern Indian corporate office, a senior manager approaches a junior female employee at her desk and makes an inappropriate comment about her appearance. Show the employee's uncomfortable reaction and the manager's inappropriate behavior clearly.'",
            height=150
        )
        
        st.markdown("**System Instructions (Optional)**")
        system_instructions = st.text_area(
            "Additional System Instructions",
            placeholder="Any specific instructions for the AI video generator. E.g., camera angles, lighting, specific actions, cultural context, etc.\n\nExample: 'Use close-up shots to show facial expressions. Focus on authentic Indian office environment with modern furniture. Include realistic background office sounds.'",
            height=100
        )
        
        # Submit button
        submitted = st.form_submit_button("🎬 Generate Custom Scene", type="primary", use_container_width=True)
        
        if submitted:
            # Validate inputs
            if not visual_description.strip():
                st.error("Please provide a visual description.")
                return None
            
            if len(visual_description.strip()) < 20:
                st.error("Please provide a more detailed visual description (at least 20 characters).")
                return None
            
            # Return custom scene data with auto-generated defaults
            return {
                "mode": "custom",
                "scene_title": "Custom POSH Training Scene",  # Auto-generated
                "setting": "Indian corporate office",  # Auto-generated
                "characters": ["Employee 1", "Employee 2"],  # Auto-generated
                "duration": duration,
                "dialogue": "Professional workplace interaction demonstrating appropriate/inappropriate behavior.",  # Auto-generated
                "tone": "realistic and natural",  # Auto-generated
                "sound_effects": "Office ambience (20%), keyboard typing (15%), phone conversations (10%)",  # Auto-generated
                "visual_description": visual_description,
                "system_instructions": system_instructions
            }
    
    return None

def display_processed_scenario(scenario: POSHScenario):
    """Display the processed scenario with scenes"""
    st.header("📋 Step 2: AI-Generated Scene Breakdown")
    
    # Scenario overview
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"🎭 {scenario.title}")
        st.write(scenario.description)
        
    with col2:
        st.metric("Total Scenes", len(scenario.scenes))
        st.metric("Total Duration", f"{scenario.total_duration}s")
    
    # Learning objectives
    st.subheader("🎯 Learning Objectives")
    for i, objective in enumerate(scenario.learning_objectives, 1):
        st.write(f"{i}. {objective}")
    
    # Scene details
    st.subheader("🎬 Scene Breakdown")
    
    for scene in scenario.scenes:
        with st.expander(f"Scene {scene.scene_number}: {scene.setting}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Visual Description:**")
                st.write(scene.visual_description)
                
                st.markdown(f"**Dialogue:**")
                st.write(f'"{scene.audio_script.dialogue}"')
                
                if scene.audio_script.sound_effects:
                    st.markdown(f"**Sound Effects:** {scene.audio_script.sound_effects}")
                
            with col2:
                st.markdown(f"**Setting:** {scene.setting}")
                st.markdown(f"**Characters:** {', '.join(scene.characters)}")
                st.markdown(f"**Tone:** {scene.audio_script.tone}")
                st.markdown(f"**Duration:** {scene.duration_seconds}s")

async def run_video_generation(scenario_text: str):
    """Run the video generation workflow"""
    try:
        # Initialize workflow
        workflow = POSHVideoWorkflow()
        
        # Create progress placeholders
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run workflow with progress updates
        status_text.text("🔄 Starting workflow...")
        
        # This is a simplified version - in a real implementation,
        # you'd want to run this in a separate thread and update progress
        result = await workflow.run_workflow(scenario_text)
        
        return result
        
    except Exception as e:
        st.error(f"Error during video generation: {e}")
        return None

async def run_custom_scene_generation(scene_data: dict):
    """Run custom scene generation"""
    try:
        from video_generator import VideoGenerator
        import time
        
        # Create progress placeholders
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Creating custom scene...")
        progress_bar.progress(0.1)
        
        # Create AudioScript object
        audio_script = AudioScript(
            dialogue=scene_data["dialogue"],
            sound_effects=scene_data["sound_effects"],
            tone=scene_data["tone"],
            background_narration=None,
            audio_transitions=None
        )
        
        # Create Scene object
        scene = Scene(
            scene_number=1,
            visual_description=scene_data["visual_description"],
            audio_script=audio_script,
            duration_seconds=scene_data["duration"],
            setting=scene_data["setting"],
            characters=scene_data["characters"],
            continuity_notes=None
        )
        
        status_text.text("🔄 Initializing video generator...")
        progress_bar.progress(0.2)
        
        # Initialize video generator
        generator = VideoGenerator()
        
        status_text.text("🔄 Generating custom scene video with Veo 3.0...")
        progress_bar.progress(0.3)
        
        # Create filename
        safe_title = "".join(c for c in scene_data["scene_title"] if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"Custom_{safe_title}_{int(time.time())}.mp4"
        
        # Generate video with custom system instructions
        result = await generate_custom_scene_video(generator, scene, filename, scene_data["system_instructions"])
        
        progress_bar.progress(1.0)
        status_text.text("✅ Custom scene generated successfully!")
        
        if result.success:
            return {
                "success": True,
                "scene": scene,
                "result": result,
                "scene_data": scene_data
            }
        else:
            return {
                "success": False,
                "error_message": result.error_message
            }
        
    except Exception as e:
        st.error(f"Error during custom scene generation: {e}")
        return {
            "success": False,
            "error_message": str(e)
        }

async def generate_custom_scene_video(generator, scene: Scene, output_filename: str, system_instructions: str = ""):
    """Generate video for a custom scene with additional system instructions"""
    import time
    import os
    from config import Config
    
    start_time = time.time()
    
    try:
        # Create enhanced prompt with system instructions
        prompt = create_custom_scene_prompt(scene, system_instructions)
        
        print(f"Generating custom scene video...")
        print(f"Prompt: {prompt[:200]}...")
        
        # Generate video using Veo 3.0
        operation = generator.client.models.generate_videos(
            model=Config.VIDEO_MODEL,
            prompt=prompt,
        )
        
        # Poll for completion
        print(f"Waiting for custom scene video generation...")
        while not operation.done:
            print(f"Custom scene: Still processing...")
            time.sleep(10)
            operation = generator.client.operations.get(operation)
        
        # Download the generated video
        generated_video = operation.response.generated_videos[0]
        output_path = os.path.join(Config.TEMP_DIR, output_filename)
        
        # Download and save video
        generator.client.files.download(file=generated_video.video)
        generated_video.video.save(output_path)
        
        generation_time = time.time() - start_time
        
        print(f"Custom scene generated successfully in {generation_time:.2f} seconds")
        
        return VideoGenerationResult(
            scene_number=scene.scene_number,
            video_path=output_path,
            success=True,
            generation_time=generation_time
        )
        
    except Exception as e:
        generation_time = time.time() - start_time
        error_msg = f"Error generating custom scene: {str(e)}"
        print(error_msg)
        
        return VideoGenerationResult(
            scene_number=scene.scene_number,
            video_path="",
            success=False,
            error_message=error_msg,
            generation_time=generation_time
        )

def create_custom_scene_prompt(scene: Scene, system_instructions: str = ""):
    """Create a custom prompt for Veo 3.0 with user's system instructions"""
    
    # Educational context header
    educational_header = """
EDUCATIONAL TRAINING VIDEO - WORKPLACE ETHICS CONTENT:
This is an educational training video for corporate workplace ethics and professional behavior standards.
Content is designed for HR training purposes to demonstrate appropriate workplace conduct and professional interactions.
All scenarios are educational simulations for learning proper workplace behavior and communication.
"""

    # Base visual description
    visual_prompt = scene.visual_description
    
    # Setting and character context
    setting_context = f"Indian workplace setting: {scene.setting}."
    character_context = f"Indian characters: {', '.join(scene.characters)}." if scene.characters else ""
    
    # Audio context
    dialogue_context = f"Primary dialogue: '{scene.audio_script.dialogue}'"
    tone_context = f"Emotional tone and delivery: {scene.audio_script.tone}"
    sound_effects_context = f"Layered background audio: {scene.audio_script.sound_effects}" if scene.audio_script.sound_effects else ""
    
    # Indian cultural context
    indian_context = """
INDIAN CULTURAL CONTEXT:
- Authentic Indian office environment with typical Indian corporate settings
- Characters with realistic Indian appearances, diverse regional backgrounds
- Traditional Indian business attire mixed with modern corporate wear
- Natural Indian workplace dynamics, hierarchies, and communication styles
- Realistic Indian office interiors: modern furniture, typical lighting, Indian corporate aesthetics
- Authentic body language and gestures common in Indian professional interactions
"""
    
    # Enhanced audio requirements
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
"""
    
    # Visual requirements
    visual_requirements = """
VISUAL REQUIREMENTS:
- MAXIMUM REALISM: Organic, natural character movements and expressions
  * Authentic Indian faces with diverse regional features and natural skin tones
  * Realistic office lighting and professional cinematic camera work
  * Natural, unforced interactions between characters with authentic body language
  * Authentic Indian workplace clothing and professional styling

- VISUAL STORYTELLING: Professional video quality with clear narrative
  * Smooth visual composition and professional camera work
  * Natural character reactions and emotional expressions matching the audio tone
  * Consistent visual style and appropriate lighting
"""
    
    # User's custom system instructions
    custom_instructions = ""
    if system_instructions.strip():
        custom_instructions = f"""
CUSTOM SYSTEM INSTRUCTIONS:
{system_instructions.strip()}

IMPORTANT: Follow these custom instructions while maintaining all other requirements.
"""
    
    # Combine all elements
    full_prompt = f"""
{educational_header.strip()}

{visual_prompt}

{setting_context} {character_context}

{dialogue_context} delivered with {tone_context}.

{sound_effects_context}

{indian_context.strip()}

{audio_requirements.strip()}

{visual_requirements.strip()}

{custom_instructions}

FINAL SPECIFICATIONS:
- {scene.duration_seconds}-second duration, 720p resolution, professional quality
- Educational workplace ethics training content for Indian corporate context
- Professional workplace interactions demonstrating proper business conduct
- Enhanced audio mixing with specified volume levels and layered soundscape
- Follow all custom instructions while maintaining educational and professional standards
""".strip()
    
    return full_prompt

def display_video_generation_results(video_summary: dict):
    """Display the generated videos"""
    st.header("🎬 Step 3: Generated Videos")
    
    if not video_summary or not video_summary.get('videos'):
        st.warning("No videos generated yet.")
        return
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Successfully Generated", video_summary['successful_scenes'])
    with col2:
        st.metric("Total Scenes", video_summary['total_scenes'])
    with col3:
        st.metric("Failed", video_summary.get('failed_scenes', 0))
    
    # Display videos
    st.subheader("📹 Individual Scene Videos")
    
    for video in video_summary['videos']:
        if not video['file_info'].get('exists'):
            continue
            
        with st.container():
            st.markdown(f"### Scene {video['scene_number']}: {video['setting']}")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Video player
                video_path = video['video_path']
                if os.path.exists(video_path):
                    try:
                        # Display video
                        st.video(video_path)
                    except Exception as e:
                        st.error(f"Could not display video: {e}")
                        st.info(f"Video saved at: {video_path}")
                else:
                    st.error(f"Video file not found: {video_path}")
            
            with col2:
                st.markdown(f"**Characters:** {', '.join(video['characters'])}")
                st.markdown(f"**Dialogue:**")
                st.write(f'"{video["dialogue"]}"')
                
                file_info = video['file_info']
                if 'file_size_mb' in file_info:
                    st.markdown(f"**File Size:** {file_info['file_size_mb']:.1f} MB")
                
                if video.get('generation_time'):
                    st.markdown(f"**Generation Time:** {video['generation_time']:.1f}s")
        
        st.markdown("---")

def display_custom_scene_result(custom_result: dict):
    """Display the custom scene generation result"""
    st.header("🎬 Step 2: Custom Scene Generated")
    
    if not custom_result.get('success'):
        st.error(f"❌ Error: {custom_result.get('error_message', 'Unknown error')}")
        return
    
    scene = custom_result['scene']
    result = custom_result['result']
    scene_data = custom_result['scene_data']
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Status", "✅ Success")
    with col2:
        st.metric("Duration", f"{scene.duration_seconds}s")
    with col3:
        st.metric("Generation Time", f"{result.generation_time:.1f}s")
    
    # Scene details
    st.subheader("📋 Scene Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Title:** {scene_data['scene_title']}")
        st.markdown(f"**Setting:** {scene.setting}")
        st.markdown(f"**Characters:** {', '.join(scene.characters)}")
        st.markdown(f"**Tone:** {scene.audio_script.tone}")
    
    with col2:
        st.markdown(f"**Dialogue:**")
        st.write(f'"{scene.audio_script.dialogue}"')
        
        if scene.audio_script.sound_effects:
            st.markdown(f"**Sound Effects:** {scene.audio_script.sound_effects}")
    
    if scene_data.get('system_instructions'):
        st.markdown(f"**Custom Instructions:** {scene_data['system_instructions']}")
    
    # Video display
    st.subheader("🎬 Generated Video")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        video_path = result.video_path
        if os.path.exists(video_path):
            try:
                st.video(video_path)
            except Exception as e:
                st.error(f"Could not display video: {e}")
                st.info(f"Video saved at: {video_path}")
        else:
            st.error(f"Video file not found: {video_path}")
    
    with col2:
        st.markdown(f"**Visual Description:**")
        st.write(scene.visual_description)
        
        # File info
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            st.markdown(f"**File Size:** {file_size:.1f} MB")
            st.markdown(f"**File Path:** `{os.path.basename(video_path)}`")
        
        # Download button
        if os.path.exists(video_path):
            with open(video_path, "rb") as file:
                st.download_button(
                    label="📥 Download Video",
                    data=file.read(),
                    file_name=os.path.basename(video_path),
                    mime="video/mp4"
                )

def main():
    """Main Streamlit application"""
    initialize_session_state()
    display_header()
    display_sidebar()
    
    # Main content area
    scenario_input = get_scenario_input()
    
    # Handle different generation modes
    if st.session_state.generation_mode == "custom":
        # Custom scene mode
        if scenario_input and isinstance(scenario_input, dict) and scenario_input.get("mode") == "custom":
            # Set generation in progress
            st.session_state.generation_in_progress = True
            
            # Show progress
            with st.spinner("Generating your custom scene video..."):
                try:
                    result = asyncio.run(run_custom_scene_generation(scenario_input))
                    
                    if result and result.get('success'):
                        st.session_state.custom_scene_result = result
                        st.success("🎉 Custom scene generated successfully!")
                        st.rerun()
                    else:
                        error_msg = result.get('error_message', 'Unknown error') if result else 'Generation failed'
                        st.error(f"❌ Error: {error_msg}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                finally:
                    st.session_state.generation_in_progress = False
    
    else:
        # Automatic mode
        if scenario_input and isinstance(scenario_input, str):
            # Generate button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Generate POSH Training Videos", type="primary", use_container_width=True):
                    if not scenario_input.strip():
                        st.error("Please enter a scenario description.")
                        return
                    
                    if len(scenario_input.strip()) < 50:
                        st.error("Please provide a more detailed scenario (at least 50 characters).")
                        return
                    
                    # Set generation in progress
                    st.session_state.generation_in_progress = True
                    
                    # Show progress
                    with st.spinner("Generating your POSH training videos..."):
                        # Run the workflow
                        try:
                            result = asyncio.run(run_video_generation(scenario_input))
                            
                            if result and not result.get('error_message'):
                                st.session_state.workflow_state = result
                                st.session_state.processed_scenario = result.get('processed_scenario')
                                st.session_state.generation_results = result.get('generation_results', [])
                                st.session_state.video_summary = result.get('video_summary', {})
                                
                                st.success("🎉 Video generation completed successfully!")
                                st.rerun()
                            else:
                                error_msg = result.get('error_message', 'Unknown error') if result else 'Generation failed'
                                st.error(f"❌ Error: {error_msg}")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                        finally:
                            st.session_state.generation_in_progress = False
    
    # Display results based on mode
    if st.session_state.generation_mode == "custom":
        # Display custom scene result
        if st.session_state.custom_scene_result:
            st.markdown("---")
            display_custom_scene_result(st.session_state.custom_scene_result)
    
    else:
        # Display automatic generation results
        if st.session_state.processed_scenario:
            st.markdown("---")
            display_processed_scenario(st.session_state.processed_scenario)
        
        if st.session_state.video_summary:
            st.markdown("---")
            display_video_generation_results(st.session_state.video_summary)
            
            # Download section
            st.header("📥 Download Options")
            
            video_summary = st.session_state.video_summary
            if video_summary.get('videos'):
                st.info(f"All videos are saved in the `{Config.TEMP_DIR}` folder for your review.")
                
                # Create download links for individual videos
                st.subheader("Individual Video Files:")
                for video in video_summary['videos']:
                    if video['file_info'].get('exists'):
                        video_path = video['video_path']
                        filename = os.path.basename(video_path)
                        st.markdown(f"- **Scene {video['scene_number']}:** `{filename}`")
    
    # Mode switching controls
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Switch to " + ("Automatic Mode" if st.session_state.generation_mode == "custom" else "Custom Scene Mode")):
            # Clear results when switching modes
            st.session_state.workflow_state = None
            st.session_state.processed_scenario = None
            st.session_state.generation_results = []
            st.session_state.video_summary = {}
            st.session_state.custom_scene_result = None
            st.session_state.generation_mode = "automatic" if st.session_state.generation_mode == "custom" else "custom"
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All Results"):
            # Clear all session state
            st.session_state.workflow_state = None
            st.session_state.processed_scenario = None
            st.session_state.generation_results = []
            st.session_state.video_summary = {}
            st.session_state.custom_scene_result = None
            st.success("All results cleared!")
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit, Google Gemini 2.5 Flash, and Veo 3.0 | "
        "For educational purposes only"
    )

if __name__ == "__main__":
    # Check configuration
    try:
        Config.validate()
        main()
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {e}")
        st.info("Please ensure your GEMINI_API_KEY is set in the .env file.")
    except Exception as e:
        st.error(f"⚠️ Startup Error: {e}")
