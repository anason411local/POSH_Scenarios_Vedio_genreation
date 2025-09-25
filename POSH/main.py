"""
POSH Video Generation System - Main Application
Multi-step video generation using Gemini 2.5 Flash and Veo 3.0
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from workflow import POSHVideoWorkflow, WorkflowState
from config import Config

class POSHVideoApp:
    """Main application class for POSH video generation"""
    
    def __init__(self):
        """Initialize the application"""
        self.workflow = POSHVideoWorkflow()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [Config.OUTPUT_DIR, Config.TEMP_DIR]
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def display_banner(self):
        """Display application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                    POSH VIDEO GENERATION SYSTEM                  ║
║              Prevention of Sexual Harassment Training            ║
║                                                                  ║
║  Powered by: Gemini 2.5 Flash + Veo 3.0 + LangGraph           ║
╚══════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def display_instructions(self):
        """Display usage instructions"""
        instructions = """
📋 INSTRUCTIONS:
1. Enter your POSH scenario description when prompted
2. The system will break it down into 8-second scenes (60-90 seconds total)
3. Each scene will be generated using Veo 3.0 with audio
4. Individual scene videos will be saved for your review
5. Videos will be saved in the 'temp_scenes' folder

💡 TIPS FOR BETTER SCENARIOS:
• Be specific about the workplace setting
• Include character descriptions and interactions
• Describe the inappropriate behavior clearly
• Mention the correct response or resolution
• Keep it realistic and educational

📹 OUTPUT:
• Each scene will be generated as a separate 8-second video
• You can review each scene individually 
• All videos will be saved in the 'temp_scenes' folder
• A summary file will list all generated videos with details

Example: "A manager repeatedly making inappropriate comments to a junior 
employee during team meetings, making them uncomfortable. The scenario 
shows other colleagues noticing and the proper way to report and address 
such behavior through HR channels."
"""
        print(instructions)
    
    def get_user_scenario(self) -> str:
        """Get scenario input from user"""
        print("\n" + "="*60)
        print("📝 ENTER YOUR POSH SCENARIO:")
        print("="*60)
        print("(Press Enter twice when finished, or type 'quit' to exit)")
        print()
        
        lines = []
        empty_line_count = 0
        
        while True:
            try:
                line = input().strip()
                
                if line.lower() == 'quit':
                    return None
                
                if line == "":
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                    lines.append(line)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return None
        
        scenario = " ".join(lines).strip()
        
        if not scenario:
            print("❌ No scenario provided.")
            return None
        
        if len(scenario) < 50:
            print("⚠️ Scenario seems too short. Please provide more details.")
            return self.get_user_scenario()
        
        return scenario
    
    def confirm_scenario(self, scenario: str) -> bool:
        """Confirm scenario with user before processing"""
        print("\n" + "="*60)
        print("📖 YOUR SCENARIO:")
        print("="*60)
        print(f"{scenario}")
        print("="*60)
        
        while True:
            response = input("\n✅ Proceed with this scenario? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    async def process_scenario(self, scenario: str) -> WorkflowState:
        """Process the scenario through the workflow"""
        print(f"\n⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run the workflow
        result = await self.workflow.run_workflow(scenario)
        
        print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return result
    
    def display_results(self, result: WorkflowState):
        """Display final results"""
        print("\n" + "="*60)
        print("📊 GENERATION RESULTS:")
        print("="*60)
        
        if result.get("error_message"):
            print(f"❌ Error: {result['error_message']}")
            return
        
        if result.get("video_summary"):
            video_summary = result["video_summary"]
            print(f"🎭 Scenario: {video_summary['scenario_title']}")
            print(f"📝 Description: {video_summary['scenario_description']}")
            print(f"🎬 Videos Generated: {video_summary['successful_scenes']}/{video_summary['total_scenes']}")
            
            if video_summary['failed_scenes'] > 0:
                print(f"⚠️  Failed Scenes: {video_summary['failed_scenes']}")
            
            print(f"\n📁 Individual Scene Videos:")
            for video in video_summary['videos']:
                file_info = video['file_info']
                if file_info.get('exists'):
                    print(f"   Scene {video['scene_number']}: {os.path.basename(video['video_path'])}")
                    print(f"      Setting: {video['setting']}")
                    print(f"      Size: {file_info.get('file_size_mb', 0):.1f} MB")
            
            print(f"\n📋 Learning Objectives:")
            for i, obj in enumerate(video_summary['learning_objectives'], 1):
                print(f"   {i}. {obj}")
        
        print("\n✅ Individual scene videos generated successfully!")
        print(f"📂 Check the '{Config.TEMP_DIR}' folder for your scene videos.")
        print(f"📄 A detailed video list file has been created in '{Config.OUTPUT_DIR}'.")
    
    def display_error(self, error_msg: str):
        """Display error message"""
        print("\n" + "="*60)
        print("❌ ERROR:")
        print("="*60)
        print(f"{error_msg}")
        print("\n💡 Please try again with a different scenario or check your configuration.")
    
    async def run_interactive(self):
        """Run the application in interactive mode"""
        self.display_banner()
        self.display_instructions()
        
        while True:
            try:
                # Get user scenario
                scenario = self.get_user_scenario()
                if scenario is None:
                    print("\n👋 Goodbye!")
                    break
                
                # Confirm scenario
                if not self.confirm_scenario(scenario):
                    print("Let's try again with a different scenario.\n")
                    continue
                
                # Process scenario
                print("\n🚀 Starting video generation process...")
                result = await self.process_scenario(scenario)
                
                # Display results
                if result.get("error_message"):
                    self.display_error(result["error_message"])
                else:
                    self.display_results(result)
                
                # Ask if user wants to generate another video
                print("\n" + "="*60)
                while True:
                    again = input("🔄 Generate another video? (y/n): ").strip().lower()
                    if again in ['y', 'yes']:
                        print("\n")
                        break
                    elif again in ['n', 'no']:
                        print("\n👋 Thank you for using POSH Video Generation System!")
                        return
                    else:
                        print("Please enter 'y' for yes or 'n' for no.")
                        
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                self.display_error(f"Unexpected error: {str(e)}")
                print("\nPlease try again.")
    
    async def run_batch(self, scenario_file: str):
        """Run in batch mode with scenario from file"""
        try:
            with open(scenario_file, 'r', encoding='utf-8') as f:
                scenario = f.read().strip()
            
            if not scenario:
                print(f"❌ Empty scenario file: {scenario_file}")
                return
            
            print(f"📖 Processing scenario from: {scenario_file}")
            print(f"Scenario: {scenario[:100]}...")
            
            result = await self.process_scenario(scenario)
            
            if result.get("error_message"):
                self.display_error(result["error_message"])
            else:
                self.display_results(result)
                
        except FileNotFoundError:
            print(f"❌ Scenario file not found: {scenario_file}")
        except Exception as e:
            self.display_error(f"Error reading scenario file: {str(e)}")

def main():
    """Main entry point"""
    app = POSHVideoApp()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Batch mode
        scenario_file = sys.argv[1]
        asyncio.run(app.run_batch(scenario_file))
    else:
        # Interactive mode
        asyncio.run(app.run_interactive())

if __name__ == "__main__":
    try:
        # Validate configuration
        Config.validate()
        main()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please check your .env file and ensure GEMINI_API_KEY is set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup Error: {e}")
        sys.exit(1)
