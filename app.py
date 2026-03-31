from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import math

app = FastAPI()

DELIVERY_TARIFFS = {
    "Центральный (Москва, МО)": 0,
    "Северо-Западный": 45,
    "Южный": 55,
    "Приволжский": 40,
    "Уральский": 60,
    "Сибирский": 70,
    "Дальневосточный": 85,
}

DENSITY = {"SBR": 1100, "SBR+EPDM": 1400}

# Фиксированные размеры плитки: 50x50 см = 0.25 м²
TILE_AREA_M2 = 0.25

# Вес одной плитки (кг) в зависимости от толщины
WEIGHT_PER_TILE = {
    "20": 4.24,
    "25": 5.30,   # промежуточное значение (не использовалось, но добавим на всякий случай)
    "30": 6.50,
    "35": 7.13,   # интерполяция
    "40": 7.75,
}

# Цена за м² в зависимости от материала и толщины (базовая формула)
def get_base_price(material: str, thickness_mm: int) -> float:
    if material == "SBR":
        return 1200 + (thickness_mm - 20) * 30
    else:
        return 1800 + (thickness_mm - 20) * 50

FORM_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLEXTILE // студия резины</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700;900&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: radial-gradient(circle at 20% 40%, #0a0502, #020100);
            font-family: 'Heebo', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            position: relative;
            overflow-x: hidden;
        }

        .spotlight {
            position: fixed;
            border-radius: 50%;
            filter: blur(70px);
            opacity: 0.3;
            background: radial-gradient(circle, rgba(255,220,150,0.7) 0%, rgba(255,180,80,0) 80%);
            pointer-events: none;
            z-index: 1;
        }
        .spotlight:nth-child(1) { width: 600px; height: 600px; top: -200px; left: -200px; opacity: 0.4; }
        .spotlight:nth-child(2) { width: 800px; height: 800px; bottom: -300px; right: -200px; opacity: 0.25; filter: blur(100px); }
        .spotlight:nth-child(3) { width: 450px; height: 450px; top: 30%; right: 5%; opacity: 0.2; filter: blur(80px); }
        .spotlight:nth-child(4) { width: 550px; height: 550px; bottom: 20%; left: -100px; opacity: 0.2; filter: blur(90px); }

        body::after {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIj48ZmlsdGVyIGlkPSJmIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iLjciIG51bU9jdGF2ZXM9IjMiLz48L2ZpbHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgjZikiIG9wYWNpdHk9IjAuMTgiLz48L3N2Zz4=');
            background-repeat: repeat;
            pointer-events: none;
            z-index: 2;
        }

        .vignette {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            box-shadow: inset 0 0 180px 70px rgba(0,0,0,0.7);
            pointer-events: none;
            z-index: 2;
        }

        .container {
            width: 100%;
            max-width: 1100px;
            position: relative;
            z-index: 10;
            animation: fadeInUp 0.9s cubic-bezier(0.2, 0.9, 0.4, 1.1);
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .hero {
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
        }
        .hero h1 {
            font-family: 'Heebo', sans-serif;
            font-weight: 900;
            font-size: clamp(4.5rem, 15vw, 13rem);
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #f5e6d3, #dbb87a, #b88b4a);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 0 25px rgba(200,150,80,0.3);
            line-height: 1;
            margin: 0;
            transform: scaleY(0.98);
        }
        .hero .sub {
            font-family: 'Heebo', sans-serif;
            font-weight: 300;
            font-size: 0.85rem;
            letter-spacing: 10px;
            text-transform: uppercase;
            color: #d6b575;
            margin-top: -1rem;
            background: rgba(0,0,0,0.45);
            display: inline-block;
            padding: 0.3rem 1.5rem;
            border-radius: 60px;
            backdrop-filter: blur(4px);
        }

        .card {
            background: rgba(8, 7, 5, 0.65);
            backdrop-filter: blur(16px);
            border-radius: 56px;
            padding: 2.2rem;
            border: 1px solid rgba(200, 170, 110, 0.5);
            box-shadow: 0 25px 45px -12px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,245,200,0.1);
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
            gap: 1.6rem;
        }
        .input-group {
            margin-bottom: 0.5rem;
        }
        label {
            display: block;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 4px;
            color: #e6d5b3;
            margin-bottom: 0.6rem;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            background: #1f1b12;
            border: 1px solid #b88b4a;
            padding: 12px 18px;
            font-size: 0.95rem;
            border-radius: 60px;
            outline: none;
            color: #f5e6d3;
            font-family: monospace;
            transition: all 0.2s;
        }
        input:focus, select:focus {
            border-color: #e6b86e;
            box-shadow: 0 0 12px #c9a258;
            background: #2c251c;
        }
        .radio-group {
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            align-items: center;
            margin-top: 0.5rem;
        }
        .radio-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            letter-spacing: normal;
            text-transform: none;
            color: #e6d5b3;
        }
        .radio-group input {
            width: auto;
            margin-right: 5px;
        }

        button {
            background: linear-gradient(95deg, #b88b4a, #7a5a3a);
            border: none;
            padding: 15px 32px;
            width: 100%;
            font-size: 1rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 4px;
            color: #0f0b06;
            border-radius: 60px;
            cursor: pointer;
            margin-top: 1.8rem;
            transition: all 0.25s;
            font-family: monospace;
        }
        button:hover {
            background: linear-gradient(95deg, #d6a15c, #9b6e42);
            letter-spacing: 5px;
            box-shadow: 0 0 20px #b88b4a;
            transform: scale(0.98);
        }

        @media (max-width: 700px) {
            body { padding: 1.2rem; }
            .card { padding: 1.5rem; }
            .hero .sub { letter-spacing: 5px; font-size: 0.7rem; }
            .form-grid { gap: 1rem; }
        }
    </style>
</head>
<body>
    <div class="spotlight"></div>
    <div class="spotlight"></div>
    <div class="spotlight"></div>
    <div class="spotlight"></div>
    <div class="vignette"></div>

    <div class="container">
        <div class="hero">
            <h1>FLEXTILE</h1>
            <div class="sub">резиновая студия</div>
        </div>
        <div class="card">
            <form action="/calculate" method="post">
                <div class="form-grid">
                    <div class="input-group">
                        <label>Количество плиток (шт)</label>
                        <input type="number" name="tile_count" min="1" max="1000" value="1" required>
                    </div>
                    <div class="input-group">
                        <label>Размер плитки</label>
                        <input type="text" value="50 x 50 см" readonly disabled style="background:#2c251c; color:#f5e6d3;">
                    </div>
                    <div class="input-group">
                        <label>Толщина (мм)</label>
                        <select name="thickness_mm">
                            <option value="20">20 мм</option>
                            <option value="30" selected>30 мм</option>
                            <option value="40">40 мм</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Пигмент</label>
                        <select name="pigment">
                            <option value="синий">🔵 Синий</option>
                            <option value="желтый">🟡 Желтый</option>
                            <option value="красный">🔴 Красный</option>
                            <option value="зеленый">🟢 Зеленый</option>
                            <option value="терракотовый">🏺 Терракотовый</option>
                            <option value="белый">⚪ Белый</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Регион доставки</label>
                        <select name="region">
                            <option value="Центральный (Москва, МО)">Центральный (Москва, МО)</option>
                            <option value="Северо-Западный">Северо-Западный</option>
                            <option value="Южный">Южный</option>
                            <option value="Приволжский">Приволжский</option>
                            <option value="Уральский">Уральский</option>
                            <option value="Сибирский">Сибирский</option>
                            <option value="Дальневосточный">Дальневосточный</option>
                        </select>
                    </div>
                    <div class="input-group">
                        <label>Материал</label>
                        <div class="radio-group">
                            <label><input type="radio" name="material" value="SBR" checked> SBR</label>
                            <label><input type="radio" name="material" value="SBR+EPDM"> SBR + EPDM</label>
                        </div>
                    </div>
                </div>
                <button type="submit">РАССЧИТАТЬ →</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

RESULT_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FLEXTILE // СМЕТА</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: radial-gradient(circle at 20% 40%, #0a0502, #020100);
            font-family: 'Heebo', 'Times New Roman', serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            position: relative;
        }}
        body::after {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIj48ZmlsdGVyIGlkPSJmIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iLjciIG51bU9jdGF2ZXM9IjMiLz48L2ZpbHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgjZikiIG9wYWNpdHk9IjAuMTgiLz48L3N2Zz4=');
            background-repeat: repeat;
            pointer-events: none;
            z-index: 1;
        }}
        .vignette {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            box-shadow: inset 0 0 180px 70px rgba(0,0,0,0.7);
            pointer-events: none;
            z-index: 2;
        }}
        .result-card {{
            position: relative;
            z-index: 10;
            background: rgba(8, 7, 5, 0.75);
            backdrop-filter: blur(14px);
            border-radius: 56px;
            padding: 2rem;
            max-width: 600px;
            width: 100%;
            border: 1px solid #b88b4a;
            box-shadow: 0 0 35px rgba(184,139,74,0.25);
            animation: fadeIn 0.6s ease;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(25px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        h1 {{
            font-family: 'Heebo', sans-serif;
            font-weight: 800;
            font-size: 2.1rem;
            background: linear-gradient(135deg, #f5e6d3, #dbb87a);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 0.3rem;
        }}
        .sub {{
            color: #d6b575;
            letter-spacing: 3px;
            font-size: 0.7rem;
            margin-bottom: 1.8rem;
            border-left: 3px solid #b88b4a;
            padding-left: 1rem;
            font-family: 'Heebo', monospace;
        }}
        .result-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.85rem 0;
            border-bottom: 1px solid rgba(184,139,74,0.3);
            color: #f0e5d0;
            font-family: 'Heebo', monospace;
            font-size: 0.95rem;
        }}
        .total {{
            font-size: 1.35rem;
            font-weight: bold;
            color: #ecd9b4;
            border-top: 2px solid #b88b4a;
            margin-top: 0.8rem;
            padding-top: 1rem;
        }}
        .button {{
            display: inline-block;
            background: #7a5a3a;
            text-decoration: none;
            color: #f0e5d0;
            padding: 12px 26px;
            border-radius: 60px;
            margin-top: 2rem;
            text-align: center;
            width: 100%;
            font-weight: bold;
            letter-spacing: 2px;
            transition: 0.2s;
            font-family: 'Heebo', monospace;
        }}
        .button:hover {{
            background: #b88b4a;
            color: #0a0703;
            transform: scale(0.98);
        }}
        @media (max-width: 600px) {{
            .result-card {{ padding: 1.5rem; }}
            h1 {{ font-size: 1.7rem; }}
        }}
    </style>
</head>
<body>
    <div class="vignette"></div>
    <div class="result-card">
        <h1>FLEXTILE</h1>
        <div class="sub">// детализация</div>
        <div class="result-row"><span>📦 Количество плиток</span><span>{tile_count} шт</span></div>
        <div class="result-row"><span>📐 Размер плитки</span><span>50 x 50 см</span></div>
        <div class="result-row"><span>📐 Общая площадь</span><span>{area} м²</span></div>
        <div class="result-row"><span>⚖️ Общий вес</span><span>{total_weight} кг</span></div>
        <div class="result-row"><span>🧱 Материал</span><span>{material}</span></div>
        <div class="result-row"><span>🎨 Пигмент</span><span>{pigment}</span></div>
        <div class="result-row"><span>📏 Толщина</span><span>{thickness} мм</span></div>
        <div class="result-row"><span>📍 Регион</span><span>{region}</span></div>
        <div class="result-row"><span>💰 Материал</span><span>{material_cost} ₽</span></div>
        <div class="result-row"><span>🚚 Доставка</span><span>{delivery_cost} ₽</span></div>
        <div class="result-row total"><span>ИТОГО</span><span>{total} ₽</span></div>
        <a href="/" class="button">← НОВЫЙ РАСЧЁТ</a>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def form():
    return FORM_HTML

@app.post("/calculate", response_class=HTMLResponse)
async def calculate(
    tile_count: int = Form(...),
    thickness_mm: str = Form(...),
    pigment: str = Form(...),
    material: str = Form(...),
    region: str = Form(...)
):
    thickness_int = int(thickness_mm)
    # Общая площадь
    total_area_m2 = tile_count * TILE_AREA_M2

    # Стоимость материала
    base_price = get_base_price(material, thickness_int)
    material_cost = total_area_m2 * base_price

    # Вес
    weight_per_tile = WEIGHT_PER_TILE.get(thickness_mm, 6.5)  # по умолчанию 30 мм
    total_weight_kg = tile_count * weight_per_tile

    # Доставка
    tariff = DELIVERY_TARIFFS.get(region, 50)
    delivery_cost = total_weight_kg * tariff if tariff > 0 else 0

    total = material_cost + delivery_cost

    return RESULT_HTML.format(
        tile_count=tile_count,
        area=round(total_area_m2, 2),
        total_weight=round(total_weight_kg, 1),
        material="SBR+EPDM" if material == "SBR+EPDM" else "SBR",
        pigment=pigment,
        thickness=thickness_mm,
        region=region,
        material_cost=round(material_cost, 2),
        delivery_cost=round(delivery_cost, 2),
        total=round(total, 2)
    )