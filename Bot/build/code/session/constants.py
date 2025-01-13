import configparser
import os
from dotenv import load_dotenv
load_dotenv()

triple_backticks = '`'*3
md_heading = "#"

assistant_prefix = 'assistant_response'
summary_prefix = 'assistant_summary'
code_prefix = 'assistant_code' 

gen_ai_path = 'gen_ai'

ai_code_path = 'gen_ai_code'
ai_errors_path = 'gen_ai_errors'
ai_results_path = 'gen_ai_results'
ai_summaries_path = 'gen_ai_summaries'
ai_history_path = 'gen_ai_history'

binary_answer = "Possible responses: yes or no"

anonymised = os.getenv('anonymised') if os.getenv('anonymised') else ''

error_file = 'currentError.txt'

config = configparser.ConfigParser()
config.read("config.ini")

