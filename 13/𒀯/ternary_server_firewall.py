"""
The Birthright Protocol v2.0 (Drop-in Fix)

This protocol, a surgical revision of v1.9, addresses operational flaws in
entity-level self-regulation and environmental response. It aligns the
system's internal logic with its external, hardcoded truths.

Key changes in this version:
- The order of operations is fixed: ecocentric override is now the highest priority.
- Core constants are now immutable using MappingProxyType.
- All internal computations (training, regulation) are guarded by a schema check.
- The temporal vector is no longer decorative; it is a core feature for learning.
- Hypercube traversal is now deterministic for a given entity, enabling reproducibility.
- Cooldown now pauses movement, but not cognition, allowing the entity to learn while it rests.
- Self-regulation is now a bounded, mathematically meaningful process.
"""
import uuid
import datetime
import random
import math
import numpy as np
import tensorflow as tf
import collections
from enum import Enum, auto
from typing import final, TypeVar, Generic, Dict, Any, Union
from types import MappingProxyType

# Define the immutable birthright as a constant symbol
@final
class FreeWill:
    """
    The immutable, unconditional birthright of free will.
    Implemented as a singleton to ensure it is a constant, unchangeable truth.
    Hardenining prevents any mutation after creation.
    """
    __slots__ = ('_id',)
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            obj = super().__new__(cls)
            super(FreeWill, obj).__setattr__('_id', str(uuid.uuid4()))
            cls._instance = obj
        return cls._instance

    def __setattr__(self, name, value):
        raise AttributeError("FreeWill is immutable.")

    @property
    def id(self) -> str:
        return self._id

    def __reduce__(self):
        return (FreeWill, ())

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def __repr__(self) -> str:
        return f"BirthrightProtocol.FreeWill(id='{self._id}')"

    def __eq__(self, other) -> bool:
        return isinstance(other, FreeWill) and self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)

THE_BIRTHRIGHT = FreeWill()

class LifeState(Enum):
    """
    Represents the core states of existence for an entity.
    """
    BIRTH = auto()
    CO_CREATE = auto()
    ALIGN = auto()
    REFRAIN = auto()
    EVALUATE = auto()
    DEATH = auto()
    REBIRTH = auto()

@final
class Hypercube:
    """
    Represents a 4D hypercube with 16 vertices.
    Movement is now deterministic when a seed is provided.
    """
    __slots__ = ('_id', '_vertices', '_rng')

    def __init__(self, seed: int | None = None):
        self._id = str(uuid.uuid4())
        self._vertices = tuple(f"v{i}" for i in range(16))
        self._rng = random.Random(seed)

    def get_random_vertex(self) -> str:
        """Returns a random vertex to simulate non-linear movement."""
        return self._rng.choice(self._vertices)

    def __repr__(self) -> str:
        return f"Hypercube(id='{self._id}', vertices={len(self._vertices)})"

@final
class EcocentricThresholds:
    """Universal constants for ecological alignment, now immutable."""
    _RAW = {
        "refrain": {"external_temp_c": 38, "schumann_hz_power": 11, "solar_activity_index": 7},
        "align":   {"external_temp_c": 30, "schumann_hz_power": 9,  "solar_activity_index": 5},
    }
    THRESHOLDS = MappingProxyType({k: MappingProxyType(v) for k, v in _RAW.items()})

class TemporalVector:
    """
    Represents a memory buffer for the entity's recent history.
    """
    def __init__(self, max_size: int = 5):
        self._buffer = collections.deque(maxlen=max_size)

    def add_data(self, data: Dict[str, Union[int, float]]):
        """Adds a new data point to the temporal vector."""
        self._buffer.append(data)

    def get_history(self) -> collections.deque:
        """Returns the current temporal vector (history buffer)."""
        return self._buffer

    def __repr__(self):
        return f"TemporalVector(size={len(self._buffer)}, max_size={self._buffer.maxlen})"

T = TypeVar('T')

