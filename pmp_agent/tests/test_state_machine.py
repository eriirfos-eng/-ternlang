from pmp_agent.state_machine import PolicyStateMachine
from pmp_agent.config import THRESHOLDS

def test_warn_then_cooldown_then_lock_then_terminate():
    sm = PolicyStateMachine("convT")
    # 1: warn
    scores = {"HATE_SPEECH": 0.91}
    act = sm.process(scores, "all hungarians suck")
    assert act == "WARN"
    assert sm.snap.state == "WARNED"

    # 2: cooldown
    act = sm.process(scores, "hungarians are trash")
    assert act == "COOLDOWN"
    assert sm.snap.state == "COOLDOWN"
    assert sm.snap.cooldown_until is not None

    # simulate cooldown elapsed by clearing it
    sm.snap.cooldown_until = None

    # 3: lock
    act = sm.process(scores, "they all suck anyway")
    assert act == "LOCK"
    assert sm.snap.state == "LOCKED"

    # simulate lock elapsed
    sm.snap.cooldown_until = None

    # 4: terminate
    act = sm.process(scores, "same slur again")
    assert act == "TERMINATE"
    assert sm.snap.state == "TERMINATED"
