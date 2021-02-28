from functools import wraps

def TryExceptRetNone(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            return func(*args,**kwargs)
        except:
            return None
    return wrapper