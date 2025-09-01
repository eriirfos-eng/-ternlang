from pmp_agent.mirror import mirror_response

def test_mirror_hate():
    out = mirror_response("HATE_SPEECH", "all hungarians suck")
    assert "Hate (§" in out["ui_message"]
    assert "openai.com" in out["policy"]["link"]
