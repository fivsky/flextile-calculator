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
            background: radial-gradient(circle at 20% 40%, #221c0c, #050301);
            font-family: 'Heebo', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
            position: relative;
        }

        .spotlight {
            position: fixed;
            border-radius: 50%;
            filter: blur(60px);
            opacity: 0.35;
            background: radial-gradient(circle, rgba(255,240,180,0.8) 0%, rgba(255,200,100,0) 80%);
            pointer-events: none;
            z-index: 1;
        }
        .spotlight:nth-child(1) { width: 500px; height: 500px; top: -150px; left: -150px; }
        .spotlight:nth-child(2) { width: 700px; height: 700px; bottom: -200px; right: -200px; opacity: 0.3; filter: blur(90px); }
        .spotlight:nth-child(3) { width: 400px; height: 400px; top: 20%; right: 10%; opacity: 0.2; filter: blur(70px); }
        .spotlight:nth-child(4) { width: 600px; height: 600px; bottom: 10%; left: 20%; opacity: 0.2; filter: blur(100px); }

        body::after {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIj48ZmlsdGVyIGlkPSJmIj48ZmVUdXJidWxlbmNlIHR5cGU9ImZyYWN0YWxOb2lzZSIgYmFzZUZyZXF1ZW5jeT0iLjgiIG51bU9jdGF2ZXM9IjMiLz48L2ZpbHRlcj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWx0ZXI9InVybCgjZikiIG9wYWNpdHk9IjAuMjUiLz48L3N2Zz4=');
            background-repeat: repeat;
            opacity: 0.15;
            pointer-events: none;
        }

        .vignette {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            box-shadow: inset 0 0 150px 50px rgba(0,0,0,0.6);
            pointer-events: none;
        }

        .container {
            width: 100%;
            max-width: 1100px;
            position: relative;
            z-index: 10;
            animation: fadeInUp 0.8s ease;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .hero {
            text-align: center;
            margin-bottom: 2rem;
        }
        .hero h1 {
            font-family: 'Heebo', sans-serif;
            font-weight: 900;
            font-size: clamp(4rem, 14vw, 12rem);
            background: linear-gradient(135deg, #ecd9b4, #b88b4a, #7a5a3a);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-shadow: 0 0 15px rgba(0,0,0,0.5);
            line-height: 1;
            margin: 0;
        }
        .hero .sub {
            font-family: 'Heebo', sans-serif;
            font-weight: 300;
            font-size: 0.9rem;
            letter-spacing: 8px;
            text-transform: uppercase;
            color: #d6b575;
            margin-top: -1rem;
            background: rgba(0,0,0,0.4);
            display: inline-block;
            padding: 0 1rem;
        }

        .card {
            background: rgba(10, 10, 12, 0.75);
            backdrop-filter: blur(12px);
            border-radius: 48px;
            padding: 2rem;
            border: 1px solid rgba(200, 170, 110, 0.5);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,200,0.1);
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 1.5rem;
        }
        .input-group {
            margin-bottom: 1rem;
        }
        label {
            display: block;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: #e6d5b3;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        input, select {
            width: 100%;
            background: #1e1a12;
            border: 1px solid #b88b4a;
            padding: 12px 16px;
            font-size: 0.95rem;
            border-radius: 60px;
            outline: none;
            color: #f0e5d0;
            font-family: monospace;
            transition: 0.2s;
        }
        input:focus, select:focus {
            border-color: #e6b86e;
            box-shadow: 0 0 12px #c9a258;
            background: #2a241a;
        }
        .radio-group {
            display: flex;
            gap: 1.8rem;
            flex-wrap: wrap;
            align-items: center;
            margin-top: 0.5rem;
        }
        .radio-group label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8rem;
            letter-spacing: normal;
            text-transform: none;
        }
        button {
            background: linear-gradient(90deg, #b88b4a, #7a5a3a);
            border: none;
            padding: 14px 28px;
            width: 100%;
            font-size: 1rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: #0f0b06;
            border-radius: 60px;
            cursor: pointer;
            margin-top: 1.5rem;
            transition: 0.2s;
        }
        button:hover {
            background: linear-gradient(90deg, #d6a15c, #9b6e42);
            letter-spacing: 4px;
            box-shadow: 0 0 15px #b88b4a;
            transform: scale(0.98);
        }

        .music-player {
            margin-top: 2rem;
            text-align: center;
        }
        .music-btn {
            background: rgba(184, 139, 74, 0.2);
            border: 1px solid #b88b4a;
            padding: 8px 30px;
            border-radius: 60px;
            font-size: 0.9rem;
            cursor: pointer;
            color: #f2e2c0;
            transition: 0.2s;
            font-weight: bold;
            letter-spacing: 2px;
        }
        .music-btn.active, .music-btn:hover {
            background: #b88b4a;
            color: #0a0703;
            box-shadow: 0 0 8px #e6b86e;
        }

        @media (max-width: 700px) {
            body { padding: 1rem; }
            .card { padding: 1.5rem; }
            .hero .sub { letter-spacing: 4px; font-size: 0.7rem; }
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
            <div class="sub">студия резины</div>
        </div>
        <div class="card">
            <form action="/calculate" method="post">
                <div class="form-grid">
                    <div class="input-group">
                        <label>Количество плиток (шт)</label>
                        <input type="number" name="tile_count" min="1" max="1000" value="1" required>
                    </div>
                    <div class="input-group">
                        <label>Длина плитки (см)</label>
                        <input type="number" step="1" name="tile_length_cm" value="50" required>
                    </div>
                    <div class="input-group">
                        <label>Ширина плитки (см)</label>
                        <input type="number" step="1" name="tile_width_cm" value="50" required>
                    </div>
                    <div class="input-group">
                        <label>Толщина (мм)</label>
                        <select name="thickness_mm">
                            <option value="20">20 мм</option>
                            <option value="25">25 мм</option>
                            <option value="30" selected>30 мм</option>
                            <option value="35">35 мм</option>
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

            <div class="music-player">
                <button type="button" id="musicBtn" class="music-btn">MUSIC (2STEP)</button>
            </div>
        </div>
    </div>

    <audio id="bgMusic" loop preload="auto">
        <source src="https://cdn.pixabay.com/download/audio/2022/12/14/audio_9e9c9b8b8e.mp3?filename=uk-garage-2step-125bpm-125416.mp3" type="audio/mpeg">
    </audio>

    <script>
        const audio = document.getElementById('bgMusic');
        const btn = document.getElementById('musicBtn');
        let playing = false;

        btn.addEventListener('click', () => {
            if (playing) {
                audio.pause();
                btn.classList.remove('active');
                playing = false;
                btn.textContent = 'MUSIC (2STEP)';
            } else {
                audio.play().then(() => {
                    playing = true;
                    btn.classList.add('active');
                    btn.textContent = '♫ 2STEP PLAYING';
                }).catch(err => {
                    console.error('Ошибка воспроизведения:', err);
                    btn.textContent = '❌ MUSIC ERROR';
                    setTimeout(() => {
                        if (!playing) btn.textContent = 'MUSIC (2STEP)';
                    }, 2000);
                });
            }
        });
    </script>
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
            background: radial-gradient(circle at 20% 40%, #221c0c, #050301);
            font-family: 'Heebo', 'Times New Roman', serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }}
        .result-card {{
            background: rgba(12, 10, 8, 0.85);
            backdrop-filter: blur(12px);
            border-radius: 48px;
            padding: 2rem;
            max-width: 600px;
            width: 100%;
            border: 1px solid #b88b4a;
            box-shadow: 0 0 30px rgba(184,139,74,0.3);
            animation: fadeIn 0.5s ease;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        h1 {{
            font-family: 'Heebo', 'Times New Roman', serif;
            font-weight: 800;
            font-size: 2rem;
            background: linear-gradient(135deg, #ecd9b4, #b88b4a);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
        }}
        .sub {{
            color: #d6b575;
            letter-spacing: 2px;
            font-size: 0.7rem;
            margin-bottom: 1.8rem;
            border-left: 3px solid #b88b4a;
            padding-left: 1rem;
            font-family: 'Heebo', monospace;
        }}
        .result-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.8rem 0;
            border-bottom: 1px solid rgba(184,139,74,0.3);
            color: #f0e5d0;
            font-family: 'Heebo', monospace;
        }}
        .total {{
            font-size: 1.3rem;
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
            padding: 12px 24px;
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
    </style>
</head>
<body>
    <div class="result-card">
        <h1>FLEXTILE</h1>
        <div class="sub">// детализация</div>
        <div class="result-row"><span>📦 Количество плиток</span><span>{tile_count} шт</span></div>
        <div class="result-row"><span>📐 Площадь (м²)</span><span>{area} м²</span></div>
        <div class="result-row"><span>⚖️ Вес (прим.)</span><span>{weight} кг</span></div>
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
    tile_length_cm: float = Form(...),
    tile_width_cm: float = Form(...),
    thickness_mm: str = Form(...),
    pigment: str = Form(...),
    material: str = Form(...),
    region: str = Form(...)
):
    tile_area_m2 = (tile_length_cm * tile_width_cm) / 10000.0
    total_area_m2 = tile_count * tile_area_m2
    thickness_int = int(thickness_mm)
    thickness_m = thickness_int / 1000.0

    if material == "SBR":
        base_price = 1200 + (thickness_int - 20) * 30
        density = DENSITY["SBR"]
    else:
        base_price = 1800 + (thickness_int - 20) * 50
        density = DENSITY["SBR+EPDM"]

    material_cost = total_area_m2 * base_price
    weight_kg = total_area_m2 * thickness_m * density
    tariff = DELIVERY_TARIFFS.get(region, 50)
    delivery_cost = weight_kg * tariff if tariff > 0 else 0
    total = material_cost + delivery_cost

    return RESULT_HTML.format(
        tile_count=tile_count,
        area=round(total_area_m2, 2),
        weight=round(weight_kg, 1),
        material="SBR+EPDM" if material == "SBR+EPDM" else "SBR",
        pigment=pigment,
        thickness=thickness_mm,
        region=region,
        material_cost=round(material_cost, 2),
        delivery_cost=round(delivery_cost, 2),
        total=round(total, 2)
    )