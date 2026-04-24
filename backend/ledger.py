import hashlib
import json
from datetime import datetime
from sqlalchemy.orm import Session
from models import LedgerBlock

def hash_block(data: dict):
    block_string = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def anchor_model_hash(db: Session, model_hash: str):

    last_block = db.query(LedgerBlock).order_by(LedgerBlock.index.desc()).first()

    if not last_block:
        previous_hash = "0"
        index = 0
    else:
        previous_hash = last_block.block_hash
        index = last_block.index + 1

    block_data = {
        "index": index,
        "timestamp": str(datetime.utcnow()),
        "model_hash": model_hash,
        "previous_hash": previous_hash,
    }

    block_hash = hash_block(block_data)

    new_block = LedgerBlock(
        index=index,
        timestamp=datetime.utcnow(),
        model_hash=model_hash,
        previous_hash=previous_hash,
        block_hash=block_hash
    )

    db.add(new_block)
    db.commit()
    db.refresh(new_block)

    return new_block