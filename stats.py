import importlib
import pkgutil
import pyclbr
from functools import reduce

import units
from unit import UNITS
from dice import DiceRoller
from weapons import WeaponTypes


def import_units(package):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = importlib.import_module(package)
    for loader, name, is_pkg in pkgutil.walk_packages(path=package.__path__):
        full_name = package.__name__ + '.' + name
        module = importlib.import_module(full_name)
        cls = [_.name for _ in pyclbr.readmodule(full_name).values()]
        if cls:
            # add each unit class to a global units dict
            UNITS[module.UNIT_NAME] = getattr(module, cls[0])
        if is_pkg:
            import_units(full_name)

# import all units
import_units(units)


def to_percentage(die_roll):
    return max(1, min(5, (6 - (die_roll - 1)))) / 6


def chance_to_wound(hits_on, wounds_on):
    return to_percentage(hits_on) * to_percentage(wounds_on)


def average_wounding_hits(attacks, hits_on, wounds_on):
    return attacks * chance_to_wound(hits_on, wounds_on)


def average_damaging_hits(attacks, hits_on, wounds_on, rend, target_save):
    return (average_wounding_hits(attacks, hits_on, wounds_on) *
            (1 - (0 if (target_save + rend) > 6 else to_percentage(target_save + rend))))


def calculate_damage(attacks, hits_on, wounds_on, rend, damage, target_save):
    hits = average_damaging_hits(attacks, hits_on, wounds_on, rend, target_save)
    return (hits * damage if isinstance(damage, int)
            else reduce((lambda x, y: x + damage()), range(round(hits)), 0))


def print_average_shooting_result(attacking_unit, target):
    attacks = attacking_unit.shooting_attacks()
    if attacks:
        print("\nShooting phase:")
    for weapon, profile in attacks:
        damage = calculate_damage(profile.count * profile.attacks + profile.extra_attacks,
                                  profile.to_hit - profile.bonus_to_hit, profile.to_wound, profile.rend,
                                  profile.damage, target.save)
        print("%40s |%30s\" |%30.2f" % (weapon, profile.weapon_range, damage))


def print_average_combat_results(attacking_unit, target):
    attacks = attacking_unit.combat_attacks()
    if attacks:
        print("\nCombat phase:")
    for weapon, profile in attacks:
        damage = calculate_damage(profile.count * profile.attacks + profile.extra_attacks,
                                  profile.to_hit - profile.bonus_to_hit, profile.to_wound, profile.rend,
                                  profile.damage, target.save)
        print("%40s |%30s\" |%30.2f" % (weapon, profile.weapon_range, damage))


def calculate_attacks_vs_target(attacking_unit, target, buff=None):
    attacking_unit.reset_buffs()
    for ability in attacking_unit.abilities:
        ability(attacking_unit, target)
    print("Attacks for %s against %s (%d+ save)" % (attacking_unit.name, target.name, target.save))
    if buff:
        print(" with %s" % buff[0])
        buff[1](attacking_unit, target)
    print("\n%40s |%31s |%30s" % ("Weapon", "Range", "Average damage"))
    print_average_shooting_result(attacking_unit, target)
    print_average_combat_results(attacking_unit, target)
    print("\n")


def calculate_attacks_vs_targets(attacking_unit, targets):
    for target in targets:
        calculate_attacks_vs_target(attacking_unit, target)
        for buff_name, buff in attacking_unit.buffs.items():
            calculate_attacks_vs_target(attacking_unit, target, (buff_name, buff))
    print("%s\n" % ("-" * 105))


