import os

from multisimulator import Multisimulator


if __name__ == '__main__':
    simulator = Multisimulator.FromJSONDirectory(os.path.join('data', '2016'), 2000, 250)
    simulator.Simulate(useKnown=True)
    simulator.PrintUndefeated()
