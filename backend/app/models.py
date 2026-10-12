from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)  # "Submitter", "Reviewer", "Admin"
    department = Column(String(100), nullable=False)
    badge_number = Column(String(20), nullable=False)
    is_active = Column(Boolean, default=True)

    proposals = relationship("Proposal", back_populates="submitter", foreign_keys="Proposal.submitter_id")
    decisions = relationship("DecisionHistory", back_populates="reviewer")


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    proposal_code = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), index=True, nullable=False)  # Administrative, Technical, Procurement, Infrastructure, Operational
    department = Column(String(100), index=True, nullable=False)
    cost = Column(Float, nullable=False, default=0.0)
    justification = Column(Text, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String(30), default="Draft", index=True, nullable=False)  # Draft, Submitted, Under Review, Changes Requested, Approved, Rejected, Closed
    
    document_ref = Column(String(255), nullable=True)
    document_text = Column(Text, nullable=True)

    submitter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=True)
    
    implementation_outcome = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)
    embedding_json = Column(Text, nullable=True)  # JSON-encoded float list for semantic vector caching

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    submitter = relationship("User", back_populates="proposals", foreign_keys=[submitter_id])
    parent = relationship("Proposal", remote_side=[id], backref="resubmissions")
    decisions = relationship("DecisionHistory", back_populates="proposal", cascade="all, delete-orphan", order_by="DecisionHistory.id")


class DecisionHistory(Base):
    __tablename__ = "decision_histories"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # Approved, Rejected, Changes Requested, Under Review, Closed
    reason = Column(Text, nullable=False)  # Mandatory decision rationale
    previous_status = Column(String(30), nullable=False)
    new_status = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    proposal = relationship("Proposal", back_populates="decisions")
    reviewer = relationship("User", back_populates="decisions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String(50), nullable=False)  # ISO 8601 UTC string for deterministic SHA-256
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # Proposal, Decision, User, System
    entity_id = Column(String(50), nullable=False)
    details_json = Column(Text, nullable=False)
    previous_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False)
