"""
run.py — Start the log watcher.
Usage: python run.py "C:/path/to/eqlog.txt"
"""
import sys
from parser import watch_log

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py <path_to_eq_log>")
        sys.exit(1)
    watch_log(sys.argv[1], verbose=True)
