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


def read_sensor(sensor: Union[str, Sensor]):
    """Read a sensor value

    Parameters
    ----------
    sensor : Sensor tuple or a string of the form "chip_prefix.feature_name"
        The sensor to read. If your system has multiple chips with the same prefix, it is highly recommended that you
        use a Sensor tuple that specifies the address.

    Returns
    -------
    float
        The sensor value

    Raises
    ------
    SensorError
        If the sensor cannot be read
    ValueError
        If the chip cannot be found or the feature cannot be found on that sensor

    Notes
    -----
    No units are provided--hopefully you can figure out on your own whether you're seeing degrees C, RPM or volts.
    """
    if isinstance(sensor, str):
        sensor_lookup = {str(value): value for value in enumerate_all_sensors()}
        try:
            sensor = sensor_lookup[sensor]
        except KeyError:
            raise ValueError(f"Could not find a sensor matching descriptor {sensor}")

    with sensors_session():
        for chip in sensors.iter_detected_chips():
            if chip.addr != sensor.addr:
                continue
            for feature in chip:
                if feature.name == sensor.feature:
                    return feature.get_value()
            else:
                raise ValueError(
                    f"Feature {sensor.feature} not found on chip {str(sensor).split('.')[0]}"
                )
    raise ValueError(f"Chip {sensor.chip} not found at address {sensor.addr}")
