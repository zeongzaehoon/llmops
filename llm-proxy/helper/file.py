import logging
import tempfile
from pathlib import Path
from contextlib import contextmanager



@contextmanager
def helper_import_files_temp_workspace(dir_path:Path | str, prefix:str=None):
    try:
        dir_path = dir_path if isinstance(dir_path, str) else str(dir_path)
        prefix = prefix or "filesearch_"

        ensure_directory(dir_path)

        with tempfile.TemporaryDirectory(prefix=prefix, dir=dir_path) as tmpdir_path:
            logging.info(f"[helper.file.helper_import_files_temp_workspace] Created temp workspace: {tmpdir_path}")
            yield tmpdir_path
            logging.info(f"[helper.file.helper_import_files_temp_workspace] Cleaned up workspace: {tmpdir_path}")
    except Exception as e:
        logging.error(f"[helper.file.helper_import_files_temp_workspace] Failed to make temp dir space | ERROR: {e}")

def ensure_directory(path_str: str):
    path = Path(path_str)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def helper_import_files_make_temp_file_path(key: str, tmpdir_path: str | Path):
    """return (file_name, temp_file_path)"""
    file_name = Path(key).name
    tmpdir_path = tmpdir_path if isinstance(tmpdir_path, Path) else Path(tmpdir_path)
    return file_name, tmpdir_path / file_name
