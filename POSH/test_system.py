"""
Test script for POSH Video Generation System
Validates all components without generating actual videos
"""
import asyncio
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config imported")
        
        from models import POSHScenario, Scene, AudioScript, VideoGenerationResult
        print("✅ Models imported")
        
        from scenario_processor import ScenarioProcessor
        print("✅ Scenario processor imported")
        
        from video_generator import VideoGenerator
        print("✅ Video generator imported")
        
        from video_combiner import VideoCombiner
        print("✅ Video combiner imported")
        
        from workflow import POSHVideoWorkflow
        print("✅ Workflow imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_configuration():
    """Test configuration validation"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import Config
        Config.validate()
        print("✅ Configuration valid")
        print(f"   API Key: {'*' * 20}...{Config.GEMINI_API_KEY[-4:]}")
        print(f"   Scenario Model: {Config.SCENARIO_MODEL}")
        print(f"   Video Model: {Config.VIDEO_MODEL}")
        print(f"   Target Duration: {Config.TARGET_TOTAL_DURATION}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_directories():
    """Test directory creation"""
    print("\n🧪 Testing directories...")
    
    try:
        from config import Config
        directories = [Config.OUTPUT_DIR, Config.TEMP_DIR]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            if Path(directory).exists():
                print(f"✅ Directory exists: {directory}")
            else:
                print(f"❌ Directory missing: {directory}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Directory error: {e}")
        return False

async def test_scenario_processing():
    """Test scenario processing with a simple example"""
    print("\n🧪 Testing scenario processing...")
    
    try:
        from scenario_processor import ScenarioProcessor
        
        processor = ScenarioProcessor()
        print("✅ Scenario processor initialized")
        
        # Test with a simple scenario
        test_scenario = """A manager makes an inappropriate comment to an employee. 
        The employee feels uncomfortable and reports it to HR. 
        HR investigates and takes appropriate action."""
        
        print("⏳ Processing test scenario...")
        # Note: This will make an actual API call to test the connection
        result = await processor.process_scenario(test_scenario)
        
        print(f"✅ Scenario processed successfully")
        print(f"   Title: {result.title}")
        print(f"   Scenes: {len(result.scenes)}")
        print(f"   Duration: {result.total_duration}s")
        
        # Validate the result
        processor.validate_scenario(result)
        print("✅ Scenario validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Scenario processing error: {e}")
        return False

def test_component_initialization():
    """Test that all components can be initialized"""
    print("\n🧪 Testing component initialization...")
    
    try:
        from video_generator import VideoGenerator
        generator = VideoGenerator()
        print("✅ Video generator initialized")
        
        from video_combiner import VideoCombiner
        combiner = VideoCombiner()
        print("✅ Video combiner initialized")
        
        from workflow import POSHVideoWorkflow
        workflow = POSHVideoWorkflow()
        print("✅ Workflow initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Component initialization error: {e}")
        return False

def test_models():
    """Test Pydantic models"""
    print("\n🧪 Testing data models...")
    
    try:
        from models import AudioScript, Scene, POSHScenario
        
        # Test AudioScript
        audio = AudioScript(
            dialogue="This is a test dialogue",
            sound_effects="office ambience",
            tone="professional"
        )
        print("✅ AudioScript model works")
        
        # Test Scene
        scene = Scene(
            scene_number=1,
            visual_description="Test scene description",
            audio_script=audio,
            setting="Office",
            characters=["Person A", "Person B"]
        )
        print("✅ Scene model works")
        
        # Test POSHScenario
        scenario = POSHScenario(
            title="Test Scenario",
            description="Test description",
            scenes=[scene],
            total_duration=8,
            learning_objectives=["Test objective"]
        )
        print("✅ POSHScenario model works")
        
        return True
        
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

async def run_full_test():
    """Run all tests"""
    print("🚀 POSH Video Generation System - Full Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Directories", test_directories),
        ("Models", test_models),
        ("Component Initialization", test_component_initialization),
    ]
    
    results = []
    
    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        
        if not result:
            print(f"❌ {test_name} test failed - stopping here")
            break
    
    # Run async tests only if basic tests pass
    if all(result for _, result in results):
        print(f"\n📋 Running Scenario Processing test...")
        try:
            result = await test_scenario_processing()
            results.append(("Scenario Processing", result))
        except Exception as e:
            print(f"❌ Scenario Processing test failed: {e}")
            results.append(("Scenario Processing", False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! System is ready to use.")
        print("Run 'python main.py' to start the application.")
    else:
        print(f"\n⚠️ {len(results) - passed} test(s) failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        success = asyncio.run(run_full_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)
