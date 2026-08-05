import os
import sys

# Add src to Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from batip.dashboard.home import run_dashboard

if __name__ == "__main__":
    run_dashboard()