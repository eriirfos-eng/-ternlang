# ternlang_memory_manager.py
# Provides functions for persistent memory management for Ternlang agents.
# This script handles saving agent memory to and loading from a JSON file.

import json
import os

# Define the default path for the persistent memory file
# This can be overridden by individual agent examples if needed
DEFAULT_MEMORY_FILE_PATH = "agent_memory.json" 

def save_agent_memory(agent_instance, file_path=DEFAULT_MEMORY_FILE_PATH):
    """
    Saves the agent's current in-memory log to a JSON file.
    
    Args:
        agent_instance: The TernAgent instance whose memory is to be saved.
        file_path (str): The path to the JSON file where memory will be stored.
    """
    try:
        # Ensure the directory exists if file_path includes a directory
        os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(agent_instance.memory, f, indent=4)
        print(f"\n--- Memory saved to {file_path} ---")
    except Exception as e:
        print(f"Error saving memory: {e}")

def load_agent_memory(agent_instance, file_path=DEFAULT_MEMORY_FILE_PATH):
    """
    Loads memory from a JSON file into the agent instance's memory attribute.
    
    Args:
        agent_instance: The TernAgent instance whose memory is to be loaded.
        file_path (str): The path to the JSON file from which memory will be loaded.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                agent_instance.memory = json.load(f)
            print(f"--- Memory loaded from {file_path}. {len(agent_instance.memory)} entries found. ---")
        except json.JSONDecodeError:
            print(f"Memory file {file_path} is corrupted or empty. Starting with fresh memory.")
            agent_instance.memory = []
        except Exception as e:
            print(f"Error loading memory: {e}")
    else:
        print(f"No existing memory file found at {file_path}. Starting with fresh memory.")
        agent_instance.memory = []

if __name__ == "__main__":
    # This block allows you to test the memory manager independently if needed.
    # It won't run when imported by other scripts.
    print("This script provides memory management functions for Ternlang agents.")
    print("It is typically imported by agent simulation scripts.")
    # Example usage (uncomment to test):
    # from ternlang_prototype import TernAgent # Assuming ternlang_prototype is accessible
    # class MyTestAgent(TernAgent):
    #     def __init__(self, name="TestAgent"):
    #         super().__init__(name)
    #         self.memory = [] # Initialize empty memory for testing
    # test_agent = MyTestAgent()
    # load_agent_memory(test_agent)
    # test_agent.memory.append({"test_entry": "This is a test."})
    # save_agent_memory(test_agent)
