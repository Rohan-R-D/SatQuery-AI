import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Index, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ExecutionModel(Base):
    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    task: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    input_type: Mapped[str] = mapped_column(String(30), nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="RUNNING")
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    change_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duration_sec: Mapped[float] = mapped_column(Float, default=0.0)
    started_at: Mapped[str] = mapped_column(String(50), nullable=False)
    completed_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        index=True
    )

    trace_steps: Mapped[List["TraceStepModel"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="TraceStepModel.step_number"
    )
    evidence_items: Mapped[List["EvidenceItemModel"]] = relationship(
        back_populates="execution",
        cascade="all, delete-orphan"
    )


class TraceStepModel(Base):
    __tablename__ = "trace_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    timestamp: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    execution: Mapped["ExecutionModel"] = relationship(back_populates="trace_steps")

    __table_args__ = (
        Index("ix_trace_steps_exec_step", "execution_id", "step_number"),
    )


class EvidenceItemModel(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    limitations_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    execution: Mapped["ExecutionModel"] = relationship(back_populates="evidence_items")
