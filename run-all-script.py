import sys
import os
import subprocess
import time

def run_script(script_name):
    print(f"\nRunning {script_name}...")
    try:
        if getattr(sys, 'frozen', False):
            # If we're running as an executable
            script_path = os.path.join(os.path.dirname(sys.executable), script_name)
        else:
            # If we're running as a script
            script_path = script_name
            
        subprocess.run([sys.executable, script_path], check=True)
        print(f"✅ {script_name} completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
    except Exception as e:
        print(f"❌ Unexpected error running {script_name}: {e}")

def main():
    print("Starting Banking Statistics Download...")
    print("=======================================")
    
    scripts = [
        "ABS_downloader.py",
        "APRA_downloader.py",
        "NSW_Revenue_downloader.py",
        "RBA_downloader.py"
    ]
    
    for script in scripts:
        run_script(script)
    
    print("\n=======================================")
    print("All downloads completed!")
    time.sleep(2)

if __name__ == "__main__":
    main()
