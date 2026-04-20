from django.db import close_old_connections
from functools import wraps
from asgiref.sync import sync_to_async

def db_auto_cleanup(func):
    """
    Decorator to ensure Django database connections are cleaned up 
    before and after a function execution. Useful for functions 
    running in worker threads (via sync_to_async).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        close_old_connections()
        try:
            return func(*args, **kwargs)
        finally:
            close_old_connections()
    return wrapper

def sync_db_to_async(func, thread_sensitive=True):
    """
    Wrapper around sync_to_async that also applies db_auto_cleanup.
    """
    return sync_to_async(db_auto_cleanup(func), thread_sensitive=thread_sensitive)


