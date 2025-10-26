import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_ROOT = os.path.join(REPO_ROOT, "src")

for path in (SRC_ROOT, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

