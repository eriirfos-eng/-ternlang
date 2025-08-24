# utils/jsonl_logger.py
import json
import os
from typing import Optional
from uuid import uuid4

class JSONLLogger:
    """
    very small append-only jsonl logger with simple rotation by line count.
    does not do time lookups beyond what the agent includes per entry.
    """

    def __init__(self, log_dir: str, run_id: Optional[str] = None, rotate_every: int = 50000):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.run_id = run_id or uuid4().hex[:12]
        self.rotate_every = rotate_every
        self._line_count = 0
        self._file_index = 0
        self._fh = None
        self._open_new_file()

    @property
    def path(self) -> str:
        return os.path.join(self.log_dir, f"run_{self.run_id}_{self._file_index:03d}.jsonl")

    def _open_new_file(self):
        if self._fh:
            self._fh.close()
        self._fh = open(self.path, "a", encoding="utf-8")
        self._line_count = 0

    def write(self, entry: dict):
        json.dump(entry, self._fh, ensure_ascii=False, separators=(",", ":"))
        self._fh.write("\n")
        self._fh.flush()
        self._line_count += 1
        if self._line_count >= self.rotate_every:
            self._file_index += 1
            self._open_new_file()

    def close(self):
        if self._fh:
            self._fh.close()
            self._fh = None
