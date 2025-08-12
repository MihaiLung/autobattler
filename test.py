from dataclasses import dataclass, fields

@dataclass
class Tracker:
    def __add__(self, other):
        if not isinstance(other, Tracker):
            return NotImplemented

        # Create a dictionary to hold the results
        new_values = {}

        # Iterate over the fields to perform addition
        for field in fields(self):
            attr_name = field.name
            new_values[attr_name] = getattr(self, attr_name) + getattr(other, attr_name)

        return type(self)(**new_values)

    def __sub__(self, other):
        if not isinstance(other, Tracker):
            return NotImplemented

        # Create a dictionary to hold the results
        new_values = {}

        # Iterate over the fields to perform addition
        for field in fields(self):
            attr_name = field.name
            new_values[attr_name] = getattr(self, attr_name) - getattr(other, attr_name)

        return type(self)(**new_values)

    def __mul__(self, other: float):

        # Create a dictionary to hold the results
        new_values = {}

        # Iterate over the fields to perform addition
        for field in fields(self):
            attr_name = field.name
            new_values[attr_name] = getattr(self, attr_name)*other

        return type(self)(**new_values)

    def __rmul__(self, other: float):
        return self.__mul__(other)
