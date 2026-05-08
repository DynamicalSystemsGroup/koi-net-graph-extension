import shutil
from pathlib import Path

BASE = Path(__file__).parent
TARGETS = ["coordinator", "test_node"]

for target in TARGETS:
    rid_cache = BASE / target / ".rid_cache"
    log_file = BASE / target / "log.ndjson"

    if rid_cache.exists():
        shutil.rmtree(rid_cache)
        print(f"Removed {rid_cache}")

    if log_file.exists():
        log_file.unlink()
        print(f"Removed {log_file}")