def simulate_damage(attacks, hits_on, wounds_on, rend, damage, target_save):
    roll_to_hit = DiceRoller.roll(attacks)  # TODO: re-rolls
    print("Rolled %s, needs %s to hit" % (roll_to_hit, hits_on))
    roll_to_wound = DiceRoller.roll(len([_ for _ in filter(lambda x: x >= hits_on, roll_to_hit)]))
    print("Rolled %s, needs %s to wound" % (roll_to_wound, wounds_on))
    roll_to_save = DiceRoller.roll(len([_ for _ in filter(lambda x: x >= wounds_on, roll_to_wound)]))
    print("Rolled %s, saves on %s+ (after rend)\n" % (roll_to_save, target_save + rend))
    wounding_hits = len([_ for _ in filter(lambda x: x < target_save + rend, roll_to_save)])
    return (wounding_hits * damage if isinstance(damage, int)
            else reduce(lambda x, y: x + damage(), range(wounding_hits), 0))


def simulate_attack(attacking_unit, defending_unit, distance, weapon_type=WeaponTypes.COMBAT):
    total_damage = 0
    for model, count in attacking_unit.models_remaining.items():
        if count <= 0:
            continue
        for weapon in model.weapons:
            if weapon.weapon_type == weapon_type and weapon.weapon_range >= distance:
                attacks = weapon.attacks if type(weapon.attacks) is int else weapon.attacks()
                damage = simulate_damage(count * attacks + weapon.extra_attacks,
                                         weapon.to_hit - weapon.bonus_to_hit,
                                         weapon.to_wound - weapon.bonus_to_wound,
                                         weapon.rend, weapon.damage, defending_unit.save)
                print("%s inflicts %d wounds with %s\n" % (attacking_unit.name, damage, weapon.name))
                total_damage += damage
    return total_damage


def battleshock(unit, models_lost):
    battleshock_test = models_lost + DiceRoller.d6()
    if unit.bravery < battleshock_test:
        fleeing_units = min(battleshock_test - unit.bravery, unit.remaining_models())
        print('%d %s models flee!\n' % (fleeing_units, unit.name))
        unit.flee(fleeing_units)


# TODO: add flag to remove output (switch to logging?)
def simulate_combat(attacking_unit, defending_unit, distance=3):
    # returns the victorious unit object
    attacking_unit_models_lost = defending_unit_models_lost = 0

    if distance > 3:
        distance = max(distance - attacking_unit.movement, 3)

    print("%s's shooting phase:\n" % attacking_unit.name)
    wounds = simulate_attack(attacking_unit, defending_unit, distance, WeaponTypes.SHOOTING)
    defending_unit.assign_wounds(wounds)
    defending_unit_models_lost += wounds

    if defending_unit.remaining_models() <= 0:
        print("%s was slain!" % defending_unit.name)
        return attacking_unit

    # FIXME: units should have a charge distance value defaulting to 12 (Judicators etc.)
    # XXX: this could potentially also be implemented as a constant and units could have a run/charge bonus field
    if distance in range(3, 13):  # range is exclusive
        charge_roll = sum(DiceRoller.roll(2))
        print("Charge roll: %d" % charge_roll)
        if charge_roll >= distance:
            distance = 0  # Effective 0 distance post-charge
            print("%s's charge succeeded!" % attacking_unit.name)
        else:
            print("%s's charge failed!" % attacking_unit.name)

    if distance < 3:
        print("\n%s's combat phase:\n" % attacking_unit.name)
        wounds = simulate_attack(attacking_unit, defending_unit, distance)
        defending_unit.assign_wounds(wounds)
        defending_unit_models_lost += wounds

        if defending_unit.remaining_models() <= 0:
            print("%s was slain!" % defending_unit.name)
            return attacking_unit

        wounds = simulate_attack(defending_unit, attacking_unit, distance)
        attacking_unit.assign_wounds(wounds)
        attacking_unit_models_lost += wounds

        if attacking_unit.remaining_models() <= 0:
            print("%s was slain!" % attacking_unit.name)
            return defending_unit

    print("Battleshock phase:\n")
    if defending_unit_models_lost > 0:
        battleshock(defending_unit, defending_unit_models_lost)

    if defending_unit.remaining_models() <= 0:
        print("%s was slain!" % defending_unit.name)
        return attacking_unit

    if attacking_unit_models_lost > 0:
        battleshock(attacking_unit, attacking_unit_models_lost)

    if attacking_unit.remaining_models() <= 0:
        print("%s was slain!" % attacking_unit.name)
        return defending_unit

    print("\n%s\n" % ("-" * 105))
    return simulate_combat(defending_unit, attacking_unit, distance=distance)


