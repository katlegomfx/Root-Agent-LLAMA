import sys
from pathlib import Path


def get_ts_files_content(directory):
    """
    Recursively searches for all .ts and .tsx files in the specified directory and its subdirectories,
    excluding those in any 'node_modules' directory. Only files that are located in a folder named 'src'
    are processed, unless the root directory itself is 'src'.

    Returns a dictionary mapping each file's path to its content.
    """
    ts_files_content = {}
    root = Path(directory).resolve()
    is_root_src = (root.name == "src")

    # Iterate over all files recursively
    for file in root.rglob("*"):
        if file.suffix not in (".ts", ".tsx", ".js", ".jsx"):
            continue
        if "node_modules" in file.parts:
            continue

        # If the root isn't named 'src', only process files that lie in a 'src' folder
        if not is_root_src:
            try:
                relative_parts = file.relative_to(root).parts
            except ValueError:
                continue
            if "src" not in relative_parts:
                continue

        try:
            content = file.read_text(encoding="utf-8")
            new_file = file.as_posix().replace(
                'C:/Users/katle/Desktop/theFlex/lastLast/app/base/', '')
            ts_files_content[str(new_file)] = content
        except Exception as e:
            print(f"Error reading {new_file}: {e}")

    return ts_files_content


def convert_to_md(ts_files):
    """
    Converts the dictionary of TypeScript files to a Markdown-formatted string.
    Each file's content is enclosed in triple backticks with language identifier.
    """
    md_content = ""
    for filepath, content in ts_files.items():
        md_content += f"### {filepath}\n\n```ts\n{content}\n```\n\n"
    return md_content


def write_to_md(content, output_file):
    """
    Writes the Markdown-formatted content to the specified output file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")


def main():
    tips = """
### Tips to keep user happy:
- Implement improvements where fit
- Stick to DRY principles
- Provide full pieces of code based on the files that need to be changed
"""

    output_file = "output.md"

    directory1 = "./app/base"
    ts_files_1 = convert_to_md(get_ts_files_content(directory1))

    directory2 = "./app/appgen"
    ts_files_2 = convert_to_md(get_ts_files_content(directory2))

    final_text = f"""
## the following is the working example:
{ts_files_1}

## work on the following:
{ts_files_2}

## question
why might the generated html not be being sent to the Studio Preview?
- modify code so that it will retry max 3 times if no html tag found

{tips}
"""
    write_to_md(final_text, output_file)
    print(f"Output written to {output_file}")


if __name__ == '__main__':
    main()
