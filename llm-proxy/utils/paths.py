from pathlib import Path
_current_file = Path(__file__).resolve()
_current_dir = _current_file.parent

# how to use? -> import CONSTANT Value
PROJECT_ROOT = _current_dir.parent
TMP_DIR = PROJECT_ROOT / "tmp"
