"""
Minimal example using the kernel from code.
"""
from ternkernel.api.server import app  # ensures imports resolve
from ternkernel.adapters.numpy_bridge import safe_div
from ternkernel.agents.time_crystal.agent import TimeCrystalAgent, CollapseConfig

if __name__ == "__main__":
    print("safe_div demo:", safe_div([1,2,3],[1,0,2]))
    ag = TimeCrystalAgent(CollapseConfig())
    print("collapse demo:", ag.collapse(0, 1, 0))
