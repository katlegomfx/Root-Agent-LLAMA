### building\code\constants\script.pyimport os

BASE_DIR = os.path.abspath("./projects")
ALLOWED_COMMANDS = {'ls', 'echo', 'grep', 'py', 'npm', 'pip'}

model_map = {
    ### 'llama3': ('bartowski/Llama-3-ChatQA-1.5-8B-GGUF', 'ChatQA-1.5-8B-Q4_K_M.gguf'),    ### 'llama3': ('QuantFactory/Meta-Llama-3-8B-GGUF', 'Meta-Llama-3-8B.Q4_K_M.gguf'),    ### 'llama3Instruct': ('QuantFactory/Meta-Llama-3-8B-Instruct-GGUF', 'Meta-Llama-3-8B-Instruct.Q6_K.gguf'),
    'deepseek': ('icycodes/deepseek-coder-6.7b-base-Q8_0-GGUF', 'deepseek-coder-6.7b-base-q8_0.gguf'),
    'deepseekV2': ('third0x/DeepSeek-V2-Lite-Chat-Q4_K_M-GGUF', 'deepseek-v2-lite-chat-q4_k_m.gguf'),

    'llama3.1': ('lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF', 'Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'),

    'llama3': ('lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF', 'Meta-Llama-3-8B-Instruct-Q4_K_M.gguf'),

    'bigllama3': ('lmstudio-community/Meta-Llama-3-70B-Instruct-GGUF', 'Meta-Llama-3-70B-Instruct-Q4_K_M.gguf'),

    'midllama3': ('lmstudio-community/Meta-Llama-3.1-13B-Instruct-GGUF', 'Meta-Llama-3.1-13B-Instruct-Q4_K_M.gguf'),

    'tiny': ('TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF', 'tinyllama-1.1b-chat-v1.0.Q6_K.gguf'),
    'stable': ("bartowski/stable-code-instruct-3b-GGUF", "stable-code-instruct-3b-Q6_K.gguf"),
    
    'llava': ("mys/ggml_llava-v1.5-13b", "ggml-model-q5_k.gguf"),
    'llavaPrj': ("mys/ggml_llava-v1.5-13b", "mmproj-model-f16.gguf"),

    'big': ("TheBloke/Code-290k-13B-GGUF", "code-290k-13b.Q5_K_M.gguf"),
    
    "uncensored": ("TheBloke/llama2_7b_chat_uncensored-GGUF", "llama2_7b_chat_uncensored.Q4_K_M.gguf"),
    "code": ("TheBloke/CodeLlama-7B-Instruct-GGUF", "codellama-7b-instruct.Q4_K_M.gguf"),
    "base": ("TheBloke/Llama-2-7b-GGUF", "llama-2-7b.Q4_K_M.gguf"),
    "chat": ("TheBloke/Llama-2-7b-Chat-GGUF", "llama-2-7b-chat.Q4_K_M.gguf"),
    "orca": ("TheBloke/Orca-2-7B-GGUF", "orca-2-7b.Q4_K_M.gguf"),
    "mistralorca": ("TheBloke/Mistral-7B-OpenOrca-GGUF", "mistral-7b-openorca.Q4_K_M.gguf"),
    "mistral": ("TheBloke/Mistral-7B-v0.1-GGUF", "mistral-7b-v0.1.Q4_K_M.gguf"),
    "zephyr": ("TheBloke/zephyr-7B-beta-GGUF", "zephyr-7b-beta.Q4_K_M.gguf"),
    "dolphin": ("TheBloke/dolphin-2.2.1-mistral-7B-GGUF", "dolphin-2.2.1-mistral-7b.Q4_K_M.gguf"),
    ### "yarn": ("ThBloke/Yarn-Mistral-7B-128k-GGUF", "yarn-mistral-7b-128k.Q4_K_M.gguf"),    ### "instruct32k": ("TheBloke/Llama-2-7B-32K-Instruct-GGUF", "llama-2-7b-32k-instruct.Q4_K_M.gguf"),    ### 'mixtral': ("TheBloke/Mixtral-8x7B-v0.1-GGUF", "mixtral-8x7b-v0.1.Q4_K_M.gguf"),}

base_web_app_name = "NeuralFront"

APP_NAME = base_web_app_name
MAIL_MAILER = "smtp"
MAIL_HOST = "mail.flexdata.co.za"
MAIL_PORT = 587
MAIL_USERNAME = "support@flexdata.co.za"
MAIL_PASSWORD = ""
MAIL_ENCRYPTION = "null"
MAIL_FROM_ADDRESS = "support@flexdata.co.za"
MAIL_FROM_NAME = "${{APP_NAME}}"

DEV = './results/codebase/'
ADDRESS_ISSUE = 'to address the problem below'

JSON_FUNCTION = "Reply with a list of json format objects that contains a functions along with the parameters from the available for example: "
example_man = {
    'function': 'write_file',
    'args': [],
    'kwargs': {
        'file_path': 'hello.py',
        'content': 'print("Hello, World!")'
    }
}
FUNCTION_EXAMPLE_MAN = f"{JSON_FUNCTION}[{example_man}]"
example_cmd = {
    'function': 'run_command',
    'args': [],
    'kwargs': {
        'command': 'py',
        'user_input': 'test.py'
    }
}
FUNCTION_EXAMPLE_CMD = f"{JSON_FUNCTION}[{example_cmd}]"

APPROVAL = 'approve'
APPROVAL_MESSAGE = f"Reply with: '{APPROVAL}' if the work looks good."
INFO = 'I will need more information'
INFO_REQUEST = f"Reply with: '{INFO}' if you need more information."

### Context Window and Max New Tokens and ProcessorCONTEXT_WINDOW_SIZE = 163840
MAX_NEW_TOKENS = CONTEXT_WINDOW_SIZE  # int(CONTEXT_WINDOW_SIZE/4)
DEVICE_TYPE = 'cpu'
N_GPU_LAYERS = 100  # Llama-2-70B has 83 layers
N_BATCH = 512
EMBEDDING_MODEL_NAME = 'hkunlp/instructor-large'
PERSIST_DIRECTORY = './results/db'
SOURCE_DIRECTORIES = [
    '../next_llm'
    ### '../../../../next_llm/'    ]

### Save models in easy to see locationMODELS_PATH = "./models/llms/"

### DOCUMENT_MAP = {###     ".txt": TextLoader,###     ".md": TextLoader,###     ".pdf": PDFMinerLoader,
###     ".mq5": TextLoader,###     ".mq4": TextLoader,
###     ".py": PythonLoader,###     ".js": TextLoader,###     ".json": TextLoader,###     ".jsx": TextLoader,###     ".ts": TextLoader,###     ".tsx": TextLoader,
###     ".csv": CSVLoader,###     ".xls": UnstructuredExcelLoader,###     ".xlsx": UnstructuredExcelLoader,
###     ".docx": Docx2txtLoader,###     ".doc": Docx2txtLoader,### }
INGEST_THREADS = os.cpu_count() or 8