import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def write_to_log(message: str):
    """Write a message to the logs.txt file in the workbench directory.
    
    Args:
        message: The message to log
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    workbench_dir = os.path.join(parent_dir, "workbench")
    
    log_path = os.path.join(workbench_dir, "logs.txt")
    os.makedirs(workbench_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

def get_env_var(var_name: str, profile: Optional[str] = None) -> Optional[str]:
    """Get an environment variable from the saved JSON file or from environment variables.
    
    Args:
        var_name: The name of the environment variable to retrieve
        profile: The profile to use (if None, uses the current profile)
        
    Returns:
        The value of the environment variable or None if not found
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    workbench_dir = os.path.join(parent_dir, "workbench")
    
    # Path to the JSON file storing environment variables
    env_file_path = os.path.join(workbench_dir, "env_vars.json")
    
    # First try to get from JSON file
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, "r") as f:
                env_vars = json.load(f)
                
                # If profile is specified, use it; otherwise use current profile
                current_profile = profile or env_vars.get("current_profile", "default")
                
                # Get variables for the profile
                if "profiles" in env_vars and current_profile in env_vars["profiles"]:
                    profile_vars = env_vars["profiles"][current_profile]
                    if var_name in profile_vars and profile_vars[var_name]:
                        return profile_vars[var_name]
                
                # For backward compatibility, check the root level
                if var_name in env_vars and env_vars[var_name]:
                    return env_vars[var_name]
        except (json.JSONDecodeError, IOError) as e:
            write_to_log(f"Error reading env_vars.json: {str(e)}")
    
    # If not found in JSON, try to get from environment variables
    return os.environ.get(var_name) 