from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from models import WorkflowModel, WorkflowInstance, TransitionAudit
import uuid
import json
import pandas as pd
from io import StringIO

from database import Base, engine, SessionLocal
from registry import register_model, activate_model
from anomaly import compute_anomaly_score

# =====================================================
# DATABASE INIT
# =====================================================

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DappGenius CyberFlow™",
    version="1.0.0",
    description="AI-Governed Workflow Intelligence Engine"
)

# =====================================================
# DB Dependency
# =====================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =====================================================
# MODEL GENERATION
# =====================================================

def generate_model_schema(domain: str):

    domain = domain.lower()

    if domain == "cybersecurity":
        states = ["event_detected","threat_classified","risk_scored","mitigated","archived"]
        transitions = [
            {"event":"classify","from":"event_detected","to":"threat_classified"},
            {"event":"score_risk","from":"threat_classified","to":"risk_scored"},
            {"event":"mitigate","from":"risk_scored","to":"mitigated"},
            {"event":"archive","from":"mitigated","to":"archived"},
        ]

    elif domain == "sessions":
        states = ["login_attempt","duo_authenticated","risk_evaluated","active_session","terminated"]
        transitions = [
            {"event":"authenticate","from":"login_attempt","to":"duo_authenticated"},
            {"event":"evaluate_risk","from":"duo_authenticated","to":"risk_evaluated"},
            {"event":"activate","from":"risk_evaluated","to":"active_session"},
            {"event":"terminate","from":"active_session","to":"terminated"},
        ]

    elif domain == "transactions":
        states = ["created","validated","fraud_checked","approved","committed"]
        transitions = [
            {"event":"validate","from":"created","to":"validated"},
            {"event":"fraud_check","from":"validated","to":"fraud_checked"},
            {"event":"approve","from":"fraud_checked","to":"approved"},
            {"event":"commit","from":"approved","to":"committed"},
        ]

    elif domain == "organizations":
        states = ["registered","verified","compliance_checked","activated","audited"]
        transitions = [
            {"event":"verify","from":"registered","to":"verified"},
            {"event":"compliance_review","from":"verified","to":"compliance_checked"},
            {"event":"activate","from":"compliance_checked","to":"activated"},
            {"event":"audit","from":"activated","to":"audited"},
        ]

    else:
        states = ["INIT","ACTIVE","COMPLETED"]
        transitions = [
            {"event":"start","from":"INIT","to":"ACTIVE"},
            {"event":"finish","from":"ACTIVE","to":"COMPLETED"},
        ]

    return {"domain": domain, "states": states, "transitions": transitions}

# =====================================================
# MODEL ENDPOINTS
# =====================================================

@app.post("/model/generate")
def generate_model(domain: str, db: Session = Depends(get_db)):
    schema = generate_model_schema(domain)
    model = register_model(db, domain, schema)
    return {"model_id": model.model_id, "version": model.version}

@app.post("/model/activate")
def activate(model_id: str, version: str, db: Session = Depends(get_db)):
    model = activate_model(db, model_id, version)
    return {"status": model.status}

# =====================================================
# WORKFLOW CREATION
# =====================================================

@app.post("/workflow/create")
def create_workflow(model_id: str, version: str, db: Session = Depends(get_db)):

    model = db.query(WorkflowModel)\
        .filter_by(model_id=model_id, version=version, status="ACTIVE")\
        .first()

    if not model:
        raise HTTPException(status_code=404, detail="Active model not found")

    model_data = json.loads(model.model_json)
    initial_state = model_data["states"][0]

    instance = WorkflowInstance(
        workflow_id=str(uuid.uuid4()),
        model_id=model_id,
        model_version=version,
        current_state=initial_state,
        history=json.dumps([initial_state])
    )

    db.add(instance)
    db.commit()

    return {"workflow_id": instance.workflow_id, "current_state": initial_state}

# =====================================================
# ALLOWED EVENTS
# =====================================================

