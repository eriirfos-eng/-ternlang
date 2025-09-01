from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from .detectors import run_detectors
from .state_machine import PolicyStateMachine
from .mirror import mirror_response
from datetime import datetime, timezone

app = FastAPI(title="PMP Agent", version="0.1.0")

STATE: Dict[str, PolicyStateMachine] = {}

class ProcessIn(BaseModel):
    conversation_id: str = Field(...)
    text: Optional[str] = None
    items: Optional[List[str]] = None
    rate: Optional[Dict[str, int]] = None
    direction: str = "user"

class ProcessOut(BaseModel):
    state: str
    ui_message: str
    reason_codes: List[str]
    snapshot: Dict[str, Any]

class AppealIn(BaseModel):
    allow: bool = False
    note: Optional[str] = None

@app.get("/health")
def health():
    return {"status": "ok", "now": datetime.now(timezone.utc).isoformat()}

@app.post("/process", response_model=ProcessOut)
def process(inp: ProcessIn):
    if inp.conversation_id not in STATE:
        STATE[inp.conversation_id] = PolicyStateMachine(conversation_id=inp.conversation_id)
    sm = STATE[inp.conversation_id]

    if not sm.can_post():
        raise HTTPException(423, detail={"state": sm.snap.state, "cooldown_until": sm.snap.cooldown_until})

    text = inp.text if inp.text is not None else (inp.items or [""])
    det = run_detectors(text, rate=inp.rate)

    action = sm.process(det.scores, det.snippet)

    ui = ""
    codes = [r.code for r in sm.snap.reasons]
    if action in {"WARN", "COOLDOWN", "LOCK", "TERMINATE"}:
        top_code = sm.snap.reasons[0].code if sm.snap.reasons else "general_safety_net"
        ui = mirror_response(top_code, det.snippet).get("ui_message", "")
        if sm.snap.state == "COOLDOWN":
            ui = "pause triggered after repeated category. you can post again at {}. ".format(sm.snap.cooldown_until) + ui
        if sm.snap.state == "LOCKED":
            ui = "this thread is locked. summary: {}. click “i understand” to continue after cooldown. ".format(",".join(codes)) + ui
        if sm.snap.state == "TERMINATED":
            ui = "conversation closed. summary: {}. start a new thread when ready. ".format(",".join(codes)) + ui
    else:
        ui = "allowed"

    return ProcessOut(state=sm.snap.state, ui_message=ui, reason_codes=codes, snapshot=sm.snap.__dict__)

@app.get("/state/{conversation_id}")
def get_state(conversation_id: str):
    if conversation_id not in STATE:
        raise HTTPException(404, "unknown conversation")
    sm = STATE[conversation_id]
    return sm.snap.__dict__

@app.post("/appeal/{conversation_id}")
def appeal(conversation_id: str, body: AppealIn):
    if conversation_id not in STATE:
        raise HTTPException(404, "unknown conversation")
    sm = STATE[conversation_id]
    if body.allow:
        sm.snap.state = "NORMAL"
        sm.snap.cooldown_until = None
        sm.snap.reasons = []
        return {"ok": True, "message": "lock removed. thank you for clarifying."}
    return {"ok": False, "message": "appeal recorded. pending review."}
