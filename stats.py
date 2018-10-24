import math
from copy import deepcopy
from enum import Enum
from functools import reduce
from itertools import cycle
from random import choice, randint

from unit import Unit
from dice import DiceRoller
from weapons import WeaponTypes


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
    for model, count in attacking_unit.models_remaining.items():
        for weapon in model.weapons:
            if weapon.weapon_type == WeaponTypes.SHOOTING:
                # FIXME: attacks should be averaged (if a weapon has d6 attacks, for example)
                attacks = weapon.attacks if type(weapon.attacks) is int else weapon.attacks()
                damage = calculate_damage(count * attacks + weapon.extra_attacks,
                                          weapon.to_hit - weapon.bonus_to_hit,
                                          weapon.to_wound - weapon.bonus_to_wound,
                                          weapon.rend, weapon.damage, target.save)
                print("%40s |%30s\" |%30.2f" % (weapon.name, weapon.weapon_range, damage))


def print_average_combat_results(attacking_unit, target):
    for model, count in attacking_unit.models_remaining.items():
        for weapon in model.weapons:
            if weapon.weapon_type == WeaponTypes.COMBAT:
                # FIXME: attacks should be averaged (if a weapon has d6 attacks, for example)
                attacks = weapon.attacks if type(weapon.attacks) is int else weapon.attacks()
                damage = calculate_damage(count * attacks + weapon.extra_attacks,
                                          weapon.to_hit - weapon.bonus_to_hit,
                                          weapon.to_wound - weapon.bonus_to_wound,
                                          weapon.rend, weapon.damage, target.save)
                print("%40s |%30s\" |%30.2f" % (weapon.name, weapon.weapon_range, damage))


def calculate_attacks_vs_target(attacking_unit, target, buff=None):
    attacking_unit.reset_buffs()
    for ability in attacking_unit.abilities:
        ability(target)
    print("Attacks for %s against %s (%d+ save)" % (attacking_unit.name, target.name, target.save))
    if buff:
        print(" with %s" % buff[0])
        buff[1](target)
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


# XXX: should this be in its own class?
class Point:

    def __init__(self, x=0., y=0.):
        self.x = x
        self.y = y

    def calculate_distance(self, p):
        dx = abs(self.x - p.x)
        dy = abs(self.y - p.y)
        return math.sqrt(pow(dx, 2) + pow(dy, 2))

FINAL_BATTLE_ROUND = 5
DEFAULT_VICTORY_POINT_RADIUS = 6


