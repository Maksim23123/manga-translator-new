import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PYFLOW_ROOT = ROOT / "app" / "third_party" / "PyFlow"

for path in (ROOT, PYFLOW_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
