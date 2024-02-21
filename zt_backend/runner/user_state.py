import threading
import asyncio

class UserState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.component_values = {}
        self.created_components = []
        self.context_globals = {"exec_mode": False}
        self.current_cell_components = []
        self.current_cell_layout = []
        self.cell_outputs_dict = {}
        self.websocket = None
        self.io_output = None
        self.message_queue = asyncio.Queue()
        self.var_state = None

class UserContext:
    _state = threading.local()

    @staticmethod
    def set_state(state: UserState):
        UserContext._state.value = state

    @staticmethod
    def get_state():
        return getattr(UserContext._state, 'value', None)

    def __init__(self, user_state: UserState):
        self.user_state = user_state

    def __enter__(self):
        UserContext.set_state(self.user_state)
        return self.user_state

    def __exit__(self, exc_type, exc_val, exc_tb):
        UserContext.set_state(None)

class State(dict):
    @staticmethod
    def get_or_create_state(*args, **kwargs):
        current_state = UserContext.get_state()
        if current_state is not None and current_state.var_state is not None:
            return current_state.var_state
        else:
            new_state = State(*args, **kwargs)
            if current_state is not None:
                current_state.var_state = new_state
            return new_state

    def __setattr__(self, key, value):
        if key in self:
            super().__setattr__(key, value)
        else:
            raise AttributeError("Cannot add new attributes. Please use dictionary key-value pairs.")

    def __delattr__(self, key):
        if key in self:
            super().__delattr__(key)
        else:
            raise AttributeError("Cannot delete attributes. Please use dictionary operations.")
        
def state():
    return State.get_or_create_state()

global_state = State()