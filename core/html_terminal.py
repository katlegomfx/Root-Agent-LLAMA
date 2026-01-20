import sys
import subprocess
import os
import datetime
import html

class HtmlLogger:
    def __init__(self, filename="terminal_log.html"):
        self.filename = filename
        self._init_file()

    def _init_file(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', 'Courier New', monospace; padding: 20px; }
        .prompt { color: #4ec9b0; font-weight: bold; }
        .command { color: #ce9178; }
        .output { color: #cccccc; white-space: pre-wrap; }
        .error { color: #f48771; }
        .timestamp { color: #858585; font-size: 0.8em; margin-right: 10px; }
        div { margin-bottom: 5px; }
    </style>
</head>
<body>
    <h3>Terminal Session Recorded</h3>
""")

    def log_input(self, cmd):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"""
        <div>
            <span class="timestamp">[{ts}]</span>
            <span class="prompt">HTML-TERM&gt;</span>
            <span class="command">{html.escape(cmd)}</span>
        </div>
        """
        self._append(entry)

    def log_output(self, output, is_error=False):
        cls = "error" if is_error else "output"
        entry = f"""
        <div class="{cls}">{html.escape(output)}</div>
        """
        self._append(entry)

    def _append(self, content):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(content)

def main():
    logger = HtmlLogger()
    print("HTML Terminal Shell v1.0")
    print("Type 'exit' to quit.")
    print("Commands are executed in system shell.")
    
    while True:
        try:
            # Force flush to ensure parent process sees prompt
            sys.stdout.write("\nHTML-TERM> ")
            sys.stdout.flush()
            
            cmd = sys.stdin.readline()
            if not cmd:
                break
                
            cmd = cmd.strip()
            if not cmd:
                continue
                
            logger.log_input(cmd)
            
            if cmd.lower() in ["exit", "quit"]:
                break
            
            # Execute command
            try:
                # Use shell=True to allow complex commands (dir, echo, etc)
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                
                output = result.stdout
                if result.stderr:
                    output += "\n[STDERR]\n" + result.stderr
                    
                print(output)
                logger.log_output(output, is_error=(result.returncode != 0))
                
            except Exception as e:
                err_msg = f"Error executing command: {e}"
                print(err_msg)
                logger.log_output(err_msg, is_error=True)
                
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            break

    # Close HTML tag
    with open(logger.filename, "a", encoding="utf-8") as f:
        f.write("</body></html>")

if __name__ == "__main__":
    main()
