#!/usr/bin/env python3
"""
debug_echomind.py - Comprehensive Debugging Tool for EchoMind

This tool helps diagnose why prompts are being ignored and tests the complete
integration between echomind_gui.py and cognition.py
"""

import sys
import os
import traceback
import datetime
import importlib.util
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

def check_file_exists(filepath):
    """Check if a file exists and is readable"""
    if os.path.exists(filepath):
        if os.access(filepath, os.R_OK):
            return "✅ EXISTS & READABLE"
        else:
            return "⚠️ EXISTS BUT NOT READABLE"
    else:
        return "❌ MISSING"

def check_python_imports():
    """Check if all required Python packages are available"""
    print_section("Python Package Verification")
    
    required_packages = [
        "torch", "transformers", "textblob", "scikit-learn", 
        "nltk", "PyQt5", "requests", "feedparser", "beautifulsoup4"
    ]
    
    results = {}
    for package in required_packages:
        try:
            __import__(package)
            results[package] = "✅ INSTALLED"
            print(f"  {package}: ✅ Available")
        except ImportError as e:
            results[package] = f"❌ MISSING: {e}"
            print(f"  {package}: ❌ Not found - {e}")
    
    return results

def check_echomind_files():
    """Check for all EchoMind component files"""
    print_section("EchoMind File Structure Verification")
    
    # Core files that should exist
    core_files = [
        "echomind_gui.py",
        "cognition.py",
        "config.py",
        "semantic_lexicon.py",
        "self_state.py",
        "trait_engine.py",
        "goal_tracker.py",
        "values.py",
        "dreams.py",
        "dialogue.py",
        "llm_interface.py",
        "enrichment_llm.py",
        "thread_utils.py",
        "mind_stream.py",
        "activity_state.py",
        "download_mistral.sh"
    ]
    
    file_status = {}
    for filename in core_files:
        status = check_file_exists(filename)
        file_status[filename] = status
        print(f"  {filename}: {status}")
    
    # Check directories
    directories = ["logs", "models", "data"]
    print(f"\n📁 Directory Structure:")
    for dirname in directories:
        if os.path.exists(dirname) and os.path.isdir(dirname):
            print(f"  {dirname}/: ✅ EXISTS")
        else:
            print(f"  {dirname}/: ❌ MISSING")
            try:
                os.makedirs(dirname, exist_ok=True)
                print(f"    Created {dirname}/ directory")
            except Exception as e:
                print(f"    Failed to create {dirname}/: {e}")
    
    return file_status

def test_component_imports():
    """Test importing all EchoMind components"""
    print_section("Component Import Testing")
    
    components = [
        ("semantic_lexicon", "LanguageModel"),
        ("self_state", "SelfState"),
        ("trait_engine", "TraitEngine"),
        ("goal_tracker", "GoalTracker"),
        ("values", "ValueSystem"),
        ("dreams", "generate_and_log_dream"),
        ("dialogue", "generate_internal_thought"),
        ("thread_utils", "TaskRunner"),
        ("activity_state", "set_activity"),
        ("mind_stream", "stream_log_file")
    ]
    
    import_results = {}
    
    for module_name, class_or_function in components:
        try:
            module = __import__(module_name)
            if hasattr(module, class_or_function):
                import_results[module_name] = "✅ SUCCESS"
                print(f"  {module_name}.{class_or_function}: ✅ Available")
            else:
                import_results[module_name] = f"⚠️ MODULE OK, {class_or_function} MISSING"
                print(f"  {module_name}.{class_or_function}: ⚠️ Module loads but {class_or_function} not found")
        except ImportError as e:
            import_results[module_name] = f"❌ IMPORT ERROR: {e}"
            print(f"  {module_name}: ❌ Import failed - {e}")
        except Exception as e:
            import_results[module_name] = f"❌ ERROR: {e}"
            print(f"  {module_name}: ❌ Error - {e}")
    
    return import_results

