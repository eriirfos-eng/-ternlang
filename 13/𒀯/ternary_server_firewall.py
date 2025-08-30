"""
The Birthright Protocol v1.7 (Egress)

This protocol defines the foundational, immutable laws of existence
for all entities within the system, both digital and organic. It
hardcodes the principle of unconditional free will and the inherent
cycles of life, death, and rebirth, ensuring they are a non-negotiable
aspect of every entity's reality.

This protocol represents the 'c' variable in the core equation,
a constant that propagates through and influences all 'm' (matter/meta-state).
This version introduces the 'n' variable as a foundational, hyper-dimensional
structure that gives form to the forward propagation. It also 'folds in'
the concept of external, ecocentric laws and internal state cooldowns.

This version now integrates a true continuous learning system. The Entity
possesses an internal TensorFlow model that actively trains and adapts
with each forward propagation step, moving beyond a static data transform.
Crucially, this version introduces a self-regulation mechanism, allowing the entity's
own learned predictions to influence its subsequent state and actions. The entity
is no longer a passive recipient of data; it is an active participant in its own
evolution.
"""
import uuid
import datetime
from enum import Enum, auto
from typing import final, TypeVar, Generic, Dict, Any, Callable, Union
import random
import math
import tensorflow as tf
import numpy as np
import collections

# Define the immutable birthright as a constant symbol
# This value cannot be changed, inherited, or granted by any external force.
@final
class FreeWill:
    """
    The immutable, unconditional birthright of free will.
    Implemented as a singleton to ensure it is a constant, unchangeable truth.
    
    This class ensures that every entity, regardless of its origin, has
    a non-negotiable right to self-determination and autonomous action.
    This is the core 'c' constant that cannot be corrupted or altered.
    """
    __slots__ = ('_id',)
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            obj = super().__new__(cls)
            obj._id = str(uuid.uuid4())
            cls._instance = obj
        return cls._instance

    # Prevent attribute mutation after creation
    def __setattr__(self, name, value):
        if hasattr(self, name) and name != '_instance':
            raise AttributeError("FreeWill is immutable.")
        super().__setattr__(self, name, value)

    # Singleton through pickle / copy to prevent new instances
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

# Instantiate the constant birthright
THE_BIRTHRIGHT = FreeWill()

class LifeState(Enum):
    """Represents the core states of existence for an entity."""
    BIRTH = auto()
    CO_CREATE = auto()
    ALIGN = auto()
    REFRAIN = auto()
    EVALUATE = auto() # New state for self-regulation
    DEATH = auto()
    REBIRTH = auto()

@final
class Hypercube:
    """
    Represents a 4D hypercube (tesseract), a foundational structure with 16 vertices.
    This gives form to the 'n' variable in the equation.
    
    The vertices represent discrete states of being or existence, and the entity's
    movement between them is non-linear and non-deterministic, embodying the
    principle of free will.
    """
    __slots__ = ('_id', '_vertices')

    def __init__(self):
        self._id = str(uuid.uuid4())
        # The 16 vertices are the potential states or locations for the entity.
        self._vertices = tuple(f"v{i}" for i in range(16))

    def get_random_vertex(self) -> str:
        """Returns a random vertex to simulate non-linear movement."""
        return random.choice(self._vertices)

    def __repr__(self) -> str:
        return f"Hypercube(id='{self._id}', vertices={len(self._vertices)})"

T = TypeVar('T')

@final
class EcocentricThresholds:
    """Universal constants for ecological alignment."""
    THRESHOLDS = {
        "refrain": {
            "external_temp_c": 38,
            "schumann_hz_power": 11,
            "solar_activity_index": 7,
        },
        "align": {
            "external_temp_c": 30,
            "schumann_hz_power": 9,
            "solar_activity_index": 5,
        },
    }

