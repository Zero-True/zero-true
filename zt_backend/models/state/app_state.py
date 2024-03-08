from zt_backend.config import settings
from zt_backend.models.state.user_state import UserState
import asyncio
import logging
import traceback
import threading

logger = logging.getLogger("__name__")

class AppState:
    def __init__(self):
        self.user_states={}
        self.user_timers={}
        self.user_threads={}
        self.user_message_tasks={}
        self.current_thread=None
        self.notebook_state=UserState('')
        self.run_mode = settings.run_mode
        self.save_queue = asyncio.Queue()

    def stop_execution(self, data):
        if self.run_mode=='dev' and self.current_thread:
            self.current_thread.kill()
            self.notebook_state.current_cell_components.clear()
            self.notebook_state.current_cell_layout.clear()
            self.notebook_state.component_values.clear()
            self.notebook_state.created_components.clear()
            self.notebook_state.context_globals['exec_mode'] = False
        if self.run_mode=='app' and self.user_threads[data]:
            self.user_threads[data].kill()
            self.user_states[data].current_cell_components.clear()
            self.user_states[data].current_cell_layout.clear()
            self.user_states[data].component_values.clear()
            self.user_states[data].created_components.clear()
            self.user_states[data].context_globals['exec_mode'] = False

    def remove_user_state(self, user_id):
        try:
            if user_id in self.user_timers:
                # Cancel and remove the associated timer
                timer = self.user_timers[user_id]
                message_sender = self.user_message_tasks[user_id]
                if timer:
                    timer.cancel()
                del self.user_timers[user_id]
                if message_sender:
                    message_sender.cancel() 
                del self.user_message_tasks[user_id]
                if user_id in self.user_states: del self.user_states[user_id]
                logger.debug("User state removed for user %s", user_id)
        except Exception as e:
            logger.error("Error removing user state for user %s: %s", user_id, traceback.format_exc())

    def timer_set(self, user_id, timeout_seconds):
        logger.debug("Starting timer for user %s", user_id)
        if user_id in self.user_timers:
            existing_timer = self.user_timers[user_id]
            if existing_timer:
                existing_timer.cancel()
            
            timer = threading.Timer(timeout_seconds, self.remove_user_state, args=(user_id,))
            timer.daemon=True
            timer.start()
            
            self.user_timers[user_id] = timer

    def shutdown(self):
        if self.current_thread:
            self.current_thread.kill()
        for user_id in self.user_threads:
            if self.user_threads[user_id]:
                self.user_threads[user_id].kill()
        for user_id in self.user_timers:
            if self.user_timers[user_id]:
                self.user_timers[user_id].cancel()
        for user_id in self.user_message_tasks:
            if self.user_message_tasks[user_id]:
                self.user_message_tasks[user_id].cancel()