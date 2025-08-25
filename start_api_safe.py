#!/usr/bin/env python3
"""
Safe startup script for Foundation-Sec API with memory monitoring
"""

import psutil
import subprocess
import sys
import time
import os

def check_system_resources():
    """Check if system has enough resources to run the model"""
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    
    print(f"Available memory: {available_gb:.2f} GB")
    print(f"Total memory: {memory.total / (1024**3):.2f} GB")
    print(f"Memory usage: {memory.percent}%")
    
    if available_gb < 6:
        print("WARNING: Less than 6GB available memory. Model may cause system freeze.")
        return False
    
    return True

def monitor_memory_usage(process):
    """Monitor memory usage of the API process"""
    try:
        proc = psutil.Process(process.pid)
        memory_mb = proc.memory_info().rss / (1024**2)
        memory_percent = proc.memory_percent()
        
        print(f"API Process Memory: {memory_mb:.1f} MB ({memory_percent:.1f}%)")
        
        # Kill process if it uses more than 80% of system memory
        if memory_percent > 80:
            print("CRITICAL: Process using too much memory. Terminating...")
            process.terminate()
            return False
            
    except psutil.NoSuchProcess:
        return False
    
    return True

def main():
    print("Foundation-Sec API Safe Startup")
    print("=" * 40)
    
    # Check initial system resources
    if not check_system_resources():
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Startup cancelled.")
            sys.exit(1)
    
    # Change to the correct directory
    os.chdir('/home/sa')
    
    # Activate virtual environment and start API
    cmd = [
        'bash', '-c',
        'source foundation-sec-env/bin/activate && uvicorn foundation_sec_api:app --host 0.0.0.0 --port 8000 --log-level info'
    ]
    
    print("Starting Foundation-Sec API...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    try:
        # Monitor the process
        while process.poll() is None:
            time.sleep(10)  # Check every 10 seconds
            
            # Monitor memory usage
            if not monitor_memory_usage(process):
                break
            
            # Check system memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                print("CRITICAL: System memory usage > 90%. Stopping API...")
                process.terminate()
                break
        
        # Wait for process to finish
        process.wait()
        print(f"API process exited with code: {process.returncode}")
        
    except KeyboardInterrupt:
        print("\nReceived interrupt signal. Stopping API...")
        process.terminate()
        process.wait()
    
    except Exception as e:
        print(f"Error monitoring process: {e}")
        process.terminate()

if __name__ == "__main__":
    main()