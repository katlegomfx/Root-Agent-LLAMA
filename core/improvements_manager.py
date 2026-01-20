#!/usr/bin/env python3
"""
Improvements Manager - RLM Style
Combines task tracking (JSON) with codebase scanning capabilities (REPL/Exec).
"""

import argparse
import json
import os
import sys
import uuid
import re
import pickle
import glob
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
import io
import traceback

# Constants
IMPROVEMENTS_FILE = 'improvements.json'
STATE_FILE = Path(".flexi/improvements_state.pkl")

# --- DATA MANAGEMENT ---

def load_data(json_path):
    if not os.path.exists(json_path):
        return {"meta": {"version": "2.0", "generated_at": datetime.now().isoformat()}, "items": []}
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file at {json_path}.")
        return {"items": []}

    if "items" not in data:
        data["items"] = []
    
    return data

def save_data(data, json_path):
    data["meta"]["last_updated"] = datetime.now().isoformat()
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def create_item_dict(title, status="suggestion", source="manual"):
    return {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "status": status,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "source": source
    }

# --- STATE MANAGEMENT ---

def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        with STATE_FILE.open("rb") as f:
            return pickle.load(f)
    except Exception:
        return {}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("wb") as f:
        pickle.dump(state, f)

# --- EXEC HELPERS ---

class CodebaseUtils:
    def __init__(self, root_path):
        self.root = Path(root_path)

    def walk(self, pattern="**/*"):
        """List files matching a glob pattern."""
        return [str(p) for p in self.root.glob(pattern) if p.is_file()]

    def grep(self, regex, file_pattern="**/*.py"):
        """Search for a regex in files."""
        results = []
        pattern = re.compile(regex)
        for filepath in self.root.glob(file_pattern):
            if not filepath.is_file(): continue
            try:
                content = filepath.read_text(encoding='utf-8', errors='ignore')
                for i, line in enumerate(content.splitlines()):
                    if pattern.search(line):
                        results.append({
                            "file": str(filepath),
                            "line": i + 1,
                            "content": line.strip()
                        })
            except Exception:
                pass
        return results

    def read(self, filepath):
        """Read a file."""
        return (self.root / filepath).read_text(encoding='utf-8', errors='ignore')

    def run(self, command):
        """Run a shell command and return result object."""
        print(f"[$] {command}")
        return subprocess.run(command, shell=True, capture_output=True, text=True, cwd=self.root)

    def replace(self, filepath, pattern, replacement):
        """Regex replace directly in file. Returns True if changed."""
        path = self.root / filepath
        if not path.exists():
            print(f"Error: {filepath} not found.")
            return False
            
        try:
            content = path.read_text(encoding='utf-8')
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            if new_content != content:
                path.write_text(new_content, encoding='utf-8')
                print(f"Modified {filepath}")
                return True
            else:
                print(f"No match for pattern in {filepath}")
                return False
        except Exception as e:
            print(f"Error modifying {filepath}: {e}")
            return False

    def backup(self, filepath):
        """Create a .bak copy of a file."""
        src = self.root / filepath
        dst = src.with_suffix(src.suffix + ".bak")
        if src.exists():
            shutil.copy2(src, dst)
            print(f"Backed up {filepath}")

    def restore(self, filepath):
        """Restore file from .bak."""
        src = self.root / filepath
        bak = src.with_suffix(src.suffix + ".bak")
        if bak.exists():
            shutil.move(bak, src)
            print(f"Restored {filepath}")
        else:
            print(f"No backup found for {filepath}")

# --- COMMANDS ---

def cmd_init(args):
    root = Path(args.path).resolve()
    json_path = root / IMPROVEMENTS_FILE
    
    state = {
        "root": str(root),
        "json_path": str(json_path),
        "globals": {} # For persistent REPL vars
    }
    save_state(state)
    print(f"Initialized Improvements Manager.")
    print(f"Codebase Root: {root}")
    print(f"Data File: {json_path}")
    
    if not json_path.exists():
        save_data(load_data(json_path), json_path)
        print("Created empty improvements.json")

