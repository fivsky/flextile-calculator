import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_form_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "FLEXTILE" in response.text
    assert "резиновая студия" in response.text

@pytest.mark.parametrize(
    "tile_count, length_cm, width_cm, thickness_mm, pigment, material, region, expected_text",
    [
        (1, 50, 50, "30", "синий", "SBR", "Центральный (Москва, МО)", "ИТОГО"),
        (10, 50, 50, "20", "красный", "SBR+EPDM", "Сибирский", "ИТОГО"),
    ]
)
def test_calculation(tile_count, length_cm, width_cm, thickness_mm, pigment, material, region, expected_text):
    response = client.post(
        "/calculate",
        data={
            "tile_count": tile_count,
            "tile_length_cm": length_cm,
            "tile_width_cm": width_cm,
            "thickness_mm": thickness_mm,
            "pigment": pigment,
            "material": material,
            "region": region,
        }
    )
    assert response.status_code == 200
    assert expected_text in response.text