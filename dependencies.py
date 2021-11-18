"""
Load dlls and other dependencies at the beginning of module importing
"""
from os import add_dll_directory

__all__ = []

def add_dll_dependencies():
    import platform
    import os.path
    arch = platform.architecture()[0]
    arch_mapping = {
        '32bit': 'x86',
        '64bit': 'x64'
    }
    dlls_folder = arch_mapping[arch]
    dlls_dir = os.path.join(os.path.dirname(__file__), 'DLLs', dlls_folder)
    add_dll_directory(dlls_dir)

# ==========
add_dll_dependencies()