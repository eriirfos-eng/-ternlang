import json
from pathlib import Path
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Any

class Status(str, Enum):
    FLOW = "flow"
    NOISE = "noise"
    SILENCE = "silence"

class Location(BaseModel):
    latitude: float
    longitude: float
    city: str
    country: Optional[str] = None

class Accelerometer(BaseModel):
    x: float
    y: float
    z: float

class Gyroscope(BaseModel):
    x: float
    y: float
    z: float

class SensorData(BaseModel):
    magneticField: float
    lightIntensity: float
    soundLevel: float
    gravity: float
    accelerometer: Accelerometer
    gyroscope: Gyroscope
    barometer: float
    proximity: float
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    note: Optional[str] = None

class Agent(BaseModel):
    agentId: str
    timestamp: str
    location: Location
    protocolStatus: Status
    sensorData: SensorData
    flowData: Optional[Dict[str, Any]] = None
    noiseData: Optional[Dict[str, Any]] = None
    silenceData: Optional[Dict[str, Any]] = None
    internalNotes: Optional[str] = None

    def state(self) -> int:
        mapping = {Status.FLOW: 1, Status.NOISE: 0, Status.SILENCE: -1}
        return mapping[self.protocolStatus]

def load_agent(path: str) -> Agent:
    with Path(path).open() as f:
        data = json.load(f)
    return Agent(**data)
