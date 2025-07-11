# test_logging.py
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("🧪 Testing Recipe Assistant Logging Configuration")
print("=" * 50)

try:
    from src.config import setup_logging, get_logger
    print("✅ Successfully imported logging config")
except ImportError as e:
    print(f"❌ Failed to import logging config: {e}")
    sys.exit(1)

def main():
    try:
        print("\n🔧 Setting up logging...")
        
        setup_logging("recipe_assistant", log_level="DEBUG")
        
        print("✅ Logging setup complete")
        print("\n📝 Testing different log levels...")
        
        app_logger = get_logger('recipe_assistant.app')
        meal_logger = get_logger('meal_planner')
        api_logger = get_logger('api')
        
        app_logger.debug("This is a debug message")
        app_logger.info("Application started successfully")
        meal_logger.warning("This is a warning message")
        api_logger.error("This is an error message")
        app_logger.critical("This is a critical message")
        
        print("✅ Log levels tested")
        print("\n📁 Checking for log files...")

        logs_dir = Path("logs")
        if logs_dir.exists():
            print(f"✅ Logs directory created: {logs_dir.absolute()}")
            
            log_files = list(logs_dir.glob("*.log"))
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"✅ {log_file.name} created ({size} bytes)")
        else:
            print("⚠️ Logs directory not found")
        
        print("\n🎉 Logging test completed successfully!")
        print("Check the 'logs/' directory for log files")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()