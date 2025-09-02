from neurosym_agent.core import Agent, Status

def test_state_mapping():
    agent = Agent(
        agentId="test",
        timestamp="2025-09-02T00:00:00Z",
        location={"latitude":1.0,"longitude":2.0,"city":"Test"},
        protocolStatus="flow",
        sensorData={
            "magneticField":1.0,"lightIntensity":1.0,"soundLevel":1.0,"gravity":9.8,
            "accelerometer":{"x":0,"y":0,"z":9.8},
            "gyroscope":{"x":0,"y":0,"z":0},
            "barometer":1000.0,"proximity":5.0
        }
    )
    assert agent.state() == 1
