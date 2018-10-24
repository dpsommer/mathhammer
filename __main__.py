import importlib
import pkgutil
import pyclbr

import stats
import units
from player import Player
from unit import UNITS


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

import_units(units)

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

# print weapon statlines
stats.calculate_attacks_vs_targets(attacking_unit, [defending_unit])

simulations_to_run = 10
simulation = stats.Simulation(
    p1=Player(name='Duncan'),
    p2=Player(name='Bjarne'),
    units_p1=[attacking_unit],
    units_p2=[defending_unit]
)
for _ in range(simulations_to_run):
    simulation.run()
    simulation.reset()
    print('\n%s\n' % ('#' * 105))
