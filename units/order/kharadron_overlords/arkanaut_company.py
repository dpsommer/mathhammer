from unit import Unit

UNIT_NAME = "Arkanaut Company"


class ArkanautCompany(Unit):

    def __init__(self):
        super().__init__(name=UNIT_NAME)

    # Custom abilities

    def glory_seekers(self, target):
        for profile in self.weapon_profiles:
            if 'HERO' in target.keywords or 'MONSTER' in target.keywords:
                profile.to_hit -= 1

    # Inherited methods

    def init_abilities(self):
        self.add_ability(self.glory_seekers)
