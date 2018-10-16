from enum import Enum


class WeaponProfileTypes(Enum):
    CORE = "Core"
    LEADER = "Leader"
    SPECIAL = "Special"


class WeaponTypes(Enum):
    SHOOTING = "Shooting"
    COMBAT = "Combat"


class WeaponProfile:

    def __init__(self,
                 name,
                 weapon_range,
                 attacks=1,
                 to_hit=4,
                 to_wound=4,
                 rend=0,
                 damage=1):
        self.name = name
        self.weapon_range = weapon_range
        self.weapon_type = WeaponTypes.COMBAT if weapon_range <= 3 else WeaponTypes.SHOOTING
        self.attacks = attacks
        self.to_hit = to_hit
        self.to_wound = to_wound
        self.rend = rend
        self.damage = damage
        self.extra_attacks = 0
        self.bonus_to_hit = 0
        self.bonus_to_wound = 0