def cmd_list(args):
    state = load_state()
    if not state:
        print("Not initialized. Run 'init <path>' first.")
        return

    data = load_data(state["json_path"])
    items = data["items"]
    
    if args.status:
        items = [i for i in items if i["status"] == args.status]    
    if args.search:
        query = args.search.lower()
        items = [i for i in items if query in i["title"].lower()]

    print(f"{'ID':<10} {'STATUS':<12} {'TITLE'}")
    print("-" * 60)
    for item in items:
        status_icon = "⚪"
        if item["status"] == "completed": status_icon = "✅"
        elif item["status"] == "in_progress": status_icon = "🚧"
        elif item["status"] == "suggestion": status_icon = "💡"
        
        print(f"{item['id']:<10} {status_icon} {item['status']:<10} {item['title'][:60]}")

def cmd_add(args):
    state = load_state()
    if not state: return
    data = load_data(state["json_path"])
    item = create_item_dict(args.title, args.status, "manual")
    data["items"].append(item)
    save_data(data, state["json_path"])
    print(f"Added item: {item['id']}")

def cmd_next(args):
    state = load_state()
    if not state: return
    data = load_data(state["json_path"])
    
    # 1. Check if we are already working on something
    in_progress = [i for i in data["items"] if i["status"] == "in_progress"]
    if in_progress:
        print(f"Already working on: {in_progress[0]['title']} ({in_progress[0]['id']})")
        print("Finish this first with: python improvements_manager.py resolve <id>")
        return

    # 2. Find next suggestion
    suggestions = [i for i in data["items"] if i["status"] == "suggestion"]
    if not suggestions:
        print("No suggestions pending. Good job!")
        return
        
    next_item = suggestions[0]
    next_item["status"] = "in_progress"
    next_item["updated_at"] = datetime.now().isoformat()
    
    save_data(data, state["json_path"])
    print(f"Picked up: {next_item['title']} ({next_item['id']})")

def cmd_resolve(args):
    state = load_state()
    if not state: return
    data = load_data(state["json_path"])
    
    target_id = args.id
    # If no ID and one item is in progress, resolve that one
    if not target_id:
        in_progress = [i for i in data["items"] if i["status"] == "in_progress"]
        if len(in_progress) == 1:
            target_id = in_progress[0]["id"]
            
    if not target_id:
        print("Please specify ID or have exactly one item in progress.")
        return

    for item in data["items"]:
        if item["id"] == target_id:
            item["status"] = args.status
            item["updated_at"] = datetime.now().isoformat()
            save_data(data, state["json_path"])
            print(f"Item {target_id} marked as {args.status}")
            return
            
    print(f"Item {target_id} not found.")

def cmd_scan(args):
    state = load_state()
    if not state: return
    data = load_data(state["json_path"])
    codebase = CodebaseUtils(state["root"])
    
    added_count = 0
    
    # Built-in scanners
    print("Scanning for TODOs...")
    # Exclude scripts directory and common hidden/build dirs
    todos = [
        t for t in codebase.grep(r"TODO[:\s]?.+") 
        if "scripts" not in t['file'] and ".git" not in t['file']
    ]
    
    for hit in todos:
        # Avoid dupes roughly
        title = f"TODO: {hit['content'].strip()}"
        if not any(i['title'] == title for i in data['items']):
            data["items"].append(create_item_dict(title, "suggestion", "scan"))
            added_count += 1
            
    save_data(data, state["json_path"])
    print(f"Scan complete. Added {added_count} new items.")

