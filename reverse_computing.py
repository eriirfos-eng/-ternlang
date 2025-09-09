# reverse_computing.py

import os, sys, json, asyncio
from socket_custom import publish  # <-- unify backbone

# optional Firebase
try:
    from firebase_admin import credentials, initialize_app, firestore
except ImportError:
    firestore = None

__app_id = os.environ.get('__app_id', 'reverse-observer')
__firebase_config = os.environ.get('__firebase_config')

def apply_ternary_logic(data: dict) -> int:
    status = data.get("status", "").lower().strip()
    if any(k in status for k in ["online", "active", "complete"]):
        return 1
    elif any(k in status for k in ["error", "failure", "offline"]):
        return -1
    else:
        return 0

async def handle_update(doc_id, data):
    ternary = apply_ternary_logic(data)
    mapping = {1: "AFFIRM (+1)", -1: "DISCONFIRM (-1)", 0: "TEND (0)"}
    msg = f"OBS | doc={doc_id} ternary={mapping[ternary]} data={data}"
    await publish(msg)   # push into HUD bus

def start_observational_agent():
    if firestore and __firebase_config:
        cred = credentials.Certificate(json.loads(__firebase_config))
        initialize_app(cred)
        db = firestore.client()
        ref = db.collection(f"artifacts/{__app_id}/public/data/data_stream")

        def on_snapshot(col_snapshot, changes, read_time):
            for change in changes:
                data = change.document.to_dict()
                asyncio.create_task(handle_update(change.document.id, data))

        ref.on_snapshot(on_snapshot)
        print("[OBS] Listening to Firestore + publishing to socket bus.")
    else:
        print("[OBS] Firebase not available. Running in local-only mode.")

if __name__ == "__main__":
    start_observational_agent()
    asyncio.get_event_loop().run_forever()