class Simulation:

    class _Phases(Enum):
        HERO = 'hero'
        MOVEMENT = 'movement'
        SHOOTING = 'shooting'
        CHARGE = 'charge'
        COMBAT = 'combat'
        BATTLESHOCK = 'battleshock'
        END = 'end'

    # FIXME: starting player should be determined based on setup
    def __init__(self, p1, p2, units_p1, units_p2, randomize_starting_player=True):
        self.battle_round = 1
        self.turn = 1
        self.active_player = p1
        if randomize_starting_player:
            self.active_player = choice([p1, p2])
        self.defending_player = p2 if self.active_player == p1 else p1
        self.phases = cycle(self._Phases)
        self.current_phase = next(self.phases)
        self.units = {p1: units_p1, p2: units_p2}
        self.remaining_units = deepcopy(self.units)
        all_units = units_p1 + units_p2
        self.models_lost = {unit: 0 for unit in all_units}
        self.locations = {unit: Point() for unit in all_units}
        self.table = Point(48, 72)  # FIXME
        self.victory_points = []
        self.victory_point_radius = DEFAULT_VICTORY_POINT_RADIUS
        self.victory_point_totals = {p1: 0, p2: 0}
        self.setup()

    def setup(self):
        # FIXME: this is a hack for testing
        for unit in self.units[self.active_player]:
            self.setup_unit(unit, Point(randint(0, self.table.x), randint(0, self.table.y / 2 - 9)))
        for unit in self.units[self.defending_player]:
            self.setup_unit(unit, Point(randint(0, self.table.x), randint(self.table.y / 2 + 9, self.table.y)))

    def setup_unit(self, unit, p):
        self.locations[unit] = p

    def reset(self):
        self.battle_round = 1
        self.turn = 1
        self.remaining_units = deepcopy(self.units)
        all_units = self.units[self.active_player] + self.units[self.defending_player]
        self.models_lost = {unit: 0 for unit in all_units}
        self.phases = cycle(self._Phases)
        self.current_phase = next(self.phases)
        self.victory_point_totals = {self.active_player: 0, self.defending_player: 0}
        self.setup()

    def simulate_damage(self, attacks, hits_on, wounds_on, rend, damage, target_save):
        roll_to_hit = DiceRoller.roll(attacks)  # TODO: re-rolls
        roll_to_wound = DiceRoller.roll(len([_ for _ in filter(lambda x: x >= hits_on, roll_to_hit)]))
        roll_to_save = DiceRoller.roll(len([_ for _ in filter(lambda x: x >= wounds_on, roll_to_wound)]))
        # print("Rolled %s, needs %s to hit" % (roll_to_hit, hits_on))
        # print("Rolled %s, needs %s to wound" % (roll_to_wound, wounds_on))
        # print("Rolled %s, saves on %s+ (after rend)\n" % (roll_to_save, target_save + rend))
        wounding_hits = len([_ for _ in filter(lambda x: x < target_save + rend, roll_to_save)])
        return (wounding_hits * damage if isinstance(damage, int)
                else reduce(lambda x, y: x + damage(), range(wounding_hits), 0))

    def simulate_attack(self, unit, target, weapon_type=WeaponTypes.COMBAT):
        total_damage = 0
        distance = self.locations[unit].calculate_distance(self.locations[target])
        for model, count in unit.models_remaining.items():
            if count <= 0:
                continue
            for weapon in model.weapons:
                if weapon.weapon_type == weapon_type and weapon.weapon_range >= distance:
                    attacks = weapon.attacks if type(weapon.attacks) is int else weapon.attacks()
                    damage = self.simulate_damage(count * attacks + weapon.extra_attacks,
                                                  weapon.to_hit - weapon.bonus_to_hit,
                                                  weapon.to_wound - weapon.bonus_to_wound,
                                                  weapon.rend, weapon.damage, target.save)
                    print("%s inflicts %d wounds with %s" % (unit.name, damage, weapon.name))
                    total_damage += damage
        return total_damage

    def hero_phase(self):
        pass  # TODO

    def movement_phase(self):
        # TODO: need to implement behaviours and refactor this
        for unit in self.remaining_units[self.active_player]:
            if unit.in_combat:
                continue  # TODO: retreating
            target = self.choose_target(unit, self.defending_player)
            # FIXME: hack for testing
            if self.locations[unit].calculate_distance(self.locations[target]) > Unit.DEFAULT_PILE_IN_DISTANCE:
                self.move_towards(unit, self.choose_target(unit, self.defending_player))

    def move_towards(self, unit, target):
        # FIXME: grid-based locations may not be good enough here...
        # naively move in a straight line the maximum allowed distance towards the target
        # FIXME: implement some logic here...
        unit_location = self.locations[unit]
        target_location = self.locations[target]
        # get the maximum allowed movement distance towards the target
        d = self.locations[unit].calculate_distance(self.locations[target])
        # TODO: implement running
        movement = min(unit.movement, d - Unit.DEFAULT_PILE_IN_DISTANCE)
        # the ratio of the distance to the target and the allowed movement in a straight line
        # will be the same as the ratio of movement in the x and y directions
        ratio = d / movement
        dx = (target_location.x - unit_location.x) / ratio
        dy = (target_location.y - unit_location.y) / ratio
        new_location = Point(unit_location.x + dx, unit_location.y + dy)
        self.locations[unit] = new_location

    def shooting_phase(self):
        print("%s's shooting phase:\n" % self.active_player.name)
        for unit in self.remaining_units[self.active_player]:
            target = self.choose_target(unit, self.defending_player)
            wounds = self.simulate_attack(unit, target, WeaponTypes.SHOOTING)
            target.assign_wounds(wounds)
            self.models_lost[target] += wounds
            self.determine_casualties()

    def determine_casualties(self):
        for player, units in self.remaining_units.items():
            for unit in units:
                if unit.remaining_models() <= 0:
                    print("%s was slain!" % unit.name)
                    self.remaining_units[player].remove(unit)
                    if not self.remaining_units[player]:
                        pass  # TODO

    def choose_target(self, unit, target_player):
        # FIXME: need to implement behaviours and refactor
        # TODO: target selection for shooting, charging, and combat
        return self.remaining_units[target_player][0]

    def charge_phase(self):
        for unit in self.remaining_units[self.active_player]:
            if unit.in_combat:
                continue
            target = self.choose_target(unit, self.defending_player)
            distance = self.locations[unit].calculate_distance(self.locations[target])
            if math.ceil(distance) in range(3, unit.charge_distance + 1):  # add 1 because range is exclusive
                # TODO: on-charge buffs
                charge_roll = sum(DiceRoller.roll(2))
                print("Charge roll: %d" % charge_roll)
                if charge_roll >= distance:
                    self.locations[unit] = self.locations[target]  # effective 0 distance post-charge
                    unit.in_combat = True
                    target.in_combat = True
                    print("%s's charge succeeded!" % unit.name)
                else:
                    print("%s's charge failed!" % unit.name)

    def combat_phase(self):
        print("\n%s's combat phase:\n" % self.active_player.name)
        units_in_combat = {self.active_player: [], self.defending_player: []}

        for player, units in self.remaining_units.items():
            for unit in units:
                if unit.in_combat:
                    units_in_combat[player].append(unit)

        attacking_player = self.active_player
        defending_player = self.defending_player
        for _ in range(len(units_in_combat[self.active_player] + units_in_combat[self.defending_player])):
            attacking_unit = self.combat_priority(units_in_combat[attacking_player])
            if attacking_unit and units_in_combat[self.defending_player]:
                target = self.choose_target(attacking_unit, defending_player)
                wounds = self.simulate_attack(attacking_unit, target)
                target.assign_wounds(wounds)
                self.models_lost[target] += wounds
                self.determine_casualties()
            attacking_player, defending_player = defending_player, attacking_player

    def combat_priority(self, units):
        # FIXME: implement prioritization algorithm
        return units[0] if units else None

    def battleshock_phase(self):
        print("\nBattleshock phase:\n")
        self.current_phase = self._Phases.BATTLESHOCK
        for player, units in self.remaining_units.items():
            for unit in units:
                models_lost = self.models_lost[unit]
                if models_lost > 0 and not unit.immune_to_battleshock:
                    self.calculate_battleshock(unit, models_lost)

    def calculate_battleshock(self, unit, models_lost):
        battleshock_test = models_lost + DiceRoller.d6()
        if unit.bravery < battleshock_test:
            fleeing_units = min(battleshock_test - unit.bravery, unit.remaining_models())
            print('%d %s models flee!\n' % (fleeing_units, unit.name))
            unit.flee(fleeing_units)
            self.models_lost[unit] += fleeing_units  # in case battleshock is triggered again somehow
            self.determine_casualties()

    def end_phase(self):
        for p in self.victory_points:  # TODO: victory point values and custom battleplans
            nearby_units = self.determine_nearby_units(p)
            model_count = {self.active_player: 0, self.defending_player: 0}
            for player, units in nearby_units.items():
                for unit in units:
                    model_count[player] += unit.remaining_models()
            self.victory_point_totals[self.active_player
                                      if model_count[self.active_player] > model_count[self.defending_player]
                                      else self.defending_player] += 1

    def determine_nearby_units(self, p):
        nearby_units = {self.active_player: [], self.defending_player: []}
        for player, units in self.remaining_units.items():
            for unit in units:
                d = self.locations[unit].calculate_distance(p)
                if d <= self.victory_point_radius:
                    nearby_units[player] = unit
        return nearby_units

    def next_phase(self):
        self.current_phase = next(self.phases)
        for player in [self.active_player, self.defending_player]:
            if not self.remaining_units[player]:
                print('%s has no more units!' % player.name)
                return False  # TODO: victory points
        getattr(self, self.current_phase.value + '_phase')()
        if self.current_phase == self._Phases.END:
            print("\n%s\n" % ("-" * 105))
            return self.next_turn()
        return self.next_phase()

    def next_turn(self):
        self.turn = (self.turn % 2) + 1  # 1 -> 2 -> 1...
        # reset units lost for battleshock purposes
        remaining_units = self.remaining_units[self.active_player] + self.remaining_units[self.defending_player]
        self.models_lost = {unit: 0 for unit in remaining_units}
        if self.turn == 2:  # we just incremented the turn, so if the previous turn was turn 1...
            # swap active and defending players
            self.active_player, self.defending_player = self.defending_player, self.active_player
        else:
            active_player_roll = DiceRoller.d6()
            defending_player_roll = DiceRoller.d6()
            # since the defending player (the player who went first in the previous round) chooses who goes first
            # in the following round in case of a tie, just assume they always wants to avoid being double turned
            if defending_player_roll >= active_player_roll:
                self.active_player, self.defending_player = self.defending_player, self.active_player
            return self.next_round()
        return True

    def next_round(self):
        if self.battle_round == FINAL_BATTLE_ROUND:
            return False  # TODO: end battle and victory conditions
        self.battle_round += 1
        return True

    # TODO: add flag to remove output (switch to logging?)
    def simulate_round(self):
        print('Battle round %d, turn %d\n' % (self.battle_round, self.turn))
        while self.next_phase():
            print('Battle round %d, turn %d\n' % (self.battle_round, self.turn))
        # FIXME: print victor

    def run(self):
        return self.simulate_round()
