# Neurosym Agent

**Protocol:** JSON schema + core validation for neurosymbolic agents.

- `flow` (+1): synchronicity, affirmation
- `noise` (0): mild deviation, tending
- `silence` (-1): breakdown, void

## Quickstart

```bash
pip install -r requirements.txt
python cli.py example.json
```

## Example Payload

```json
{
  "agentId": "demo-01",
  "timestamp": "2025-09-02T13:49:27Z",
  "location": { "latitude": 47.07, "longitude": 15.43, "city": "Graz" },
  "protocolStatus": "flow",
  "sensorData": {
    "magneticField": 44.1,
    "lightIntensity": 320,
    "soundLevel": 55,
    "gravity": 9.8,
    "accelerometer": {"x":0,"y":0,"z":9.8},
    "gyroscope": {"x":0,"y":0,"z":0},
    "barometer": 1013,
    "proximity": 10
  }
}
```