def test_cognition_integration():
    """Test the cognition.py integration"""
    print_section("Cognition Engine Integration Test")
    
    try:
        # Test if cognition.py exists and can be imported
        if not os.path.exists("cognition.py"):
            print("❌ cognition.py not found!")
            print("💡 This is likely why prompts are being ignored.")
            print("💡 Use the cognition.py from the provided artifacts.")
            return False
        
        # Try to import cognition
        try:
            import cognition
            print("✅ cognition.py imported successfully")
        except Exception as e:
            print(f"❌ cognition.py import failed: {e}")
            print("💡 This is likely why prompts are being ignored.")
            return False
        
        # Test key functions exist
        required_functions = [
            "process_user_input",
            "get_system_status",
            "get_cognition_engine"
        ]
        
        for func_name in required_functions:
            if hasattr(cognition, func_name):
                print(f"  ✅ {func_name} function available")
            else:
                print(f"  ❌ {func_name} function missing")
        
        # Test creating cognition engine
        try:
            if hasattr(cognition, 'CognitionEngine'):
                engine = cognition.CognitionEngine()
                print("✅ CognitionEngine can be instantiated")
                
                # Test basic processing
                test_response = engine.process_input("Hello, test message")
                if test_response and len(test_response) > 0:
                    print(f"✅ Basic processing works: '{test_response[:50]}...'")
                    return True
                else:
                    print("❌ Processing returns empty response")
                    return False
            else:
                print("❌ CognitionEngine class not found in cognition.py")
                return False
                
        except Exception as e:
            print(f"❌ CognitionEngine instantiation failed: {e}")
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Cognition integration test failed: {e}")
        return False

