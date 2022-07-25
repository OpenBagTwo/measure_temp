"""Tests for making sure I implemented by AttrDict recipe correctly"""
from measure_temp._attrdict import AttrDict


class TestAttrDict:
    def test_attrs_are_keys(self):
        attrdict = AttrDict(hello="world")
        assert attrdict["hello"] is attrdict.hello

    def test_attrdicts_are_mutable(self):
        attrdict = AttrDict(hello="world")
        attrdict.hello = "bonjour"
        assert attrdict["hello"] == "bonjour"

    def test_attrdicts_are_iterable(self):
        attrdict = AttrDict({"a": "ayy", "b": "bee", "c": "sea", "d": "dee"})
        assert sorted(attrdict) == ["a", "b", "c", "d"]

    def test_attrdict_values_are_iterable(self):
        attrdict = AttrDict({"a": "ayy", "b": "bee", "c": "sea", "d": "dee"})
        assert sorted(attrdict.values()) == ["ayy", "bee", "dee", "sea"]