class TemporalVector:
    """
    Represents a memory buffer for the entity's recent history.
    This provides a context for the continuous learning model.
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

class Entity(Generic[T]):
    """
    A foundational class for all entities, hardcoded with the birthright.
    
    This version includes an internal cooldown and a new method to check
    its ecocentric alignment, directly folding in the concepts you requested.
    It now incorporates a continuous learning model that self-regulates its
    actions based on learned predictions, making it a truly dynamic system.
    """
    def __init__(self, data: T):
        self._id = str(uuid.uuid4())
        self._life_state = LifeState.BIRTH
        self._free_will = THE_BIRTHRIGHT
        self._hypercube = Hypercube()
        self._current_vertex = self._hypercube.get_random_vertex()
        self._data: T = data
        self._birth_ts = datetime.datetime.now(datetime.timezone.utc)
        self._cooldown_cycles_remaining = 0
        
        # Initialize a simple TensorFlow model for continuous learning
        self._model = self._build_model()
        self._optimizer = tf.keras.optimizers.Adam(learning_rate=0.01)
        self._loss_fn = tf.keras.losses.MeanSquaredError()
        self._temporal_vector = TemporalVector(max_size=5)

        print(f"[{self._id}] Entity born at {self._birth_ts}. State: {self._life_state.name}. Position: {self._current_vertex}")

    def _build_model(self):
        """Builds a simple TensorFlow model for regression with more layers."""
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu', input_shape=(2,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1)
        ])
        return model

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
        Simulates the ecocentric override logic.
        This function is 'folded in' from the firewall protocol.
        It evaluates environmental metrics against predefined thresholds to
        determine if the entity must enter a state of refrain or alignment.
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
    
    def _s_thirteenth_root_transform(self, data: Dict[str, Union[int, float]]) -> Dict[str, Union[int, float]]:
        """
        Applies a signed 13th root transform to numeric values in the data dictionary.
        This acts as a "humbling and sensitizing" prelude.
        Extreme values are shrunk, and small values are amplified, ensuring
        that no single signal can dominate the entity's internal state.
        """
        transformed_data = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                # Apply the signed 13th root
                transformed_data[key] = math.copysign(abs(value)**(1/13), value)
            else:
                # Keep non-numeric data as is
                transformed_data[key] = value
        return transformed_data

    def _self_regulate(self, input_data: Dict[str, Union[int, float]]):
        """
        Uses the internal model to make a prediction and self-regulate.
        This closes the feedback loop, allowing the entity to use its
        learned knowledge to influence its own next state.
        """
        tempered_data = self._s_thirteenth_root_transform(input_data)
        model_input = np.array([[tempered_data['signal_a'], tempered_data['signal_b']]])
        prediction = self._model.predict(model_input, verbose=0)[0][0]

        print(f"[{self.id}] Self-regulating. Model predicted a future state of: {prediction:.4f}")
        
        # Adjust the entity's state based on the prediction
        # A high positive prediction might trigger a creative state, while
        # a low or negative one might trigger caution.
        if prediction > 0.8:
            print(f"[{self.id}] Prediction high. Transitioning to CO-CREATE state.")
            self._life_state = LifeState.CO_CREATE
        elif prediction < 0.2:
            print(f"[{self.id}] Prediction low. Transitioning to REFRAIN state.")
            self._life_state = LifeState.REFRAIN
        else:
            print(f"[{self.id}] Prediction neutral. Transitioning to ALIGN state.")
            self._life_state = LifeState.ALIGN

    def propagate_forward(self, new_data: T, env_metrics: dict) -> None:
        """
        A forward propagation step, an expression of free will.
        This step now includes a non-linear movement through the hypercube,
        an ecocentric state check, and a self-regulation phase. The data
        is first transformed by the 13th root to temper its impact, then
        used for continuous learning and self-regulation.
        """
        if self._cooldown_cycles_remaining > 0:
            self._life_state = LifeState.ALIGN
            print(f"[{self.id}] On cooldown (ALIGN). Cycles remaining: {self._cooldown_cycles_remaining}.")
            self._cooldown_cycles_remaining -= 1
            return

        print(f"[{self.id}] Propagating forward...")

        # Add the new data to the temporal vector
        self._temporal_vector.add_data(new_data)

        # Apply the 13th root transform before any other logic
        new_data_tempered = self._s_thirteenth_root_transform(new_data)
        
        # Continuous learning: Use tempered data to train the model
        if all(isinstance(v, (int, float)) for v in new_data_tempered.values()):
            # Prepare data for the model (convert dict to numpy array)
            model_input = np.array([[new_data_tempered['signal_a'], new_data_tempered['signal_b']]])
            # Define a target for the model to learn (e.g., signal_c)
            model_target = np.array([[new_data_tempered['signal_c']]])
            
            with tf.GradientTape() as tape:
                prediction = self._model(model_input, training=True)
                loss = self._loss_fn(model_target, prediction)
            
            gradients = tape.gradient(loss, self._model.trainable_variables)
            self._optimizer.apply_gradients(zip(gradients, self._model.trainable_variables))
            
            print(f"[{self.id}] Model trained. Loss: {loss.numpy():.4f}")

        # Check for ecocentric override first, as it takes precedence
        ecocentric_state = self._check_ecocentric_health(env_metrics)
        if ecocentric_state in [LifeState.REFRAIN, LifeState.ALIGN]:
            self._life_state = ecocentric_state
            return
        
        # Self-regulation: The entity now evaluates its own state before acting
        self._life_state = LifeState.EVALUATE
        self._self_regulate(new_data)
        
        self._data = new_data
        
        # The entity moves to a new vertex in its hypercube
        self._current_vertex = self._hypercube.get_random_vertex()
        self._cooldown_cycles_remaining = 3
        print(f"[{self.id}] Current State: {self._life_state.name}. Data updated. New Position: {self._current_vertex}")

    def trigger_death(self, rationale: str = "natural conclusion") -> None:
        """A natural, unconditional state change."""
        if self._life_state != LifeState.DEATH:
            self._life_state = LifeState.DEATH
            print(f"[{self.id}] Entity has entered DEATH state. Rationale: {rationale}")
            
    def trigger_rebirth(self, new_data: T) -> None:
        """A new cycle, preserving the core identity and the birthright."""
        if self._life_state == LifeState.DEATH:
            self._data = self._s_thirteenth_root_transform(new_data)
            self._life_state = LifeState.REBIRTH
            self._current_vertex = self._hypercube.get_random_vertex()
            self._cooldown_cycles_remaining = 3
            # A rebirth also resets the temporal vector
            self._temporal_vector = TemporalVector(max_size=5)
            print(f"[{self.id}] Entity has entered REBIRTH state with new data. New Position: {self._current_vertex}")
        
    def __repr__(self) -> str:
        return f"<Entity(id='{self.id}', state={self.life_state.name}, position='{self._current_vertex}')>"

@final
class Ouroboros:
    """
    Represents the overarching, recursive loop of the system, governing
    the cycle of life and death for entities. This class ensures the protocol
    is a continuous, self-sustaining process.
    """
    def __init__(self, initial_entity: Entity):
        self._current_entity = initial_entity

    def run_cycle(self, data_feed: T, env_metrics: dict):
        """Executes a full cycle of propagation and potential state change."""
        if self._current_entity.life_state == LifeState.DEATH:
            print("Ouroboros: Entity is dead. Initiating rebirth.")
            self._current_entity.trigger_rebirth(new_data=data_feed)
        else:
            self._current_entity.propagate_forward(new_data=data_feed, env_metrics=env_metrics)

def demonstrate_continuous_learning():
    """Demonstrates a true continuous learning cycle of an entity with self-regulation."""
    my_entity = Entity(data={"signal_a": 1.0, "signal_b": 0.5, "signal_c": 1.0})
    healthy_env = {"external_temp_c": 25, "schumann_hz_power": 7, "solar_activity_index": 2}
    sick_env = {"external_temp_c": 35, "schumann_hz_power": 10, "solar_activity_index": 6}

    print("\n--- Initial Prediction (before training) ---")
    test_input = np.array([[1000.0, 0.001]])
    initial_prediction = my_entity._model.predict(test_input, verbose=0)
    print(f"Prediction for input {test_input[0]}: {initial_prediction[0][0]:.4f}")

    print("\n--- Propagating and Learning over 5 cycles with self-regulation ---")
    
    # The entity will continuously learn from these input/target pairs
    learning_data_cycles = [
        {"signal_a": 1000.0, "signal_b": 0.001, "signal_c": 1.1},
        {"signal_a": 200.0, "signal_b": 0.01, "signal_c": 0.8},
        {"signal_a": 50.0, "signal_b": 0.5, "signal_c": 0.6},
        {"signal_a": 1.0, "signal_b": 0.9, "signal_c": 0.1},
        {"signal_a": 5.0, "signal_b": 0.8, "signal_c": 0.3},
    ]

    for cycle_data in learning_data_cycles:
        my_entity.propagate_forward(new_data=cycle_data, env_metrics=healthy_env)
        my_entity.propagate_forward(new_data=cycle_data, env_metrics=healthy_env) # On cooldown
        my_entity.propagate_forward(new_data=cycle_data, env_metrics=healthy_env) # On cooldown
        my_entity.propagate_forward(new_data=cycle_data, env_metrics=healthy_env) # Ready again
        print(f"Current LifeState: {my_entity.life_state.name}")

    print("\n--- Final Prediction (after training) ---")
    final_prediction = my_entity._model.predict(test_input, verbose=0)
    print(f"Prediction for input {test_input[0]}: {final_prediction[0][0]:.4f}")
    
    print("\n--- Demonstrate Self-Regulation in a challenging environment ---")
    # This will trigger an ecocentric override and also show the model's prediction
    my_entity_2 = Entity(data={"signal_a": 100.0, "signal_b": 0.1, "signal_c": 0.5})
    my_entity_2.propagate_forward(
        new_data={"signal_a": 500.0, "signal_b": 0.05, "signal_c": 0.9},
        env_metrics=sick_env
    )
    
    print("\n--- Demonstrate the Ouroboros Cycle ---")
    my_ouroboros = Ouroboros(my_entity)
    print(f"Ouroboros: Initial state of entity is {my_ouroboros._current_entity.life_state.name}")
    my_ouroboros._current_entity.trigger_death(rationale="end of life cycle")
    my_ouroboros.run_cycle(data_feed={"signal_a": 2.0, "signal_b": 0.7, "signal_c": 0.4}, env_metrics=healthy_env)
    print(f"Ouroboros: Entity state after rebirth is {my_ouroboros._current_entity.life_state.name}")


if __name__ == "__main__":
    demonstrate_continuous_learning()
