from enum import Enum
from random import randint


class Dice(Enum):
    D6 = "d6"
    D3 = "d3"


class DiceRoller:

    @staticmethod
    def roll(number_of_dice, dice_type=Dice.D6, modifier=0):
        return [getattr(DiceRoller, dice_type.value)() + modifier for _ in range(number_of_dice)]

    @staticmethod
    def d3():
        return randint(1, 3)

    @staticmethod
    def d6():
        return randint(1, 6)
