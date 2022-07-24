"""Get readings from sensors"""
from contextlib import contextmanager
from typing import List, NamedTuple, Optional, Set, Tuple, Union

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
    addr : int
        The chip's address
    feature : str
        The name of the specific reading
    num : int, optional
        If two chips share the same name, you can supply a unique number suffix to distinguish them from each other
        without resorting to using the address. If None is specified at init, the default value is 0.

    """

    chip: str
    addr: int
    feature: str
    num: int = 0

    def __str__(self):
        return f"{self.chip}{self.num if self.num else ''}.{self.feature}"


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
    sensors_list: List[Sensor] = []
    chip_labels: Set[Tuple[str, int]] = set()
    for chip in sensors.iter_detected_chips():
        chip_label = chip.prefix.decode()
        num = 0
        while (chip_label, num) in chip_labels:
            num += 1
        chip_labels.add((chip_label, num))
        for feature in chip:
            if readable_only:
                try:
                    _ = feature.get_value()
                except sensors.SensorsError:
                    continue
            sensors_list.append(Sensor(chip_label, chip.addr, feature.name, num=num))
    return sensors_list
