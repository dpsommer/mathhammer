from uuid import uuid4 as uuid


class Player:

    def __init__(self, name):
        self.id = uuid()
        self.name = name

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id
