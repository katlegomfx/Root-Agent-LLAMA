
def get_directory_tree(path: str) -> str:
    """
    Generate a string representation of the directory tree starting from the given path,
    while ignoring files and directories matching the specified patterns.

    Args:
        path: The path to the directory to start from.

    Returns:
        A string representation of the directory tree.
    """
    import os
    import fnmatch

    tree = ""

    ignore_patterns = ['interest', 'pyds', 'backup', 'models', 'sdlc',
                    'self_autoCode', 'self_autoCodebase', 'tests', 'to_confirm_tools', 'node_modules', 'gen_ai', 'idea', 'imagev1', 'pretrained', 'prompts', '.next', '__pycache__']

    def is_ignored(path):
        if ignore_patterns:
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(os.path.basename(path), pattern):
                    return True
        return False

    for root, directories, files in os.walk(path):
        # Filter out ignored directories
        directories[:] = [d for d in directories if not is_ignored(os.path.join(root, d))]
        
        # Filter out ignored files
        files = [f for f in files if not is_ignored(os.path.join(
            root, f)) and f.split('.')[-1] in ['py', 'ts', 'js', 'tsx', 'jsx', 'md']]

        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree += '{}{}/\n'.format(indent, os.path.basename(root))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree += '{}{}\n'.format(subindent, f)
    return tree
