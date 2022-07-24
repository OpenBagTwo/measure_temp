"""Integration tests for ensuring the read_sensors module is playing nicely on your system"""
from typing import Iterable, NamedTuple, Optional, Tuple

import pytest
import sensors

from measure_temp import read_sensors


class TestReportAllReadings:
    def test_report_all_readings_smoke_test(self):
        print("\n---")
        read_sensors.report_all_readings()


class TestSensorRepresentation:
    def test_addr_isnt_used_for_stringification(self):
        assert str(read_sensors.Sensor("ppu", 314, "temp")) == "ppu.temp"

    def test_addr_numberings_in_stringification(self):
        assert str(read_sensors.Sensor("ppu", 272, "temp", num=1)) == "ppu1.temp"


class TestEnumerateAllSensors:

    all_sensors = read_sensors.enumerate_all_sensors(readable_only=False)
    all_readable_sensors = read_sensors.enumerate_all_sensors(readable_only=True)

    def test_system_has_at_least_one_readable_sensor(self):
        assert len(self.all_readable_sensors) > 0

    def test_all_sensors_are_unique(self):

        # also checking that the Sensor class is hashable and sortable
        assert sorted(set(self.all_sensors)) == sorted(self.all_sensors)

    def test_all_sensor_string_reprs_are_unique(self):
        sensor_strings = [str(sensor) for sensor in self.all_sensors]
        # also checking that the Sensor class is hashable and sortable
        assert sorted(set(sensor_strings)) == sorted(sensor_strings)

    @pytest.mark.parametrize("sensor", all_readable_sensors, ids=str)
    def test_all_readable_sensors_are_readable(self, sensor):
        with read_sensors.sensors_session():
            for chip in sensors.iter_detected_chips():
                if chip.prefix.decode() != sensor.chip or chip.addr != sensor.addr:
                    continue
                for feature in chip:
                    if feature.name == sensor.feature:
                        _ = feature.get_value()
                        break
                else:
                    raise ValueError("Feature not found")
                break
            else:
                raise ValueError("Chip not found")


class TestReadSensor:
    class MockFeature(NamedTuple):

        name: str
        value: float
        readable: Optional[bool] = True

        def get_value(self):
            if not self.readable:
                raise sensors.SensorsError("permission denied")
            return self.value

    class MockChip:
        def __init__(self, prefix: str, addr: int, features: Iterable[Tuple]):
            self.prefix = prefix.encode()
            self.addr = addr
            self.features = features

        def __iter__(self):
            for feature in self.features:
                yield feature

    @pytest.fixture(scope="class")
    def testing_chips(self):
        MC = TestReadSensor.MockChip
        MF = TestReadSensor.MockFeature
        yield [
            MC("ppu", 1234, [MF("freq", 100), MF("temp", -273.15)]),
            MC(
                "heisenbergcompensator",
                2370,
                [MF("position", 0.0), MF("momentum", 0.0, readable=False)],
            ),
            MC(
                "zpm",
                2004,
                [MF("power", 7e11)],
            ),
            MC(
                "fluxcapacitor",
                9309,
                [
                    MF("power", 1.21),
                    MF("speed", 88),
                ],
            ),
            MC(
                "fluxcapacitor",
                1809,
                [
                    MF("power", 2.21),
                    MF("year", 2035),
                ],
            ),
        ]

    @pytest.fixture(autouse=True)
    def mock_sensors_module(self, monkeypatch, testing_chips):
        monkeypatch.setattr(sensors, "init", lambda: None)
        monkeypatch.setattr(sensors, "cleanup", lambda: None)
        monkeypatch.setattr(sensors, "iter_detected_chips", lambda: iter(testing_chips))

    def test_get_reading_by_sensor(self):
        assert read_sensors.read_sensor(
            read_sensors.Sensor("zpm", 2004, "power")
        ) == pytest.approx(7e11)

    def test_get_reading_by_string(self):
        assert read_sensors.read_sensor("ppu.temp") == pytest.approx(-273.15)

    @pytest.mark.parametrize("addr, expected", ((9309, 1.21), (1809, 2.21)))
    def test_get_ambiguous_reading_by_address(self, addr, expected):
        assert read_sensors.read_sensor(
            read_sensors.Sensor("fluxcapacitor", addr, "power")
        ) == pytest.approx(expected)

    def test_get_ambiguous_by_suffix(self):
        assert read_sensors.read_sensor("fluxcapacitor1.year") == pytest.approx(2035)

    def test_chip_not_found_raises_value_error(self):
        with pytest.raises(ValueError, match="Chip zpm not found at address 1997"):
            read_sensors.read_sensor(read_sensors.Sensor("zpm", 1997, "power"))

    def test_feature_not_found_raises_value_error(self):
        with pytest.raises(
            ValueError,
            match="Feature speed not found on chip fluxcapacitor1",
        ):
            read_sensors.read_sensor(
                read_sensors.Sensor("fluxcapacitor", 1809, "speed", num=1)
            )

    def test_string_not_recognized_raises_value_error(self):
        with pytest.raises(
            ValueError,
            match="Could not find a sensor matching descriptor fluxcapacitor.year",
        ):
            read_sensors.read_sensor("fluxcapacitor.year")

    def test_unreadable_sensor_raises_sensor_error(self):
        with pytest.raises(sensors.SensorsError):
            read_sensors.read_sensor("heisenbergcompensator.momentum")
