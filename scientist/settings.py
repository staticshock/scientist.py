class settings(object):
    """
    Settings shared by all experiments.
    """

    # Chance of running experiment. 1.0 corresponds to 100% chance of running.
    # 0.5 = 50%.
    chance = 1.0

    # Raise an error on mismatches
    raise_on_mismatches = False


class ConfigurationError(Exception):
    pass
