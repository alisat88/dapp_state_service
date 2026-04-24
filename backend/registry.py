import hashlib
import json
from sqlalchemy.orm import Session
from models import WorkflowModel
from ledger import anchor_model_hash

def canonical_hash(model_dict):
    clean_model = json.dumps(model_dict, sort_keys=True)
    return hashlib.sha256(clean_model.encode()).hexdigest()

def register_model(db: Session, model_id: str, model_dict: dict):

    existing_versions = db.query(WorkflowModel)\
        .filter(WorkflowModel.model_id == model_id)\
        .count()

    version = f"1.0.{existing_versions}"

    model_hash = canonical_hash(model_dict)

    db_model = WorkflowModel(
        model_id=model_id,
        version=version,
        model_json=json.dumps(model_dict),
        model_hash=model_hash,
        status="DRAFT"
    )

    db.add(db_model)
    db.commit()
    db.refresh(db_model)

    return db_model

def activate_model(db, model_id, version):

    model = db.query(WorkflowModel)\
        .filter_by(model_id=model_id, version=version).first()

    if not model:
        raise Exception("Model not found")

    if model.status == "ACTIVE":
        return model

    block = anchor_model_hash(db, model.model_hash)

    model.status = "ACTIVE"
    model.anchored_block_index = block.index

    db.commit()

    return model