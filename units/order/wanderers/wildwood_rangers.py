from data import database
from model import Model
from unit import Unit
from weapons import WeaponProfile

UNIT_NAME = "Wildwood Rangers"


class WildwoodRangers(Unit):

    def __init__(self):
        unit_id, unit_name, movement, save, bravery, wounds = database.get_unit_by_name(UNIT_NAME)
        models = {}
        for model_id, unit_id, model_name, model_type in database.get_models_by_unit_id(unit_id):
            profiles = database.get_weapon_profiles_by_model_id(model_id)
            models[model_name] = Model(name=model_name, model_type=model_type, weapons=[])
            for _, _, profile_id in profiles:
                models[model_name].weapons.append(WeaponProfile(*database.get_weapon_profile_by_id(profile_id)))
        super().__init__(
            name=UNIT_NAME,
            movement=movement,
            save=save,
            bravery=bravery,
            wounds=wounds,
            models=models,
            unit_types=database.get_unit_types_by_unit_id(unit_id),
            keywords=database.get_keywords_by_unit_id(unit_id)
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
        self.add_ability(self.guardians_of_the_kindreds)

    # Custom abilities

    def guardians_of_the_kindreds(self, target):
        for profile in self.weapon_profiles.values():
            profile.damage = 2 if 'MONSTER' in target.keywords else 1
