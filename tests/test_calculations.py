import pytest
from app import DELIVERY_TARIFFS, DENSITY

def test_delivery_tariffs():
    assert DELIVERY_TARIFFS["Центральный (Москва, МО)"] == 0
    assert DELIVERY_TARIFFS["Дальневосточный"] == 85

def test_density():
    assert DENSITY["SBR"] == 1100
    assert DENSITY["SBR+EPDM"] == 1400