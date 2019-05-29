import functools


def lazyprop(func):
    """
    Decorator for properties that calculate their value
    the first time and then return the cached value after that.
    See `<https://stackoverflow.com/questions/3012421/>`_
    """
    attr_name = "_lazy_" + func.__name__

    @property
    @functools.wraps(func)
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return _lazyprop
