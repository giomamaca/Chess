import os
import sys

# Make `app` and `db` importable when pytest is run from anywhere.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
