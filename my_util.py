import sys

def get_file_name(file_path: str):
    if sys.platform.startswith('win'):
        return file_path.split('/')[-1]
    elif sys.platform.startswith('linux'):
        return file_path.split('/')[-1]