Analyze whether the user's goal has been COMPLETED based on the conversation history.

USER'S GOAL:
{user_goal}

STEPS COMPLETED:
{progress_summary}

CONVERSATION HISTORY:
{conversation_history}

Return ONLY valid JSON:
{{
  "completed": true or false,
  "explanation": "Brief explanation. QUOTE the specific log line that proves completion. Do not hallucinate success if the log shows 'Sent: 7' but the required action was Option 1.",
  "next_step": "If not completed, what should be the next step"
}}
