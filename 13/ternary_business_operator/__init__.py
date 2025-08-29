# company_operator/__init__.py
"""
company_operator: ternary operator middleware for 13-stage decision rails.

exports:
- TernaryEngine: core middleware
- jsonl_sink: simple JSONL log sink
- __version__: package version if installed as a distribution
"""

from importlib import metadata

try:
    __version__ = metadata.version("company_operator")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from .middleware import TernaryEngine, jsonl_sink

__all__ = ["TernaryEngine", "jsonl_sink", "__version__"]
