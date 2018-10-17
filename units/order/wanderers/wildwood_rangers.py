from unit import Unit

UNIT_NAME = "Wildwood Rangers"


class WildwoodRangers(Unit):

    def __init__(self):
        super().__init__(name=UNIT_NAME)

    # Custom abilities

    def guardians_of_the_kindreds(self, target):
        for profile in self.weapon_profiles.values():
            profile.damage = 2 if 'MONSTER' in target.keywords else 1

    # Inherited methods

    def init_abilities(self):
        self.add_ability(self.guardians_of_the_kindreds)
