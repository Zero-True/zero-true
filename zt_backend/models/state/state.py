from zt_backend.models.state.user_state import UserContext

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