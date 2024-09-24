from threading import Timer
import asyncio

def debounce(wait):
    """ Decorator that will postpone a functions
        execution until after wait seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        def debounced(*args, **kwargs):
            def call_it():
                fn(*args, **kwargs)
            try:
                debounced.t.cancel()
            except(AttributeError):
                pass
            debounced.t = Timer(wait, call_it)
            debounced.t.start()
        return debounced
    return decorator


def async_debounce(wait):
    """Decorator that postpones an async function's execution until after `wait` seconds have elapsed since the last time it was invoked."""
    def decorator(fn):
        current_task = None

        async def debounced(*args, **kwargs):
            nonlocal current_task

            # Cancel the previous task if it exists and is not done
            if current_task is not None and not current_task.done():
                current_task.cancel()

            async def wait_and_invoke():
                await asyncio.sleep(wait)  # Delay execution
                await fn(*args, **kwargs)  # Invoke the async function

            # Schedule the new task
            current_task = asyncio.create_task(wait_and_invoke())

        return debounced
    return decorator