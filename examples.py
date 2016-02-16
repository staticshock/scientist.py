from __future__ import print_function
from scientist import Experiment


def test_fn():
    print("in test fn")


# Decorator approach
@Experiment(test_fn)
def control_fn():
    print("in control fn")

control_fn()


def big_function():
    control = lambda: print('in control!')
    test_behavior = lambda: print('in test!')
    experiment = Experiment(test_behavior, control, context={})
    print(experiment.run())

big_function()