def cmd_prune(args):
    state = load_state()
    if not state: return
    data = load_data(state["json_path"])
    codebase = CodebaseUtils(state["root"])
    
    print("Pruning stale scan results...")
    
    # Only prune items that were automatically scanned
    scan_items = [i for i in data["items"] if i.get("source") == "scan" and i["status"] == "suggestion"]
    removed_count = 0
    
    for item in scan_items:
        # Extract content from title "TODO: <content>"
        if item["title"].startswith("TODO: "):
            content_to_find = item["title"][6:].strip() # len("TODO: ") == 6
            
            # Simple check: does this string exist anywhere?
            # We escape regex special chars to treat it as literal
            escaped_content = re.escape(content_to_find)
            hits = codebase.grep(escaped_content)
            
            # If nothing found, or only found in scripts (if we want to be strict), remove it
            # But codebase.grep doesn't filter scripts by default, so we filter results
            valid_hits = [h for h in hits if "scripts" not in h['file']]
            
            if not valid_hits:
                print(f"Removing stale: {item['title'][:50]}...")
                data["items"].remove(item)
                removed_count += 1

    if removed_count > 0:
        save_data(data, state["json_path"])
    print(f"Pruned {removed_count} stale items.")

def cmd_exec(args):
    state = load_state()
    if not state:
        print("Not initialized. Run 'init <path>' first.")
        return

    data = load_data(state["json_path"])
    root = state["root"]
    
    # helper for adding items within script
    def add_item(title, status="suggestion", source="script"):
        # Check for duplicates
        if any(i['title'] == title for i in data['items']):
            return None
        item = create_item_dict(title, status, source)
        data["items"].append(item)
        print(f"[Script] Added: {title}")
        return item

    # Build environment
    codebase = CodebaseUtils(root)
    env = state.get("globals", {})
    env.update({
        "items": data["items"], 
        "data": data,
        "codebase": codebase,
        "grep": codebase.grep,
        "add_item": add_item,
        "print": print
    })
    
    # Read code
    code = args.code
    if code is None:
        code = sys.stdin.read()

    # Capture output
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    
    try:
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            exec(code, env, env)
    except Exception:
        traceback.print_exc(file=stderr_buf)
    
    # Save changes to JSON
    save_data(data, state["json_path"])
    
    # Persist globals (exclude system stuff)
    to_persist = {k: v for k, v in env.items() 
                  if k not in ["items", "data", "codebase", "grep", "add_item", "print", "__builtins__"]}
    
    # Simple picklability check could go here
    state["globals"] = to_persist
    save_state(state)

    print(stdout_buf.getvalue(), end='')
    sys.stderr.write(stderr_buf.getvalue())

def main():
    parser = argparse.ArgumentParser(description="Improvements Manager (RLM-style)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # INIT
    init_parser = subparsers.add_parser("init", help="Initialize for a codebase")
    init_parser.add_argument("path", help="Path to codebase root")

    # LIST
    list_parser = subparsers.add_parser("list", help="List improvements")
    list_parser.add_argument("--status", choices=["suggestion", "in_progress", "completed"])
    list_parser.add_argument("--search", "-q")

    # ADD
    add_parser = subparsers.add_parser("add", help="Add improvement manually")
    add_parser.add_argument("title")
    add_parser.add_argument("--status", default="suggestion")

    # NEXT
    subparsers.add_parser("next", help="Pick next suggestion to work on")

    # RESOLVE
    resolve_parser = subparsers.add_parser("resolve", help="Resolve an item (completed/suggestion)")
    resolve_parser.add_argument("id", nargs="?", help="ID of item (optional if only 1 in progress)")
    resolve_parser.add_argument("--status", choices=["completed", "suggestion", "rejected"], default="completed")

    # SCAN
    subparsers.add_parser("scan", help="Scan codebase for new improvements (TODOs etc)")

    # PRUNE
    subparsers.add_parser("prune", help="Remove scanned items that no longer exist")

    # EXEC
    exec_parser = subparsers.add_parser("exec", help="Run python script against codebase and improvements")
    exec_parser.add_argument("-c", "--code", help="Inline code code")

    args = parser.parse_args()

    if args.command == "init": cmd_init(args)
    elif args.command == "list": cmd_list(args)
    elif args.command == "add": cmd_add(args)
    elif args.command == "next": cmd_next(args)
    elif args.command == "resolve": cmd_resolve(args)
    elif args.command == "scan": cmd_scan(args)
    elif args.command == "prune": cmd_prune(args)
    elif args.command == "exec": cmd_exec(args)

if __name__ == "__main__":
    main()
