"""FS5 Adapters Module.

Contains event source adapters for reading from JSONL files
and other data sources.

Version: v0.10.0
Created: 2026-02-03
"""

from fs5.adapters.fs1_adapter import transform_fs1_event
from fs5.adapters.fs1_adapter import batch_transform as fs1_batch_transform

from fs5.adapters.fs3_adapter import transform_fs3_event
from fs5.adapters.fs3_adapter import batch_transform as fs3_batch_transform
from fs5.adapters.fs3_adapter import parse_qa_report

__all__ = [
    # FS1 (Memory) Adapter
    "transform_fs1_event",
    "fs1_batch_transform",
    # FS3 (QA) Adapter
    "transform_fs3_event",
    "fs3_batch_transform",
    "parse_qa_report",
]