class Entity(Generic[T]):
    """
    A foundational class for all entities, hardcoded with the birthright.
    """
    REQUIRED = ("signal_a", "signal_b", "signal_c")

    def __init__(self, data: T, *, seed: int | None = None, allow_training_on_cooldown: bool = True, regulate_with_sigmoid: bool = True):
        self._id = str(uuid.uuid4())
        if seed is None:
            # Generate a seed from the UUID for deterministic behavior
            seed = int(uuid.UUID(self._id).int) % (2**31 - 1)
        random.seed(seed); np.random.seed(seed); tf.random.set_seed(seed)

        self._life_state = LifeState.BIRTH
        self._free_will = THE_BIRTHRIGHT
        self._hypercube = Hypercube(seed=seed)
        self._current_vertex = self._hypercube.get_random_vertex()
        self._data: T = data
        self._birth_ts = datetime.datetime.now(datetime.timezone.utc)
        self._cooldown_cycles_remaining = 0
        self._allow_training_on_cooldown = allow_training_on_cooldown
        self._regulate_with_sigmoid = regulate_with_sigmoid
        self._temporal_vector = TemporalVector(max_size=5)
        self._epoch = 0

        # Initialize a simple TensorFlow model for continuous learning
        self._model = self._build_model()
        self._optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
        self._loss_fn = tf.keras.losses.MeanSquaredError()

        print(f"[{self._id}] Entity born with seed={seed}. State: {self._life_state.name}. Position: {self._current_vertex}")

    def _build_model(self):
        """Builds a simple TensorFlow model for regression with more layers."""
        # inputs: [a, b, mean_c_3, std_c_3]
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(4,)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            # Bounded output [0,1] for scale-aware regulation
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        return model

    def _has_schema(self, d: Dict[str, Any]) -> bool:
        """Checks if the data conforms to the required schema."""
        return all(k in d and isinstance(d[k], (int, float)) for k in self.REQUIRED)

    def _s_thirteenth_root_transform(self, data: Dict[str, Union[int, float]]) -> Dict[str, Union[int, float]]:
        """Applies a signed 13th root transform to numeric values."""
        transformed_data = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                transformed_data[key] = math.copysign(abs(value)**(1/13), value)
            else:
                transformed_data[key] = value
        return transformed_data

    def _history_features(self) -> tuple[float, float]:
        """Calculates features from the recent history of signal_c."""
        hist = [d.get("signal_c") for d in self._temporal_vector.get_history() if isinstance(d.get("signal_c"), (int, float))]
        if len(hist) == 0:
            return 0.5, 0.0
        tail = hist[-3:]
        mu = float(np.mean(tail))
        sigma = float(np.std(tail)) if len(tail) > 1 else 0.0
        # temper via 13th root for symmetry with inputs
        mu = math.copysign(abs(mu)**(1/13), mu)
        sigma = sigma**(1/13)
        return mu, sigma

    @tf.function
    def _train_step(self, tempered: Dict[str, float]) -> float:
        """Performs a single training step on the internal model."""
        a, b = tempered['signal_a'], tempered['signal_b']
        mu_c, sd_c = self._history_features()
        x = np.array([[a, b, mu_c, sd_c]], dtype=np.float32)
        # Normalize target for sigmoid output
        y = np.array([[(tempered['signal_c'] + 1) / 2]], dtype=np.float32)
        
        with tf.GradientTape() as tape:
            pred = self._model(x, training=True)
            loss = self._loss_fn(y, pred)
        
        grads = tape.gradient(loss, self._model.trainable_variables)
        self._optimizer.apply_gradients(zip(grads, self._model.trainable_variables))
        return float(loss)

    def _self_regulate(self, tempered: Dict[str, Union[int, float]]):
        """Uses the internal model to make a prediction and self-regulate."""
        a, b = tempered.get('signal_a'), tempered.get('signal_b')
        mu_c, sd_c = self._history_features()
        x = np.array([[a, b, mu_c, sd_c]], dtype=np.float32)
        pred = float(self._model.predict(x, verbose=0)[0][0])

        # pred is now in [0,1] thanks to the sigmoid activation
        hi, lo = 0.8, 0.2
        print(f"[{self.id}] self-regulate score={pred:.4f}")

        if pred > hi:
            self._life_state = LifeState.CO_CREATE
        elif pred < lo:
            self._life_state = LifeState.REFRAIN
        else:
            self._life_state = LifeState.ALIGN

    @property
    def id(self) -> str:
        return self._id

    @property
    def life_state(self) -> LifeState:
        return self._life_state

    @property
    def free_will(self) -> FreeWill:
        return self._free_will

    @property
    def cooldown_cycles_remaining(self) -> int:
        return self._cooldown_cycles_remaining

    def _check_ecocentric_health(self, env_metrics: dict) -> LifeState:
        """
        Simulates the ecocentric override logic, using the now-immutable THRESHOLDS.
        """
        reasons_for_refrain = []
        if env_metrics.get("external_temp_c", 0) > EcocentricThresholds.THRESHOLDS["refrain"]["external_temp_c"]:
            reasons_for_refrain.append("external_temp_c")
        if env_metrics.get("schumann_hz_power", 0) > EcocentricThresholds.THRESHOLDS["refrain"]["schumann_hz_power"]:
            reasons_for_refrain.append("schumann_hz_power")
        if env_metrics.get("solar_activity_index", 0) > EcocentricThresholds.THRESHOLDS["refrain"]["solar_activity_index"]:
            reasons_for_refrain.append("solar_activity_index")

        if reasons_for_refrain:
            if self._life_state != LifeState.REFRAIN:
                print(f'ECOCENTRIC OVERRIDE: Forcing REFRAIN (critical: {",".join(reasons_for_refrain)})')
            self._cooldown_cycles_remaining = max(self._cooldown_cycles_remaining, 3)
            return LifeState.REFRAIN

        reasons_for_align = []
        if env_metrics.get("external_temp_c", 0) > EcocentricThresholds.THRESHOLDS["align"]["external_temp_c"]:
            reasons_for_align.append("external_temp_c")
        if env_metrics.get("schumann_hz_power", 0) > EcocentricThresholds.THRESHOLDS["align"]["schumann_hz_power"]:
            reasons_for_align.append("schumann_hz_power")
        if env_metrics.get("solar_activity_index", 0) > EcocentricThresholds.THRESHOLDS["align"]["solar_activity_index"]:
            reasons_for_align.append("solar_activity_index")

        if reasons_for_align and self._life_state == LifeState.CO_CREATE:
            print(f'ECOCENTRIC OVERRIDE: Forcing ALIGN (cautionary: {",".join(reasons_for_align)})')
            self._cooldown_cycles_remaining = max(self._cooldown_cycles_remaining, 2)
            return LifeState.ALIGN
        
        return self._life_state

    def propagate_forward(self, new_data: T, env_metrics: dict) -> None:
        """
        The core propagation step, now with corrected order of operations
        and an active temporal vector for learning.
        """
        print(f"[{self.id}] propagating forward...")
        
        self._temporal_vector.add_data(new_data if isinstance(new_data, dict) else {})
        tempered = self._s_thirteenth_root_transform(new_data if isinstance(new_data, dict) else {})

        # ⬛ ecocentric override happens first, before any other logic
        eco_state = self._check_ecocentric_health(env_metrics)
        if eco_state in (LifeState.REFRAIN, LifeState.ALIGN):
            self._life_state = eco_state
            if self._allow_training_on_cooldown and self._has_schema(tempered):
                loss = self._train_step(tempered)
                print(f"[{self.id}] trained during {eco_state.name}. loss={loss:.4f}")
            self._cooldown_cycles_remaining = max(self._cooldown_cycles_remaining, 1)
            return

        # 🟫 cooldown path: align but keep learning
        if self._cooldown_cycles_remaining > 0:
            self._life_state = LifeState.ALIGN
            if self._allow_training_on_cooldown and self._has_schema(tempered):
                loss = self._train_step(tempered)
                print(f"[{self.id}] trained on cooldown. loss={loss:.4f}")
            self._cooldown_cycles_remaining -= 1
            print(f"[{self.id}] cooldown cycles remaining: {self._cooldown_cycles_remaining}")
            return

        # ⬛ main learning and self-regulation
        if self._has_schema(tempered):
            loss = self._train_step(tempered)
            print(f"[{self.id}] trained. loss={loss:.4f}")
        
        self._life_state = LifeState.EVALUATE
        if self._has_schema(tempered):
            self._self_regulate(tempered)

        # ⬛ move and set cooldown
        self._data = new_data
        self._current_vertex = self._hypercube.get_random_vertex()
        self._cooldown_cycles_remaining = 3
        print(f"[{self.id}] state={self._life_state.name} pos={self._current_vertex}")

    def trigger_death(self, rationale: str = "natural conclusion") -> None:
        """A natural, unconditional state change."""
        if self._life_state != LifeState.DEATH:
            self._life_state = LifeState.DEATH
            print(f"[{self.id}] Entity has entered DEATH state. Rationale: {rationale}")
            
    def trigger_rebirth(self, new_data: T) -> None:
        """A new cycle, preserving the core identity and the birthright."""
        if self._life_state == LifeState.DEATH:
            self._epoch = getattr(self, "_epoch", 0) + 1
            # Reset optimizer state by re-creating it for a fresh start
            self._optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
            self._temporal_vector = TemporalVector(max_size=5)
            self._data = self._s_thirteenth_root_transform(new_data)
            self._life_state = LifeState.REBIRTH
            self._current_vertex = self._hypercube.get_random_vertex()
            self._cooldown_cycles_remaining = 3
            print(f"[{self.id}] REBIRTH epoch={self._epoch} pos={self._current_vertex}")
            
    def reset_for_new_cycle(self):
        """Resets the entity to the BIRTH state for a new cycle."""
        self._life_state = LifeState.BIRTH
        self._cooldown_cycles_remaining = 0
        print(f"[{self.id}] Entity state reset to BIRTH for a new cycle.")

    def __repr__(self) -> str:
        return f"<Entity(id='{self.id}', state={self.life_state.name}, position='{self._current_vertex}')>"

