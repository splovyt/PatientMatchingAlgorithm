"""
Thread-safety:
    __init__ methods will not be locked.
    An unfinished init will not be a problem since the language spec says
    it is run before the instance is returned to the caller.
    All else will be made thread-safe with simple locks if it can be modified.
    If a new method is added, appropriate locking will have to be added.
    Optimizing might be possible with read-write locks.
"""
