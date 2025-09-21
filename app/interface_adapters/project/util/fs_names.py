# interface_adapters/util/fs_names.py
import os, re, unicodedata

_WINDOWS_RESERVED = {"con","prn","aux","nul",*(f"com{i}" for i in range(1,10)),*(f"lpt{i}" for i in range(1,10))}
_ILLEGAL_CHARS = r'<>:"/\\|?*\x00-\x1F'

def safe_folder_name(name: str, *, ascii_only: bool = False, max_len: int = 100) -> str:
    if not name: return "untitled"
    name = unicodedata.normalize("NFKC", name)
    if ascii_only: name = name.encode("ascii","ignore").decode("ascii")
    for sep in {"/","\\", os.sep, *(x for x in [os.altsep] if x)}:
        name = name.replace(sep, "-")
    name = re.sub(f"[{_ILLEGAL_CHARS}]", "", name)
    name = re.sub(r"\s+", " ", name).strip().rstrip(" .")
    if not name: name = "untitled"
    if name.casefold() in _WINDOWS_RESERVED: name += "_"
    if len(name) > max_len: name = name[:max_len].rstrip(" .")
    return name