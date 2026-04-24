from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer, Text
from database import Base
from datetime import datetime
import uuid

# =====================================================
# 📘 Workflow Model Registry
# =====================================================

class WorkflowModel(Base):
    __tablename__ = "workflow_models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String, index=True)
    version = Column(String)
    status = Column(String)  # DRAFT / ACTIVE
    model_json = Column(Text)  # Stored model schema
    model_hash = Column(String)
    anchored_block_index = Column(Integer, nullable=True)


# =====================================================
# 🔗 Blockchain Ledger Blocks
# =====================================================

class LedgerBlock(Base):
    __tablename__ = "ledger_blocks"

    index = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    model_hash = Column(String)
    previous_hash = Column(String)
    block_hash = Column(String)


# =====================================================
# 🔄 Workflow Instance (Run)
# =====================================================

class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String)
    model_version = Column(String)
    current_state = Column(String)
    history = Column(Text)  # JSON-encoded state history


# =====================================================
# 📊 Transition Audit (Execution History)
# =====================================================

class TransitionAudit(Base):
    __tablename__ = "transition_audit"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String)
    from_state = Column(String)
    to_state = Column(String)
    severity = Column(String)  # LOW / MEDIUM / HIGH
    normalized_score = Column(Float)
    archived = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # 🔥 REQUIRED FOR GOVERNANCE
    domain = Column(String)
