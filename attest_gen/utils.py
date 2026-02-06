import os
import shutil

def wipe_folder(folder_path):
    """
    Removes all files and subdirectories from the specified folder.

    Args:
        folder_path (str): The path to the folder to be wiped.
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found.")
        return

    # Iterate over all items in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            # Check if it's a file or directory/symlink and remove accordingly
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) # Removes a file
            elif os.path.isdir(file_path):
                # Removes a directory and all its contents recursively
                shutil.rmtree(file_path) 
        except OSError as e:
            print(f"Error removing {file_path}: {e}")


