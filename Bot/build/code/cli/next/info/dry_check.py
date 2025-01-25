# Bot\build\code\cli\next\info\dry_check.py
# Bot/build/code/cli/next/info/dry_check.py
import os
import difflib
from typing import List, Tuple

def list_files(directory: str, extension: str = ".py") -> List[str]:
    """
    Recursively list all files in the given directory with the given extension.
    """
    matched_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                matched_files.append(os.path.join(root, file))
    return matched_files

def compare_files(file1: str, file2: str, min_match_lines: int = 3) -> List[Tuple[int, int, int]]:
    """
    Compare two files line by line and return a list of matching blocks.
    
    Each matching block is a tuple: (start_line_file1, start_line_file2, length)
    where line numbers are 0-indexed. Only blocks with length >= min_match_lines
    (and not the dummy last match from get_matching_blocks, which has size 0) are returned.
    """
    with open(file1, 'r', encoding='utf-8') as f:
        lines1 = f.readlines()
    with open(file2, 'r', encoding='utf-8') as f:
        lines2 = f.readlines()

    matcher = difflib.SequenceMatcher(None, lines1, lines2)
    matching_blocks = matcher.get_matching_blocks()
    results = []
    for match in matching_blocks:
        if match.size >= min_match_lines:
            results.append((match.a, match.b, match.size))
    return results

def format_matching_info(file1: str, file2: str, match_info: Tuple[int, int, int],
                         lines1: List[str], lines2: List[str]) -> str:
    """
    Returns a Markdown-formatted string with matching block information.
    """
    start1, start2, size = match_info
    end1 = start1 + size
    end2 = start2 + size
    # Convert 0-indexed to 1-indexed for display.
    md = []
    md.append("---")
    md.append(f"**File 1:** `{file1}`")
    md.append(f"   - Matching lines: **{start1+1}** to **{end1}**")
    md.append(f"**File 2:** `{file2}`")
    md.append(f"   - Matching lines: **{start2+1}** to **{end2}**")
    md.append("**Common block:**")
    md.append("```")
    # The common block (assumed identical in both files) is taken from file1's corresponding lines.
    common_block = "".join(lines1[start1:end1])
    md.append(common_block.rstrip())
    md.append("```")
    md.append("\n")
    return "\n".join(md)

def find_similar_code_in_directory(directory: str, min_match_lines: int = 3,
                                   extension: str = ".py") -> str:
    """
    Recursively goes through each file in the provided directory with the specified extension,
    compares each pair of files, and returns a markdown string that describes where similar code blocks occur.
    
    Parameters:
        directory (str): The root directory to scan.
        min_match_lines (int): The minimum number of consecutive similar lines to report.
        extension (str): The file extension filter (default: '.py')
    
    Returns:
        str: A Markdown-formatted report of similar code blocks.
    """
    output_lines = []
    output_lines.append(f"# Similar Code Report for Directory: {directory}\n")

    files = list_files(directory, extension)
    num_files = len(files)

    if num_files < 2:
        output_lines.append("Not enough files found to compare.\n")
        return "\n".join(output_lines)

    # Compare every pair of files (without duplicates)
    for i in range(num_files):
        for j in range(i + 1, num_files):
            file1 = files[i]
            file2 = files[j]
            matches = compare_files(
                file1, file2, min_match_lines=min_match_lines)
            if matches:
                output_lines.append(
                    f"## Comparing:\n- **File 1:** `{file1}`\n- **File 2:** `{file2}`\n")
                # Read files once to show the matching snippet
                with open(file1, 'r', encoding='utf-8') as f:
                    lines1 = f.readlines()
                with open(file2, 'r', encoding='utf-8') as f:
                    lines2 = f.readlines()
                for match in matches:
                    block_md = format_matching_info(
                        file1, file2, match, lines1, lines2)
                    output_lines.append(block_md)

    return "\n".join(output_lines)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python dry_check.py <directory> [min_match_lines]")
        sys.exit(1)
    directory = sys.argv[1]
    try:
        min_lines = int(sys.argv[2]) if len(sys.argv) >= 3 else 3
    except ValueError:
        print("min_match_lines must be an integer.")
        sys.exit(1)

    report = find_similar_code_in_directory(
        directory, min_match_lines=min_lines)
    output_filepath = "similar_code_report.md"
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report written to {output_filepath}")
