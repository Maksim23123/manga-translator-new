import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
THIRD_PARTY = ROOT / "app" / "third_party"
THIRD_PARTY_PYFLOW = THIRD_PARTY / "PyFlow"

for path in (ROOT, THIRD_PARTY, THIRD_PARTY_PYFLOW):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
