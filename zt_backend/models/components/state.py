from zt_backend.runner.user_state import UserContext 

try:
    state = UserContext.get_state().var_state
except:
    state=None