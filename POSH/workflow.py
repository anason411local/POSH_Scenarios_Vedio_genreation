"""
LangGraph Workflow for POSH Video Generation
Orchestrates the multi-step process from scenario input to final video
"""
import asyncio
from typing import Dict, List, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain.schema import BaseMessage
from scenario_processor import ScenarioProcessor
from video_generator import VideoGenerator
from video_combiner import VideoCombiner
from models import POSHScenario, VideoGenerationResult

class WorkflowState(TypedDict):
    """State object for the LangGraph workflow"""
    user_scenario: str
    processed_scenario: POSHScenario
    generation_results: List[VideoGenerationResult]
    video_summary: dict
    error_message: str
    current_step: str
    progress: float

class POSHVideoWorkflow:
    """LangGraph workflow for POSH video generation"""
    
    def __init__(self):
        """Initialize the workflow with all components"""
        self.scenario_processor = ScenarioProcessor()
        self.video_generator = VideoGenerator()
        self.video_combiner = VideoCombiner()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("process_scenario", self._process_scenario_node)
        workflow.add_node("validate_scenario", self._validate_scenario_node)
        workflow.add_node("generate_videos", self._generate_videos_node)
        workflow.add_node("organize_videos", self._organize_videos_node)
        workflow.add_node("finalize", self._finalize_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("process_scenario")
        
        # Add edges
        workflow.add_edge("process_scenario", "validate_scenario")
        workflow.add_conditional_edges(
            "validate_scenario",
            self._should_continue_after_validation,
            {
                "continue": "generate_videos",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "generate_videos",
            self._should_continue_after_generation,
            {
                "continue": "organize_videos",
                "error": "handle_error"
            }
        )
        workflow.add_edge("organize_videos", "finalize")
        workflow.add_edge("finalize", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    async def _process_scenario_node(self, state: WorkflowState) -> WorkflowState:
        """Process user scenario into structured scenes"""
        print("🔄 Step 1: Processing scenario with Gemini 2.5 Flash...")
        state["current_step"] = "Processing scenario"
        state["progress"] = 0.1
        
        try:
            processed_scenario = await self.scenario_processor.process_scenario(
                state["user_scenario"]
            )
            state["processed_scenario"] = processed_scenario
            
            print(f"✅ Scenario processed successfully!")
            print(f"   Title: {processed_scenario.title}")
            print(f"   Scenes: {len(processed_scenario.scenes)}")
            print(f"   Duration: {processed_scenario.total_duration} seconds")
            
            state["progress"] = 0.2
            
        except Exception as e:
            state["error_message"] = f"Error processing scenario: {str(e)}"
            print(f"❌ Error processing scenario: {e}")
        
        return state
    
    async def _validate_scenario_node(self, state: WorkflowState) -> WorkflowState:
        """Validate the processed scenario"""
        print("🔄 Step 2: Validating scenario structure...")
        state["current_step"] = "Validating scenario"
        state["progress"] = 0.25
        
        try:
            if "processed_scenario" not in state or state["processed_scenario"] is None:
                raise ValueError("No processed scenario to validate")
            
            self.scenario_processor.validate_scenario(state["processed_scenario"])
            print("✅ Scenario validation passed!")
            
            # Print scenario summary
            summary = self.scenario_processor.get_scenario_summary(state["processed_scenario"])
            print(f"\n{summary}\n")
            
            state["progress"] = 0.3
            
        except Exception as e:
            state["error_message"] = f"Error validating scenario: {str(e)}"
            print(f"❌ Error validating scenario: {e}")
        
        return state
    
    async def _generate_videos_node(self, state: WorkflowState) -> WorkflowState:
        """Generate videos for all scenes"""
        print("🔄 Step 3: Generating videos with Veo 3.0...")
        state["current_step"] = "Generating scene videos"
        state["progress"] = 0.35
        
        try:
            scenario = state["processed_scenario"]
            results = await self.video_generator.generate_all_scenes(
                scenario.scenes, 
                scenario.title
            )
            state["generation_results"] = results
            
            # Update progress based on completion
            successful_count = sum(1 for r in results if r.success)
            print(f"✅ Video generation completed: {successful_count}/{len(results)} successful")
            
            state["progress"] = 0.8
            
        except Exception as e:
            state["error_message"] = f"Error generating videos: {str(e)}"
            print(f"❌ Error generating videos: {e}")
        
        return state
    
    async def _organize_videos_node(self, state: WorkflowState) -> WorkflowState:
        """Organize individual scene videos for review"""
        print("🔄 Step 4: Organizing videos for individual review...")
        state["current_step"] = "Organizing videos"
        state["progress"] = 0.85
        
        try:
            video_summary = self.video_combiner.organize_scene_videos(
                state["generation_results"],
                state["processed_scenario"]
            )
            state["video_summary"] = video_summary
            
            # Print summary
            self.video_combiner.print_video_summary(video_summary)
            
            # Create video list file
            self.video_combiner.create_video_list_file(video_summary)
            
            print(f"✅ Videos organized successfully")
            state["progress"] = 0.95
            
        except Exception as e:
            state["error_message"] = f"Error organizing videos: {str(e)}"
            print(f"❌ Error organizing videos: {e}")
        
        return state
    
    async def _finalize_node(self, state: WorkflowState) -> WorkflowState:
        """Finalize the workflow"""
        print("🔄 Step 5: Finalizing...")
        state["current_step"] = "Complete"
        state["progress"] = 1.0
        
        # Show completion summary
        if state.get("video_summary"):
            video_summary = state["video_summary"]
            print(f"\n🎉 POSH Video Generation Complete!")
            print(f"   Scenario: {video_summary['scenario_title']}")
            print(f"   Videos Generated: {video_summary['successful_scenes']}/{video_summary['total_scenes']}")
            print(f"   All videos saved in: {Config.OUTPUT_DIR}/temp_scenes/")
            print(f"   Video list file created for easy reference")
        
        return state
    
    async def _handle_error_node(self, state: WorkflowState) -> WorkflowState:
        """Handle errors in the workflow"""
        print(f"❌ Workflow Error: {state.get('error_message', 'Unknown error')}")
        state["current_step"] = "Error"
        
        # Cleanup temporary files if needed
        try:
            self.video_generator.cleanup_temp_files(keep_successful=False)
        except:
            pass
        
        return state
    
    def _should_continue_after_validation(self, state: WorkflowState) -> str:
        """Decide whether to continue after validation"""
        if state.get("error_message"):
            return "error"
        return "continue"
    
    def _should_continue_after_generation(self, state: WorkflowState) -> str:
        """Decide whether to continue after video generation"""
        if state.get("error_message"):
            return "error"
        
        # Check if we have any successful videos
        results = state.get("generation_results", [])
        successful = [r for r in results if r.success]
        
        if not successful:
            state["error_message"] = "No videos were generated successfully"
            return "error"
        
        return "continue"
    
    async def run_workflow(self, user_scenario: str) -> WorkflowState:
        """
        Run the complete POSH video generation workflow
        
        Args:
            user_scenario: User-provided scenario description
            
        Returns:
            WorkflowState: Final state of the workflow
        """
        print("🚀 Starting POSH Video Generation Workflow")
        print("=" * 50)
        
        # Initialize state
        initial_state = WorkflowState(
            user_scenario=user_scenario,
            processed_scenario=None,
            generation_results=[],
            video_summary={},
            error_message="",
            current_step="Starting",
            progress=0.0
        )
        
        # Run workflow
        try:
            final_state = await self.workflow.ainvoke(initial_state)
            return final_state
        except Exception as e:
            print(f"❌ Workflow execution error: {e}")
            initial_state["error_message"] = f"Workflow execution error: {str(e)}"
            initial_state["current_step"] = "Error"
            return initial_state
    
    def get_workflow_status(self, state: WorkflowState) -> str:
        """Get a formatted status string for the workflow"""
        progress_bar = "█" * int(state["progress"] * 20) + "░" * (20 - int(state["progress"] * 20))
        return f"[{progress_bar}] {state['progress']*100:.0f}% - {state['current_step']}"
