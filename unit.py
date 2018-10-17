import abc
from enum import Enum
from functools import reduce
from uuid import uuid4 as uuid

from data import database
from model import Model
from weapons import WeaponProfile

UNITS = {}  # Global dictionary to hold all unit names + classes


class UnitTypes(Enum):
    BATTLELINE = "Battleline"
    LEADER = "Leader"
    BEHEMOTH = "Behemoth"
    ARTILLERY = "Artillery"


class Unit:

    __metaclass__ = abc.ABCMeta

    DEFAULT_CHARGE_DISTANCE = 12
    DEFAULT_PILE_IN_DISTANCE = 3

    def __init__(self, name):
        unit_id, unit_name, movement, save, bravery, wounds = database.get_unit_by_name(name)
        models = {}
        for model_id, unit_id, model_name, model_type in database.get_models_by_unit_id(unit_id):
            profiles = database.get_weapon_profiles_by_model_id(model_id)
            models[model_name] = Model(name=model_name, model_type=model_type, weapons=[])
            for _, _, profile_id in profiles:
                models[model_name].weapons.append(WeaponProfile(*database.get_weapon_profile_by_id(profile_id)))

        # TODO: implement damage tables
        self.name = name
        self.id = uuid()
        self.movement = movement
        self.bravery = bravery
        self.wounds = wounds
        self.save = save
        self.models = models
        self.unit_types = database.get_unit_types_by_unit_id(unit_id)
        self.keywords = database.get_keywords_by_unit_id(unit_id)
        self.model_counts = {}  # FIXME: there should be a better way to set the base count for models initially
        self.models_remaining = {}
        self.wounds_remaining = 0
        self.charge_distance = Unit.DEFAULT_CHARGE_DISTANCE
        self.pile_in_distance = Unit.DEFAULT_PILE_IN_DISTANCE
        self.in_combat = False
        self.immune_to_battleshock = False
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
        self.wounds_remaining = self.wounds
        self.charge_distance = Unit.DEFAULT_CHARGE_DISTANCE
        self.immune_to_battleshock = False

    def assign_wounds(self, damage):
        models_slain, spill = divmod(damage, self.wounds)
        self.remove_models(models_slain)
        self.wounds_remaining -= spill
        if self.wounds_remaining <= 0:
            self.remove_models(1)
            # Allocate remaining wounds and account for overkill
            self.wounds_remaining = self.wounds + self.wounds_remaining

    def flee(self, fleeing_models):
        self.remove_models(fleeing_models)
        self.wounds_remaining = self.wounds

    def remaining_models(self):
        return sum(self.models_remaining.values())

    def remove_models(self, models_slain):
        for _ in range(models_slain):
            model_to_remove = None
            for model, count in self.models_remaining.items():
                if count <= 0:
                    continue
                # Remove base models first, then special models, then unit leaders
                if (model_to_remove is None or model.type == Model.BASE_TYPE
                        or (model_to_remove.type == Model.LEADER_TYPE and model.type == Model.SPECIAL_TYPE)):
                    model_to_remove = model
            if model_to_remove:
                self.models_remaining[model_to_remove] -= 1

    @abc.abstractmethod
    def init_abilities(self):
        pass


# Custom exception classes
class NoSuchModelException(Exception):
    pass
