# Bot\build\code\cli\ai_requests.py
import os
import json

from Bot.build.code.llm.prompts import load_message_template, process_user_messages_with_model, code_corpus, add_context_to_messages, read_file_content, get_message_context_summary
from Bot.build.code.tasks.improver import analyze, improve, refine

class AIRequests:

    
    # async def do_summarize(self, arg):    
    #     """Summarize the chat or code context."""    
    #     if not self.messages_context:    
    #         print("No context to summarize.")    
    #         return    
    #     summary_result = await get_message_context_summary(self.messages_context)    
    #     print("Summary:", summary_result)
    
    #     return summary_result

    async def do_auto_improve(self, arg):
        """
        Automatically improves the initial state by creating a plan, executing steps,        
        and checking for completion.

        Args:
            initial_state (dict): The initial state to be improved.

        Returns:
            dict: The final improved state.
        """
        # Load self_improvement_state.json if it exists        
        path = 'self_improvement_state.json'
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
            # Possibly feed that into a prompt            
            prompt = f"Given the self-improvement plan: {data}..."
            # Initialize an empty dictionary to store improvements            
            improvements = data
        else:
            prompt = "No existing plan. Start from scratch..."
            improvements = {}

        # Define the possible steps to be taken in each iteration        
        steps = [
            {
                "step": "Analyze",
                "action": analyze,
                "params": {"state": self.initial_state}
            },
            {
                "step": "Improve",
                "action": improve,
                "params": {"state": self.initial_state}
            },
            {
                "step": "Refine",
                "action": refine,
                "params": {"state": self.initial_state}
            }
        ]

        # Initialize the current state        
        current_state = self.initial_state

        # Loop until all steps are completed      
        while len(steps) > 0:
            # Select the next step to be executed            
            next_step = steps.pop(0)

            # Check if the step is already in progress            
            if "in_progress" in current_state and current_state["in_progress"] == next_step["step"]:
                print(f"""Skipping {next_step['step']
                                  }, it's already in progress.""")
                continue

            messages = load_message_template(sys_type='base')
            messages.append({'role': 'user', 'content': prompt})
            # Execute the selected step            
            result = await process_user_messages_with_model(messages, tool_use=True, execute=True)

            # Check for completion            
            if "completed" in current_state:
                if not current_state["completed"] and next_step["action"] == refine:
                    print(
                        f"{next_step['step']} was not completed, skipping to the next iteration.")
                    continue

            # Update the current state with the result of the step execution            
            improvements[next_step["step"]] = {"result": result}

            # Update the in_progress flag if the step is completed            
            if "completed" not in current_state and result:
                current_state["in_progress"] = next_step["step"]
                print(f"{next_step['step']} was completed.")

        return improvements
