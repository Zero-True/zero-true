class state(dict):
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

    # Optional: Override __setitem__ and __delitem__ to refine dict behavior
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def __delitem__(self, key):
        super().__delitem__(key)

State = state()