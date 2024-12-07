# Root-Agent-LLAMA

Root Agent is an algorithm that is light weight and aims to become the underpinnings of a conversational AI agent

## Features
- **Conversational Interface:** Interact with the AI agent via a simple CLI interface.
- **Tool Integration:** Trigger external tools, like running bash commands, through structured JSON instructions.
- **Self Improvement & Correction:** Provide prompts to review code and suggest fixes or enhancements.
- **Code Extraction & Logging:** Automatically extract and store generated code snippets, and record conversation outputs.

## Prerequisites
- **Operating System:** Tested on Windows (adaptable to macOS or Linux with minor changes)
- **Python:** 3.9+ recommended
- **Ollama:** Install Ollama before running the project.
- **Virtual Environment:** Recommended for isolated dependency management.

## Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/katlegomfx/Root-Agent-LLAMA.git
cd Root-Agent-LLAMA
```

2. Install Ollama
Download and install Ollama from [Ollama](https://ollama.com/)

3. Install Python
Download and install Python from [Python](https://www.python.org/downloads/)

4. Install Create a virtual environment
```bash
$ python -m venv venv
```

5. Activate the virtual environment
```bash
source venv/Scripts/activate
```

6. Install dependencies
```bash
$ pip install -r  requirements.txt
```

7. Create .env file and modify
```bash
$ cp .env.example .env
```
change the 'anonymised' value in the .env file

8. Run the code using

## Running the code
```bash
$ python main.py
```

## Usage Examples
> Hello, AI!
Hello! How can I assist you today?

> self Improve the code by adding more comments
Here’s how we can enhance the code...

> fix Add better exception handling
To handle exceptions more gracefully, we could...
