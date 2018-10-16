from data import database
from model import Model
from unit import Unit, UnitTypes, UNITS
from weapons import WeaponProfile

UNIT_NAME = "Wildwood Rangers"


class WildwoodRangers(Unit):

    def __init__(self):
        # TODO: linkages for unit types, keywords
        unit_id, unit_name, movement, save, bravery, wounds = database.get_unit_by_name(UNIT_NAME)
        models = {}
        for model_id, unit_id, model_name, model_type in database.get_models_by_unit_id(unit_id):
            profiles = database.get_weapon_profiles_by_model_id(model_id)
            models[model_name] = Model(name=model_name, model_type=model_type, weapons=[])
            for _, _, profile_id in profiles:
                weapon_name, weapon_range, attacks, to_hit, to_wound, rend, damage = \
                    database.get_weapon_profile_by_id(profile_id)
                models[model_name].weapons.append(
                    WeaponProfile(
                        name=weapon_name,
                        weapon_range=weapon_range,
                        attacks=attacks,
                        to_hit=to_hit,
                        to_wound=to_wound,
                        rend=rend,
                        damage=damage
                    )
                )
        super(WildwoodRangers, self).__init__(
            name=UNIT_NAME,
            movement=movement,
            save=save,
            bravery=bravery,
            wounds=wounds,
            models=models,
            unit_types=[
                UnitTypes.BATTLELINE
            ]
        )

    # Inherited methods

    def remove_models(self, models_slain):
        for _ in range(models_slain):
            model_to_remove = None
            for model, count in self.models_remaining.items():
                if count <= 0:
                    continue
                # Remove base models first, then special models, then unit leaders
                if (model_to_remove is None or model.type is Model.BASE_TYPE
                        or (model_to_remove.type is Model.LEADER_TYPE and model.type is Model.SPECIAL_TYPE)):
                    model_to_remove = model
            if model_to_remove:
                self.models_remaining[model_to_remove] -= 1

    def init_abilities(self):
        pass

    # Custom abilities

UNITS[UNIT_NAME] = WildwoodRangers
