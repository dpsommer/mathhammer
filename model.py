from uuid import uuid4 as uuid


class Model:

    BASE_TYPE = 'Base'
    LEADER_TYPE = 'Leader'
    SPECIAL_TYPE = 'Special'

    def __init__(self, name, weapons=None, model_type=BASE_TYPE):
        self.id = uuid()
        self.name = name
        self.type = model_type
        self.weapons = weapons or []

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def add_weapon(self, weapon):
        self.weapons.append(weapon)
