import os

def get_asset_path(filename):
    """
    Constructs a path to an asset file relative to the script's location.

    Args:
        filename (str): The name of the asset file (e.g., 'goodboy.png').

    Returns:
        str: The absolute path to the asset file.
    """
    # Get the directory of the currently executing script.
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the assets directory, which is a sibling of the script's directory.
    assets_dir = os.path.join(script_dir, 'assets')

    # Construct the full path to the file.
    file_path = os.path.join(assets_dir, filename)

    return file_path