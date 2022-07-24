"""Integration tests for ensuring the read_sensors module is playing nicely on your system"""
from typing import List

import pytest
from sensors import SensorsError

from measure_temp import read_sensors


class TestReportAllReadings:
    def test_report_all_readings_smoke_test(self):
        read_sensors.report_all_readings()


class TestEnumerateAllSensors:

    all_readable_sensors = read_sensors.enumerate_all_sensors(readable_only=True)

    @staticmethod
    def pytest_generate_tests(metafunc):
        if "sensor" in metafunc.fixturenames:
            id_list, arg_values = zip(*metafunc.cls.all_readable_sensors)
            id_list = [".".join(sensor_name) for sensor_name in id_list]
            arg_names = [["sensor"]] * len(id_list)
            arg_values = [[sensor] for sensor in arg_values]
            metafunc.parametrize(arg_names, arg_values, ids=id_list, scope="class")

    def test_system_has_at_least_one_readable_sensor(self):
        assert len(self.all_readable_sensors) > 0

    @pytest.mark.xfail
    def test_all_readings_are_unique(self):
        all_sensors, _ = zip(*read_sensors.enumerate_all_sensors(readable_only=False))
        # also checking that the Sensor class is hashable and sortable
        assert sorted(set(all_sensors)) == sorted(all_sensors)

    def test_all_readable_sensors_are_readable(self, sensor):
        with read_sensors.sensors_session():
            _ = sensor.get_value()