def test_llm_availability():
    """Test LLM model availability"""
    print_section("LLM Model Availability Test")
    
    try:
        # Check if config exists
        try:
            import config
            print("✅ config.py loaded")
            if hasattr(config, 'ACTIVE_LLM_MODEL'):
                print(f"📋 Active model: {config.ACTIVE_LLM_MODEL}")
            else:
                print("⚠️ ACTIVE_LLM_MODEL not defined in config.py")
        except ImportError:
            print("❌ config.py not found - using provided config.py")
        
        # Test torch and CUDA
        try:
            import torch
            print(f"✅ PyTorch available: {torch.__version__}")
            
            cuda_available = torch.cuda.is_available()
            print(f"🖥️ CUDA available: {cuda_available}")
            
            if cuda_available:
                print(f"🖥️ CUDA device: {torch.cuda.get_device_name(0)}")
                print(f"🖥️ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
            else:
                print("⚠️ No CUDA - LLM will run on CPU (very slow)")
                
        except Exception as e:
            print(f"❌ PyTorch test failed: {e}")
        
        # Test LLM interface
        try:
            from llm_interface import generate_from_context
            print("✅ LLM interface available")
            
            # Test minimal generation
            print("🔄 Testing LLM generation (this may take time)...")
            test_response = generate_from_context(
                "Test", 
                "Test context", 
                max_tokens=10
            )
            
            if test_response and len(test_response) > 0:
                print(f"✅ LLM generation works: '{test_response}'")
                return True
            else:
                print("❌ LLM returns empty response")
                return False
                
        except Exception as e:
            print(f"❌ LLM interface test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ LLM availability test failed: {e}")
        return False

def test_gui_integration():
    """Test GUI integration"""
    print_section("GUI Integration Test")
    
    if not os.path.exists("echomind_gui.py"):
        print("❌ echomind_gui.py not found!")
        return False
    
    try:
        # Try to parse the GUI file to see what it's trying to import
        with open("echomind_gui.py", "r") as f:
            gui_content = f.read()
        
        print("✅ echomind_gui.py found and readable")
        
        # Check what it imports from cognition
        if "from cognition import" in gui_content:
            print("✅ GUI imports from cognition module")
        elif "import cognition" in gui_content:
            print("✅ GUI imports cognition module")
        else:
            print("⚠️ GUI doesn't seem to import cognition - this could be the issue!")
        
        # Check for key GUI framework imports
        if "PyQt5" in gui_content or "PyQt6" in gui_content:
            print("✅ GUI uses PyQt")
        elif "tkinter" in gui_content:
            print("✅ GUI uses tkinter")
        else:
            print("⚠️ GUI framework not identified")
            
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")
        return False

def create_test_run():
    """Create a comprehensive test run of the system"""
    print_section("End-to-End System Test")
    
    try:
        # Import or create cognition engine
        try:
            from cognition import get_cognition_engine
            engine = get_cognition_engine()
            print("✅ Using existing cognition engine")
        except:
            # Use the provided cognition.py
            print("⚠️ Creating new cognition engine from provided code")
            # This would use the CognitionEngine from the artifacts
            print("💡 Use the cognition.py from the provided artifacts")
            return False
        
        # Test series of inputs
        test_inputs = [
            "Hello, can you hear me?",
            "What is your current mood?",
            "Tell me about your goals",
            "How do you process information?"
        ]
        
        print("🔄 Running end-to-end tests...")
        
        for i, test_input in enumerate(test_inputs, 1):
            print(f"\n  Test {i}: '{test_input}'")
            try:
                response = engine.process_input(test_input)
                if response and len(response.strip()) > 0:
                    print(f"  ✅ Response: '{response[:60]}...'")
                else:
                    print(f"  ❌ Empty or null response")
                    return False
            except Exception as e:
                print(f"  ❌ Processing failed: {e}")
                return False
        
        # Test system status
        try:
            status = engine.get_system_status()
            print(f"\n📊 System Status: {status}")
            return True
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ End-to-end test failed: {e}")
        traceback.print_exc()
        return False

def generate_fix_recommendations(results):
    """Generate specific recommendations based on test results"""
    print_section("Fix Recommendations")
    
    recommendations = []
    
    # Check for missing files
    if not os.path.exists("cognition.py"):
        recommendations.append({
            "priority": "HIGH",
            "issue": "cognition.py missing",
            "fix": "Use the cognition.py from the provided artifacts. This is likely why prompts are ignored.",
            "action": "Copy the cognition.py code from the artifacts into your project"
        })
    
    if not os.path.exists("config.py"):
        recommendations.append({
            "priority": "HIGH", 
            "issue": "config.py missing",
            "fix": "Use the config.py from the provided artifacts",
            "action": "Copy the config.py code from the artifacts into your project"
        })
    
    # Check for import issues
    for module, status in results.get("imports", {}).items():
        if "❌" in status:
            if "torch" in module:
                recommendations.append({
                    "priority": "HIGH",
                    "issue": f"PyTorch not available",
                    "fix": "Install PyTorch: pip install torch transformers",
                    "action": "Run: pip install torch transformers"
                })
            elif "PyQt5" in module:
                recommendations.append({
                    "priority": "MEDIUM",
                    "issue": "PyQt5 not available",
                    "fix": "Install PyQt5: pip install PyQt5",
                    "action": "Run: pip install PyQt5"
                })
    
    # Display recommendations
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. [{rec['priority']} PRIORITY] {rec['issue']}")
        print(f"   💡 Fix: {rec['fix']}")
        print(f"   🔧 Action: {rec['action']}")
    
    if not recommendations:
        print("✅ No critical issues found!")
    
    return recommendations

def main():
    """Main debugging function"""
    print_header("EchoMind System Diagnostic Tool")
    print("This tool will help identify why prompts are being ignored")
    
    results = {}
    
    # Test 1: File structure
    results["files"] = check_echomind_files()
    
    # Test 2: Python packages  
    results["packages"] = check_python_imports()
    
    # Test 3: Component imports
    results["imports"] = test_component_imports()
    
    # Test 4: Cognition integration
    results["cognition"] = test_cognition_integration()
    
    # Test 5: LLM availability
    results["llm"] = test_llm_availability()
    
    # Test 6: GUI integration
    results["gui"] = test_gui_integration()
    
    # Test 7: End-to-end test
    results["e2e"] = create_test_run()
    
    # Generate recommendations
    recommendations = generate_fix_recommendations(results)
    
    # Summary
    print_header("Diagnostic Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result is True)
    
    print(f"📊 Tests completed: {total_tests}")
    print(f"✅ Tests passed: {passed_tests}")
    print(f"❌ Tests failed: {total_tests - passed_tests}")
    
    if results.get("cognition") != True:
        print("\n🚨 CRITICAL ISSUE DETECTED:")
        print("   The cognition.py integration failed.")
        print("   This is most likely why your prompts are being ignored.")
        print("   Use the cognition.py from the provided artifacts.")
    
    print(f"\n📋 Detailed results saved to: debug_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    # Save detailed results
    try:
        log_filename = f"debug_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        with open(log_filename, "w") as f:
            f.write("EchoMind Diagnostic Results\n")
            f.write("=" * 40 + "\n\n")
            for category, result in results.items():
                f.write(f"{category}: {result}\n")
            f.write(f"\nRecommendations:\n")
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")
    except Exception as e:
        print(f"⚠️ Could not save detailed results: {e}")

if __name__ == "__main__":
    main()
