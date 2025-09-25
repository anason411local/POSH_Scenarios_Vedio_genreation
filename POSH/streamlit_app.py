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
from models import POSHScenario
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
        st.markdown("""
        **Step 1:** Enter your POSH scenario
        
        **Step 2:** AI breaks it into 8-second scenes
        
        **Step 3:** Veo 3.0 generates individual videos
        
        **Step 4:** Review each scene video
        """)
        
        st.header("💡 Tips for Better Scenarios")
        st.markdown("""
        • Be specific about workplace setting
        • Include character descriptions
        • Describe inappropriate behavior clearly
        • Mention proper resolution process
        • Keep it realistic and educational
        """)
        
        st.header("⚙️ Configuration")
        st.info(f"**Video Duration:** {Config.VIDEO_DURATION_SECONDS} seconds per scene")
        st.info(f"**Target Total:** {Config.TARGET_TOTAL_DURATION[0]}-{Config.TARGET_TOTAL_DURATION[1]} seconds")
        st.info(f"**Resolution:** {Config.VIDEO_RESOLUTION}")

def get_scenario_input():
    """Get scenario input from user"""
    st.header("📝 Step 1: Enter Your POSH Scenario")
    
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

def main():
    """Main Streamlit application"""
    initialize_session_state()
    display_header()
    display_sidebar()
    
    # Main content area
    scenario_text = get_scenario_input()
    
    # Generate button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate POSH Training Videos", type="primary", use_container_width=True):
            if not scenario_text.strip():
                st.error("Please enter a scenario description.")
                return
            
            if len(scenario_text.strip()) < 50:
                st.error("Please provide a more detailed scenario (at least 50 characters).")
                return
            
            # Set generation in progress
            st.session_state.generation_in_progress = True
            
            # Show progress
            with st.spinner("Generating your POSH training videos..."):
                # Run the workflow
                try:
                    result = asyncio.run(run_video_generation(scenario_text))
                    
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
    
    # Display results if available
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
