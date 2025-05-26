#!/usr/bin/env python3
"""
Cross-platform line count checker for .mdc files.
Ensures .mdc files don't exceed 150 lines.
"""
import sys
from pathlib import Path


def check_file(file_path: Path) -> bool:
    """Check if a file exceeds 150 lines. Returns True if valid, False if invalid."""
    if not file_path.exists():
        print(f"ERROR: File {file_path} does not exist.")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = sum(1 for _ in f)
    except Exception as e:
        print(f"ERROR: Error reading {file_path}: {e}")
        return False
    
    if lines > 150:
        print(f"ERROR: {file_path} exceeds 150 lines ({lines} lines).")
        return False
    
    print(f"OK: {file_path} is within limit ({lines} lines).")
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python lint_mdc.py <file1> [file2] ...")
        sys.exit(1)
    
    all_valid = True
    
    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)
        if not check_file(file_path):
            all_valid = False
    
    if not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main() 