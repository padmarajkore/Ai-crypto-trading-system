import os
import subprocess
import time
import glob

PROJECT_DIR = "/Users/padamarajkore/Documents/ADK-crash-course/ai-crypto-trading-system"
STRATEGIES_DIR = f"{PROJECT_DIR}/freqtrade/user_data/strategies"
CURRENT_STRATEGY_FILE = f"{PROJECT_DIR}/current_strategy.txt" 

def get_active_strategy_name():
    """Reads the name of the currently active strategy."""
    if os.path.exists(CURRENT_STRATEGY_FILE):
        with open(CURRENT_STRATEGY_FILE, 'r') as f:
            return f.read().strip()
    return "SampleStrategy"

def set_active_strategy_name(name):
    """Saves the name of the active strategy."""
    with open(CURRENT_STRATEGY_FILE, 'w') as f:
        f.write(name)

def list_strategies():
    """Lists all available strategy files."""
    files = glob.glob(f"{STRATEGIES_DIR}/*.py")
    strategies = [os.path.basename(f).replace('.py', '') for f in files if not f.endswith('__init__.py')]
    return strategies

def read_strategy_code(strategy_name=None):
    """Reads the content of a specific strategy file. Defaults to active strategy."""
    if not strategy_name:
        strategy_name = get_active_strategy_name()
    
    path = f"{STRATEGIES_DIR}/{strategy_name}.py"
    if not os.path.exists(path):
        return f"Error: Strategy {strategy_name} not found."
        
    with open(path, 'r') as f:
        return f.read()

def restart_freqtrade(strategy_name=None):
    """
    Restarts Freqtrade with the specified strategy.
    Returns status message.
    """
    if not strategy_name:
        strategy_name = get_active_strategy_name()

    try:
        # Kill existing Freqtrade process
        subprocess.run(
            ["pkill", "-9", "-f", "freqtrade trade"],
            cwd=PROJECT_DIR,
            capture_output=True
        )
        time.sleep(2)  # Wait for process to fully stop
        
        # Start Freqtrade again with the NEW strategy
        log_file = open(f"{PROJECT_DIR}/freqtrade/freqtrade.log", "a")
        
        cmd = ["freqtrade", "trade", "--dry-run", "-c", "adk_config.json", "--strategy", strategy_name]
        
        subprocess.Popen(
            cmd,
            cwd=f"{PROJECT_DIR}/freqtrade",
            stdout=log_file,
            stderr=log_file,
            start_new_session=True
        )
        time.sleep(3)  # Wait for startup
        
        set_active_strategy_name(strategy_name)
        return f"✅ Freqtrade restarted successfully. Active Strategy: {strategy_name}"
    except Exception as e:
        return f"⚠️ Could not restart Freqtrade: {e}"

def create_and_switch_strategy(class_name: str, code: str):
    """
    Creates a NEW strategy file and switches Freqtrade to use it.
    Use this to try completely new logic (e.g., 'AggressiveScalping').
    """
    if "class " + class_name not in code:
        return f"Error: Code must contain 'class {class_name}'"
        
    file_path = f"{STRATEGIES_DIR}/{class_name}.py"
    
    # Save the file
    with open(file_path, 'w') as f:
        f.write(code)
        
    # Switch and Restart
    return restart_freqtrade(class_name)

def update_strategy_code(new_code: str):
    """
    Overwrites the CURRENT active strategy file with new code and restarts.
    """
    current_name = get_active_strategy_name()
    path = f"{STRATEGIES_DIR}/{current_name}.py"
    
    # Validation
    if f"class {current_name}" not in new_code:
        return f"Error: Code must contain 'class {current_name}' to match file."
    
    # Backup
    with open(path, 'r') as f:
        original = f.read()
    with open(path + ".bak", 'w') as f:
        f.write(original)
        
    # Write
    with open(path, 'w') as f:
        f.write(new_code)
        
    # Restart
    return restart_freqtrade(current_name)