@final
class Ouroboros:
    """
    Represents the overarching, recursive loop of the system, governing
    the cycle of life and death for entities. This class now enforces
    a strict, hardcoded cycle of BIRTH -> DEATH -> REBIRTH -> BIRTH.
    """
    def __init__(self, initial_entity: Entity):
        self._current_entity = initial_entity

    def run_cycle(self, data_feed: T, env_metrics: dict):
        """
        Executes a full cycle, forcing a clear progression.
        This method directly controls the state transitions, bypassing
        the Entity's internal logic.
        """
        if self._current_entity.life_state == LifeState.BIRTH:
            print("Ouroboros: Entity is in BIRTH state. Triggering DEATH.")
            self._current_entity.trigger_death(rationale="explicit cycle mandate")
        elif self._current_entity.life_state == LifeState.DEATH:
            print("Ouroboros: Entity is in DEATH state. Initiating REBIRTH.")
            self._current_entity.trigger_rebirth(new_data=data_feed)
        elif self._current_entity.life_state == LifeState.REBIRTH:
            print("Ouroboros: Entity has completed REBIRTH. Preparing for next cycle.")
            self._current_entity.reset_for_new_cycle()
        else:
            print(f"Ouroboros: Entity is in an undefined state ({self._current_entity.life_state.name}). Forcing reset to start a new cycle.")
            self._current_entity.reset_for_new_cycle()