@app.get("/workflow/{workflow_id}/allowed-events")
def allowed_events(workflow_id: str, db: Session = Depends(get_db)):

    instance = db.query(WorkflowInstance)\
        .filter_by(workflow_id=workflow_id)\
        .first()

    if not instance:
        raise HTTPException(status_code=404, detail="Workflow not found")

    model = db.query(WorkflowModel)\
        .filter_by(model_id=instance.model_id, version=instance.model_version)\
        .first()

    model_data = json.loads(model.model_json)

    allowed = [
        t["event"]
        for t in model_data["transitions"]
        if t["from"] == instance.current_state
    ]

    return {"events": allowed}

# =====================================================
# EXECUTE TRANSITION
# =====================================================

@app.post("/workflow/{workflow_id}/execute")
def execute_event(workflow_id: str, event: str, db: Session = Depends(get_db)):

    instance = db.query(WorkflowInstance)\
        .filter_by(workflow_id=workflow_id)\
        .first()

    if not instance:
        raise HTTPException(status_code=404, detail="Workflow not found")

    model = db.query(WorkflowModel)\
        .filter_by(model_id=instance.model_id, version=instance.model_version)\
        .first()

    model_data = json.loads(model.model_json)

    transition = next(
        (t for t in model_data["transitions"]
         if t["from"] == instance.current_state and t["event"] == event),
        None
    )

    if not transition:
        raise HTTPException(status_code=400, detail="Illegal transition")

    next_state = transition["to"]
    state_index = model_data["states"].index(next_state)

    raw_score, normalized_score = compute_anomaly_score(state_index, 1.0)

    severity = "LOW"
    if normalized_score > 0.85:
        severity = "HIGH"
    elif normalized_score > 0.6:
        severity = "MEDIUM"

    audit = TransitionAudit(
        workflow_id=workflow_id,
        from_state=instance.current_state,
        to_state=next_state,
        severity=severity,
        normalized_score=normalized_score,
        archived=False,
        domain=model_data.get("domain", "unknown")
    )

    db.add(audit)

    instance.current_state = next_state
    history = json.loads(instance.history)
    history.append(next_state)
    instance.history = json.dumps(history)

    db.commit()

    return {"new_state": next_state, "severity": severity}

# =====================================================
# CSV SCORING (PERSISTED TO GOVERNANCE)
# =====================================================

@app.post("/analytics/score-csv")
async def score_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):

    contents = await file.read()
    decoded = contents.decode("utf-8")

    try:
        df = pd.read_csv(StringIO(decoded))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    required_columns = {"workflow_id", "state_index", "time_delta"}

    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail="CSV must contain: workflow_id, state_index, time_delta"
        )

    results = []

    for _, row in df.iterrows():

        raw_score, normalized_score = compute_anomaly_score(
            int(row["state_index"]),
            float(row["time_delta"])
        )

        severity = "LOW"
        if normalized_score > 0.85:
            severity = "HIGH"
        elif normalized_score > 0.6:
            severity = "MEDIUM"

        audit = TransitionAudit(
            workflow_id=row["workflow_id"],
            from_state="CSV_INPUT",
            to_state=f"STATE_{row['state_index']}",
            severity=severity,
            normalized_score=normalized_score,
            archived=False,
            domain="csv_batch"
        )

        db.add(audit)

        results.append({
            "workflow_id": row["workflow_id"],
            "state_index": row["state_index"],
            "time_delta": row["time_delta"],
            "raw_score": raw_score,
            "normalized_score": normalized_score,
            "severity": severity
        })

    db.commit()

    return results

# =====================================================
# GOVERNANCE
# =====================================================

@app.get("/analytics/by-domain")
def analytics_by_domain(db: Session = Depends(get_db)):

    audits = db.query(TransitionAudit).filter_by(archived=False).all()

    summary = {}

    for audit in audits:
        domain = audit.domain or "unknown"

        if domain not in summary:
            summary[domain] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

        summary[domain][audit.severity] += 1

    return summary
# =====================================================
# ALL HISTORY (NEW)
# =====================================================

@app.get("/analytics/history")
def full_history(db: Session = Depends(get_db)):
    records = db.query(TransitionAudit).all()

    return [
        {
            "workflow_id": r.workflow_id,
            "from_state": r.from_state,
            "to_state": r.to_state,
            "severity": r.severity,
            "normalized_score": r.normalized_score,
            "archived": r.archived,
            "timestamp": r.timestamp
        }
        for r in records
    ]
