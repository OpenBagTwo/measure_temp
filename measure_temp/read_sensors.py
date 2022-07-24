"""Get readings from sensors"""
from contextlib import contextmanager
from typing import Union

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
