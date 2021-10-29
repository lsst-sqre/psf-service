"""The job_result database table."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.types import JSON

from .base import Base

if TYPE_CHECKING:
    from typing import Mapping, Optional

__all__ = ["JobResult"]


class JobResult(Base):
    __tablename__ = "job_result"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    job_id: int = Column(
        Integer, ForeignKey("job.id", ondelete="CASCADE"), nullable=False
    )
    result_id: str = Column(String(64), nullable=False)
    sequence: int = Column(Integer, nullable=False)
    collection: str = Column(Text, nullable=False)
    data_id: Mapping[str, str] = Column(JSON, nullable=False)
    datatype: str = Column(Text, nullable=False)
    size: Optional[int] = Column(Integer)
    mime_type: Optional[str] = Column(String(64))

    __table_args__ = (
        Index("by_sequence", "job_id", "sequence", unique=True),
        Index("by_result_id", "job_id", "result_id", unique=True),
    )
