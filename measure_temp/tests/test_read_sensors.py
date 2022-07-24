"""Integration tests for ensuring the read_sensors module is playing nicely on your system"""
import pytest
import sensors

from measure_temp import read_sensors


class TestReportAllReadings:
    def test_report_all_readings_smoke_test(self):
        read_sensors.report_all_readings()


class TestEnumerateAllSensors:

    all_readable_sensors = read_sensors.enumerate_all_sensors(readable_only=True)

    def test_system_has_at_least_one_readable_sensor(self):
        assert len(self.all_readable_sensors) > 0

    @pytest.mark.xfail
    def test_all_readings_are_unique(self):
        all_sensors, _ = zip(*read_sensors.enumerate_all_sensors(readable_only=False))
        # also checking that the Sensor class is hashable and sortable
        assert sorted(set(all_sensors)) == sorted(all_sensors)

    @pytest.mark.parametrize("sensor", all_readable_sensors)
    def test_all_readable_sensors_are_readable(self, sensor):
        with read_sensors.sensors_session():
            for chip in sensors.iter_detected_chips():
                if chip.prefix.decode() != sensor.chip:
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
