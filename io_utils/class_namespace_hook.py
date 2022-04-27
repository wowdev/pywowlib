class AnnotationsHook(dict):
    """ Dict derivative to be used in metaclasses to hook the creation of __annotations__ dictionary. """
    def __init__(self, other: dict):
        self.specials_counter: int = 0
        super().__init__(other)

    def __setitem__(self, key, value):
        if key != '_':
            super().__setitem__(key, value)
            return

        # handle special layout variables
        new_key = f"_struct_spec_var_{self.specials_counter}"
        print(new_key)
        self.specials_counter += 1

        super().__setitem__(new_key, value)


class NameSpaceHook(dict):
    """ Dict derivative tgo be used in metaclasses to hook the creation of __dict__ dictionary. """
    def __setitem__(self, key, value):
        val = AnnotationsHook(value) if key == '__annotations__' else value
        super().__setitem__(key, val)

