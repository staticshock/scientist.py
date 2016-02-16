from random import random, sample
from functools import wraps
from logging import getLogger

from .settings import settings, ConfigurationError
from .utils import Timer

logger = getLogger(__name__)


class Experiment(object):
    """
    Establish a function as the basis for an experiment.

    >>> @Experiment(new_unverified_fn)
    ... def old_known_fn():
    ...     ...
    """
    _control = None

    def __init__(self, behaviors=(), control=None, name=None, **options):
        self.behaviors = set([behaviors] if callable(behaviors) else behaviors)
        # Control function can also be specified as a decorator via __call__
        self.control = control
        if control is not None:
            self.behaviors.add(self.control)

        self._name = name
        self._compare = options.pop('compare', None)
        self.context = options.pop('context', {})

        # Settings
        self.chance = options.get('chance', settings.chance)
        self.raise_on_mismatches = options.get(
            'raise_on_mismatches', settings.raise_on_mismatches)

    @property
    def name(self):
        return self._name or (
            self.control.__name__ if self.control else self.__name__)

    @property
    def control(self):
        return self._control

    @control.setter
    def control(self, value):
        if self._control is not None:
            raise ConfigurationError(
                "The control function should only be set once."
            )
        self._control = value

    def __call__(self, control):
        """
        Wrap a control function.
        """
        self.control = control
        self.behaviors.add(control)

        @wraps(control)
        def wrapper(*args, **kwargs):
            return self.run(*args, **kwargs)

        wrapper.experiment = self
        return wrapper

    @property
    def should_run_experiment(self):
        return len(self.behaviors) > 1 and settings.chance > random()

    def run(self, *args, **kwargs):
        # Always run the control behavior, but allow other behaviors to run
        # intermittently.
        if self.should_run_experiment:
            behaviors = sample(self.behaviors, len(self.behaviors))
        else:
            behaviors = [self.control]

        result = Result(self, behaviors, args, kwargs)
        try:
            for ix, behavior in enumerate(behaviors):
                result.timed_run(behavior, *args, **kwargs)
        finally:
            # If control raised an exception, some of the other behaviors may
            # not have run yet. Keep going.
            for behavior in behaviors[ix+1:]:
                result.timed_run(behavior, *args, **kwargs)

            self.publish(result)

            # Mismatch exceptions should supersede a control's exception
            should_raise = (
                self.raise_on_mismatches and
                not result.observations_are_equivalent
            )
            if should_raise:
                raise ObservationMismatchError(
                    "Observations are not equivalent", result)

        # If control didn't throw an exception, return its value.
        return result.control_observation.value

    def compare(self, control_result, experimental_result):
        _compare = getattr(self, '_compare', lambda x, y: x == y)
        """
        Return true if the results match.
        """
        return (
            # Mismatch if only one of the results returned an error, or if
            # different types of errors were returned.
            type(control_result.error) is type(experimental_result.error) and
            _compare(control_result.value, experimental_result.value)
        )

    def publish(self, result):
        if result.observations_are_equivalent:
            logger.info(u"Observations for {e.name} match!".format(e=self))
        else:
            logger.error(
                u"Observations for {e.name} don't match!".format(e=self))


class Result(object):
    """
    A single run of an experiment.
    """
    def __init__(self, experiment, behaviors, args, kwargs):
        self.experiment = experiment
        self.behaviors = behaviors
        self.observations = []
        self.args = args
        self.kwargs = kwargs

    def timed_run(self, behavior, *args, **kwargs):
        timer = Timer()
        try:
            value = behavior(*args, **kwargs)
            self.observations.append(Observation(value, None, timer.stop()))
        except Exception as ex:
            self.observations.append(Observation(None, ex, timer.stop()))
            if behavior is self.experiment.control:
                raise

    @property
    def control_observation(self):
        for behavior, observation in zip(self.behaviors, self.observations):
            if behavior is self.experiment.control:
                return observation

    def observations_are_equivalent(self):
        control_observation = self.control_observation
        for behavior, observation in zip(self.behaviors, self.observations):
            is_equivalent = (
                behavior is self.experiment.control or
                self.experiment.compare(control_observation, observation))
            if not is_equivalent:
                return False
        return True


class Observation(object):
    def __init__(self, value, error, duration):
        self.value = value
        self.error = error
        self.duration = duration


class ObservationMismatchError(Exception):
    pass