ATTACKER = 'attacker'
DEFENDER = 'defender'


def run_simulation(attacking_unit, defending_unit, simulations_to_run=100, distance=10):
    results = {ATTACKER: 0, DEFENDER: 0}
    for n in range(1, simulations_to_run + 1):
        print("\n%s\n" % ("#" * 105))
        print("SIMULATION %d" % n)
        print("\n%s\n" % ("#" * 105))
        winning_unit = simulate_combat(attacking_unit, defending_unit, distance)
        results[(ATTACKER if winning_unit == attacking_unit else DEFENDER)] += 1
        attacking_unit.reset()
        defending_unit.reset()
    print("\n%s\n" % ("#" * 105))
    print("Simulated %d battles between %d %s and %d %s." %
          (simulations_to_run, attacking_unit.remaining_models(), attacking_unit.name,
           defending_unit.remaining_models(), defending_unit.name))
    print("%s had the initiative at a distance of %d inches" % (attacking_unit.name, distance))
    print("%s won %d times, %s won %d times." %
          (attacking_unit.name, results[ATTACKER], defending_unit.name, results[DEFENDER]))
    print("\n%s\n" % ("#" * 105))


def run():
    # Glade guard
    def peerless_archery(self, target):
        if self.remaining_models() >= 20:
            for profile in self.shooting_attacks():
                profile.to_hit -= 1

    def bodkin_arrows(self, target):
        for profile in self.shooting_attacks():
            profile.rend = 3

    # TODO: Khemist
    def aetheric_augmentation(self, target):
        for name, profile in self.weapon_profiles.items():
            profile.extra_attacks += profile.count

    # Rat Ogors
    # TODO: represent on-charge conditional
    def rabid_fury(self, target):
        weapon_profile = self.weapon_profiles["Tearing Claws, Blades, and Fangs"]
        weapon_profile.extra_attacks = (self.remaining_models() * weapon_profile.attacks *
                                        (0 if (6 - weapon_profile.bonus_to_hit) > 6
                                         else to_percentage(6 - weapon_profile.bonus_to_hit)))

    def herded_into_the_fray(self, target):
        self.weapon_profiles["Tearing Claws, Blades, and Fangs"].bonus_to_hit = 2

    # for unit in attacking_group:
    #     calculate_attacks_vs_targets(unit, target_group)

    attacking_unit_cls = UNITS['Arkanaut Company']
    defending_unit_cls = UNITS['Wildwood Rangers']
    attacking_unit = attacking_unit_cls()
    # TODO: implement maximums for models <-----
    # FIXME: models are singletons (sortof) so we need a way of having weapon profile instances
    # FIXME: need a much better way of accessing model types...
    attacking_unit.add_models('Arkanaut', 6)
    attacking_unit.add_models('Arkanaut with Light Skyhook', 3)
    attacking_unit.add_models('Arkanaut Captain', 1)

    defending_unit = defending_unit_cls()
    defending_unit.add_models('Ranger', 9)
    defending_unit.add_models('Warden', 1)

    '''
    print("Unit list")
    for unit_name, unit_class in UNITS.items():
        print("%s" % unit_name)
    attacking_unit = UNITS[input("Select an attacking unit: ")]()
    defending_unit = UNITS[input("Select a defending unit: ")]()
    simulations = int(input("Enter the number of iterations to run: "))
    distance = int(input("Enter a distance to start at: "))
    '''

    run_simulation(
        attacking_unit=attacking_unit,
        defending_unit=defending_unit,
        simulations_to_run=10,  # simulations,
        distance=10,  # distance
    )


if __name__ == "__main__":
    run()
