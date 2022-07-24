"""Get readings from sensors"""
from contextlib import contextmanager
from typing import List, NamedTuple, Optional, Tuple, Union

import sensors

from .detect_notebook import in_ipython_frontend


@contextmanager
def sensors_session():
    try:
        sensors.init()
        yield
    finally:
        sensors.cleanup()


@sensors_session()
def report_all_readings():
    """Display readings from all available sensors

    Parameters
    ----------
    None

    Returns
    -------
    None
        The readings are displayed directly to stdout or a Jupyter notebook
    """
    if in_ipython_frontend():
        from IPython.display import Markdown, display

        report = lambda text: display(Markdown(text))
    else:
        report = print

    for chip in sensors.iter_detected_chips():
        for feature in chip:
            try:
                value: Union[float, None] = feature.get_value()
            except sensors.SensorsError:
                value = None
            report(f"- {chip.prefix.decode()}:{feature.name} : {value}")


class Sensor(NamedTuple):
    """Hashable specification for a specific sensor

    Attributes
    ----------
    chip : str
        The chip's prefix
    feature : str
        The name of the specific reading
    """

    chip: str
    feature: str

    def __str__(self):
        return ".".join(self)


@sensors_session()
def enumerate_all_sensors(
    readable_only: Optional[bool] = False,
) -> List[Sensor]:
    """Generate a list of all available sensors

    Parameters
    ----------
    readable_only : bool, optional
        If True, only return the sensors that are actually readable (read: don't throw a SensorsError).
        Default is False.

    Returns
    -------
    list of tuples, where the first value is a Sensor (chip, feature) tuples and the second the corresponding Feature
    instances
    """
    sensors_list = []
    for chip in sensors.iter_detected_chips():
        for feature in chip:
            if readable_only:
                try:
                    _ = feature.get_value()
                except sensors.SensorsError:
                    continue
            sensors_list.append(Sensor(chip.prefix.decode(), feature.name))
    return sensors_list
