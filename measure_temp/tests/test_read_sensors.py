"""Integration tests for ensuring the read_sensors module is playing nicely on your system"""
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