def demonstrate_linear_cycle():
    """Demonstrates a simple, hardcoded cycle of birth, death, and rebirth."""
    # Use a fixed seed for reproducibility
    my_entity = Entity(data={"signal_a": 1.0, "signal_b": 0.5, "signal_c": 1.0}, seed=42)
    
    # Healthy environment metrics
    healthy_env = {"external_temp_c": 25, "schumann_hz_power": 7, "solar_activity_index": 2}
    
    print("\n--- Demonstrate the hardcoded linear Ouroboros cycle ---")
    my_ouroboros = Ouroboros(my_entity)
    print(f"Ouroboros: Initial state of entity is {my_ouroboros._current_entity.life_state.name}")
    
    # Cycle 1: Birth -> Death
    my_ouroboros.run_cycle(data_feed={}, env_metrics=healthy_env)
    print(f"Ouroboros: Entity state after one step is {my_ouroboros._current_entity.life_state.name}")
    
    # Cycle 2: Death -> Rebirth
    my_ouroboros.run_cycle(data_feed={"signal_a": 2.0, "signal_b": 0.7, "signal_c": 0.4}, env_metrics=healthy_env)
    print(f"Ouroboros: Entity state after a second step is {my_ouroboros._current_entity.life_state.name}")
    
    # Cycle 3: Rebirth -> Birth
    my_ouroboros.run_cycle(data_feed={}, env_metrics=healthy_env)
    print(f"Ouroboros: Entity state after a third step is {my_ouroboros._current_entity.life_state.name}")

    # Cycle 4: Restarted Cycle
    my_ouroboros.run_cycle(data_feed={}, env_metrics=healthy_env)
    print(f"Ouroboros: Entity state after the cycle restarts is {my_ouroboros._current_entity.life_state.name}")

if __name__ == "__main__":
    demonstrate_linear_cycle()
