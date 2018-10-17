import abc

from enum import Enum
from functools import reduce
from uuid import uuid4 as uuid

UNITS = {}  # Global dictionary to hold all unit names + classes


class UnitTypes(Enum):
    BATTLELINE = "Battleline"
    LEADER = "Leader"
    BEHEMOTH = "Behemoth"
    ARTILLERY = "Artillery"


class Unit:

    __metaclass__ = abc.ABCMeta

    def __init__(self, name, movement, save, bravery, wounds, models, unit_types=None, keywords=None):
        # TODO: implement damage tables
        self.name = name
        self.id = uuid()
        self.movement = movement
        self.bravery = bravery
        self.wounds = wounds
        self.save = save
        self.models = models
        self.unit_types = unit_types or []
        self.keywords = keywords or []
        self.model_counts = {}  # FIXME: there should be a better way to set the base count for models initially
        self.models_remaining = {}
        self.wounds_remaining = 0
        self.abilities = []
        self.buffs = {}
        self.weapon_profiles = reduce(lambda x, y: x + y.weapons, self.models.values(), [])
        self.init_abilities()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def add_ability(self, fn):
        self.abilities.append(fn)

    def add_buff(self, name, fn):
        self.buffs[name] = fn

    def add_models(self, model, count=1):
        if model not in self.models:
            raise NoSuchModelException()
        # Use the model object here rather than the string key for simplicity
        # FIXME: is there a better way to handle this?
        model = self.models[model]
        if model in self.model_counts:
            self.model_counts[model] += count
            self.models_remaining[model] += count
        else:
            self.model_counts[model] = count
            self.models_remaining[model] = count
        # FIXME: are there individual models in a unit with additional wounds?
        self.wounds_remaining += self.wounds * count

    def reset_buffs(self):
        # TODO: these should be stored elsewhere as the profile is shared between instances of a unit
        for weapon_profile in self.weapon_profiles:
            weapon_profile.extra_attacks = 0
            weapon_profile.bonus_to_hit = 0
            weapon_profile.bonus_to_wound = 0

    def reset(self):
        self.reset_buffs()
        self.models_remaining = self.model_counts.copy()
        self.wounds_remaining = self.remaining_models() * self.wounds

    def assign_wounds(self, damage):
        models_slain, spill = divmod(damage, self.wounds)
        self.remove_models(models_slain)
        self.wounds_remaining -= spill
        if self.wounds_remaining <= 0:
            self.remove_models(1)
            # Allocate remaining wounds and account for overkill
            self.wounds_remaining = self.wounds + self.wounds_remaining

    def remaining_models(self):
        return sum(self.models_remaining.values())

    @abc.abstractmethod
    def init_abilities(self):
        pass

    @abc.abstractmethod
    def remove_models(self, models_slain):
        pass


# Custom exception classes
class NoSuchModelException(Exception):
    pass
