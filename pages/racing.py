"""F1 Physics Garage - Racing page

Garage의 st.session_state 설정을 읽어 같은 차량으로 레이스합니다.
"""

import html
import json
import random
from copy import deepcopy

import streamlit as st
import streamlit.components.v1 as components


# Garage의 저장 키가 달라질 경우 이 두 줄만 수정하면 됩니다.
CAR_CONFIG_KEY = "my_car_config"
CAR_PERFORMANCE_KEY = "my_car_performance"
GARAGE_CONFIG_FALLBACK_KEY = "selections"  # 현재 Garage main.py가 실제로 사용하는 키
TOTAL_LAPS = 3
AI_CAR_COUNT = 6

METRICS = ["다운포스", "최고속도", "코너링", "그립", "제동", "안정성"]
METRIC_ENGLISH = {
    "다운포스": "DOWNFORCE", "최고속도": "TOP SPEED", "코너링": "CORNERING",
    "그립": "GRIP", "제동": "BRAKING", "안정성": "STABILITY",
}


def get_racing_part_data():
    """Garage와 같은 옵션 점수를 저장합니다.

    Racing 페이지는 main.py를 import하지 않으므로 페이지를 단독 실행해도
    같은 차량 성능을 재현할 수 있도록 필요한 데이터만 이곳에 둡니다.
    """
    return {
        "front_wing": {"low": [48,94,57,61,60,62], "balanced": [72,77,76,72,67,76], "high": [94,55,92,79,72,84]},
        "rear_wing": {"low": [45,96,54,59,58,56], "balanced": [73,76,76,70,64,78], "high": [96,51,93,77,69,94]},
        "tyres": {"soft": [66,80,92,98,91,71], "medium": [63,81,80,82,82,82], "hard": [60,82,68,70,73,89]},
        "brakes": {"race": [62,78,78,76,98,78], "balanced": [61,80,76,74,84,88], "light": [59,85,75,72,75,72]},
        "suspension": {"stiff": [73,80,91,80,77,67], "balanced": [68,81,82,82,80,88], "soft": [62,78,72,88,83,90]},
        "floor": {"venturi": [98,72,94,80,67,82], "balanced": [81,80,83,75,66,87], "light": [60,89,68,67,62,69]},
        "diffuser": {"large": [93,67,90,76,65,87], "balanced": [77,80,79,71,64,83], "compact": [55,91,63,61,61,68]},
        "engine": {"power": [62,99,82,72,62,70], "balanced": [62,88,80,72,64,87], "efficient": [60,82,79,72,65,92]},
        "ers": {"attack": [60,97,82,71,65,70], "balanced": [61,88,80,71,68,86], "recovery": [60,80,76,70,78,91]},
    }


def load_my_car_config():
    """Garage에서 사용자가 선택한 파츠 설정을 가져옵니다."""
    if CAR_CONFIG_KEY in st.session_state:
        return deepcopy(st.session_state[CAR_CONFIG_KEY])
    if GARAGE_CONFIG_FALLBACK_KEY in st.session_state:
        return deepcopy(st.session_state[GARAGE_CONFIG_FALLBACK_KEY])
    return None


def calculate_car_performance(car_config):
    """선택한 파츠가 차량 전체 성능에 미치는 영향을 Garage와 같은 방식으로 계산합니다."""
    part_data = get_racing_part_data()
    totals = [0] * len(METRICS)
    valid_part_count = 0
    for part_name, option_name in car_config.items():
        if part_name in part_data and option_name in part_data[part_name]:
            scores = part_data[part_name][option_name]
            totals = [total + score for total, score in zip(totals, scores)]
            valid_part_count += 1
    if not valid_part_count:
        return None
    return {metric: round(total / valid_part_count) for metric, total in zip(METRICS, totals)}


def load_my_car_performance(car_config):
    """Garage가 저장한 성능을 우선 사용하고, 없을 때만 파츠 설정으로 다시 계산합니다."""
    stored = st.session_state.get(CAR_PERFORMANCE_KEY)
    if isinstance(stored, dict) and all(metric in stored for metric in METRICS):
        return {metric: int(stored[metric]) for metric in METRICS}
    return calculate_car_performance(car_config)


def prepare_car_data(car_config, performance):
    """Python 데이터를 JavaScript 게임에서 사용하기 쉬운 영문 구조로 바꿉니다."""
    return {
        "config": car_config,
        "performance": {
            "downforce": performance["다운포스"], "topSpeed": performance["최고속도"],
            "cornering": performance["코너링"], "grip": performance["그립"],
            "braking": performance["제동"], "stability": performance["안정성"],
        },
        "appearance": {
            "frontWing": car_config.get("front_wing", "balanced"),
            "rearWing": car_config.get("rear_wing", "balanced"),
            "tyres": car_config.get("tyres", "medium"),
        },
    }


def generate_ai_cars(count=AI_CAR_COUNT):
    """레이스를 시작할 때마다 서로 다른 파츠와 성능을 가진 AI 차량을 만듭니다."""
    options = {key: list(value.keys()) for key, value in get_racing_part_data().items()}
    colors = ["#24c7ff", "#ffb21a", "#8a68ff", "#35e69a", "#ff5c72", "#e8edf2"]
    cars = []
    for index in range(count):
        config = {part: random.choice(names) for part, names in options.items()}
        performance = calculate_car_performance(config)
        cars.append({
            "name": f"AI {index + 1}", "config": config,
            "performance": prepare_car_data(config, performance)["performance"],
            "color": colors[index % len(colors)], "skill": round(random.uniform(0.94, 1.04), 3),
        })
    return cars


def apply_racing_css():
    """Garage와 연결되는 어두운 F1 게임 화면을 만듭니다."""
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@500;600;700&family=Noto+Sans+KR:wght@400;600;700&display=swap');
    :root{--red:#ff3158;--cyan:#27d6ff;--panel:#10161e;--line:#2a3542}
    .stApp{background:radial-gradient(circle at 50% 12%,#202b37,#090c11 48%,#05070a);color:#eff5fa}
    .block-container{max-width:1500px;padding:1rem 1.4rem 2rem}header,#MainMenu,footer{visibility:hidden}
    .race-head{border-top:3px solid var(--red);border-bottom:1px solid var(--line);padding:12px 16px;background:#0c1118;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
    .race-logo{font:700 25px 'Oxanium';letter-spacing:2px}.race-logo b{color:var(--red)}.race-step{font:600 11px 'Oxanium';color:#8391a0;letter-spacing:2px}
    .panel{background:linear-gradient(145deg,#111821,#090d12);border:1px solid var(--line);padding:15px;min-height:100%}.panel-title{font:700 12px 'Oxanium';letter-spacing:2px;color:#9daab8;border-bottom:1px solid #293542;padding-bottom:9px;margin-bottom:12px}
    .track-card{height:330px;background:radial-gradient(circle,#1e2a34,#080c11);display:flex;align-items:center;justify-content:center;border:1px solid #2b3744}.track-svg{width:92%;height:92%}.track-line{fill:none;stroke:#59636e;stroke-width:30;stroke-linecap:round;stroke-linejoin:round}.track-edge{fill:none;stroke:#dce4eb;stroke-width:35;stroke-dasharray:3 7}.track-center{fill:none;stroke:#13191f;stroke-width:25}
    .car-card{text-align:center;padding:14px;background:#0b1016;border:1px solid #283440}.mini-car{width:100%;max-width:360px;height:180px}.car-name{font:700 17px 'Oxanium';letter-spacing:2px}.config-chip{display:inline-block;margin:3px;padding:4px 7px;border:1px solid #344252;color:#9cabb9;font-size:10px}
    .perf{padding:8px 0}.perf-top{display:flex;justify-content:space-between;font:700 11px 'Oxanium'}.bar{height:9px;margin-top:5px;background:#232c36;overflow:hidden;transform:skewX(-12deg)}.bar>i{display:block;height:100%;background:linear-gradient(90deg,#27d6ff,#8265ff)}
    div[data-testid='stButton'] button{width:100%!important;min-height:56px!important;background:#e51d45!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid #ff6681!important;font:700 16px 'Oxanium'!important;letter-spacing:2px!important}div[data-testid='stButton'] button *{color:#fff!important;-webkit-text-fill-color:#fff!important}div[data-testid='stButton'] button:hover{background:#ff3158!important;box-shadow:0 0 25px #ff315877!important}
    .empty{max-width:650px;margin:100px auto;padding:35px;text-align:center;background:#0e141c;border:1px solid #2c3845;border-top:3px solid var(--red)}.empty h2{font-family:'Oxanium';color:#fff}.empty p{color:#9caab8}
    </style>""", unsafe_allow_html=True)


def create_track_preview():
    """긴 직선·헤어핀·빠른 코너·S자 코너가 포함된 가상 트랙을 SVG로 표시합니다."""
    return """<svg class='track-svg' viewBox='0 0 600 360' aria-label='가상 F1 트랙 미리보기'>
    <path class='track-edge' d='M105 285 C35 245 48 135 135 112 L430 52 C535 30 575 115 510 170 C472 202 394 164 366 207 C337 252 467 261 439 307 C405 350 278 289 222 303 C172 316 142 306 105 285Z'/>
    <path class='track-line' d='M105 285 C35 245 48 135 135 112 L430 52 C535 30 575 115 510 170 C472 202 394 164 366 207 C337 252 467 261 439 307 C405 350 278 289 222 303 C172 316 142 306 105 285Z'/>
    <path class='track-center' d='M105 285 C35 245 48 135 135 112 L430 52 C535 30 575 115 510 170 C472 202 394 164 366 207 C337 252 467 261 439 307 C405 350 278 289 222 303 C172 316 142 306 105 285Z'/>
    <text x='122' y='92' fill='#27d6ff' font-size='12'>LONG STRAIGHT</text><text x='455' y='205' fill='#ff6681' font-size='12'>S-CURVES</text><circle cx='105' cy='285' r='8' fill='#ff3158'/></svg>"""


def create_car_preview(car_data):
    """Garage 설정에 따라 윙 크기와 타이어 색이 달라지는 준비 화면 차량을 그립니다."""
    front_scale = {"low": 0.78, "balanced": 1.0, "high": 1.2}.get(car_data["appearance"]["frontWing"], 1)
    rear_scale = {"low": 0.78, "balanced": 1.0, "high": 1.22}.get(car_data["appearance"]["rearWing"], 1)
    tyre_color = {"soft": "#ed2939", "medium": "#ffd326", "hard": "#f2f4f6"}.get(car_data["appearance"]["tyres"], "#ffd326")
    return f"""<svg class='mini-car' viewBox='0 0 500 230'><defs><linearGradient id='r' x1='0' x2='1'><stop stop-color='#7c0920'/><stop offset='.5' stop-color='#ff3158'/><stop offset='1' stop-color='#78071b'/></linearGradient></defs>
    <ellipse cx='250' cy='194' rx='180' ry='18' fill='#000' opacity='.5'/><g fill='#090b0e' stroke='{tyre_color}' stroke-width='6'><rect x='70' y='57' width='82' height='53' rx='15'/><rect x='348' y='57' width='82' height='53' rx='15'/><rect x='55' y='145' width='95' height='60' rx='16'/><rect x='350' y='145' width='95' height='60' rx='16'/></g>
    <rect x='{250-145*front_scale}' y='30' width='{290*front_scale}' height='14' rx='5' fill='#27d6ff'/><rect x='{250-105*rear_scale}' y='202' width='{210*rear_scale}' height='16' rx='5' fill='#ffb21a'/><path d='M210 190 Q190 135 221 100 L238 44 H262 L279 100 Q310 135 290 190Z' fill='url(#r)'/><ellipse cx='250' cy='113' rx='28' ry='37' fill='#090d12' stroke='#5a6876' stroke-width='4'/><text x='250' y='80' text-anchor='middle' fill='white' font-family='Oxanium' font-weight='700'>01</text></svg>"""


def render_performance_bars(performance):
    """레이스 전에 현재 차량의 특징을 막대로 빠르게 확인하게 합니다."""
    for metric in METRICS:
        value = performance[metric]
        st.markdown(f"<div class='perf'><div class='perf-top'><span>{METRIC_ENGLISH[metric]}</span><span>{value}</span></div><div class='bar'><i style='width:{value}%'></i></div></div>", unsafe_allow_html=True)


def render_no_car_message():
    """Garage를 거치지 않은 사용자가 오류 대신 해야 할 일을 이해하게 합니다."""
    st.markdown("<div class='empty'><h2>🏎 아직 내 차량이 없어요</h2><p>먼저 Garage에서 파츠를 선택해 나만의 F1 차량을 만들어주세요.</p></div>", unsafe_allow_html=True)
    if st.button("GARAGE로 이동", use_container_width=True):
        st.switch_page("main.py")


def render_race_setup(car_data, performance):
    """트랙·내 차량·성능을 확인한 뒤 사용자가 직접 레이스를 시작하게 합니다."""
    st.markdown("<div class='race-head'><div class='race-logo'>F1 PHYSICS <b>RACING</b></div><div class='race-step'>RACE PREPARATION · AURORA CIRCUIT</div></div>", unsafe_allow_html=True)
    track_column, car_column, performance_column = st.columns([1.25, 1.05, 0.8], gap="medium")
    with track_column:
        st.markdown("<div class='panel'><div class='panel-title'>01 / TRACK · AURORA CIRCUIT</div><div class='track-card'>" + create_track_preview() + "</div><p style='color:#8d9baa;font-size:11px'>긴 직선 · 저속 헤어핀 · 고속 코너 · S자 구간</p></div>", unsafe_allow_html=True)
    with car_column:
        chips = "".join(f"<span class='config-chip'>{html.escape(key.replace('_',' ').upper())} · {html.escape(str(value).upper())}</span>" for key, value in car_data["config"].items())
        st.markdown(f"<div class='panel'><div class='panel-title'>02 / YOUR GARAGE CAR</div><div class='car-card'>{create_car_preview(car_data)}<div class='car-name'>MY F1 CAR</div>{chips}</div></div>", unsafe_allow_html=True)
    with performance_column:
        st.markdown("<div class='panel'><div class='panel-title'>03 / CAR PERFORMANCE</div>", unsafe_allow_html=True)
        render_performance_bars(performance)
        st.markdown("<p style='color:#758392;font-size:10px'>Garage에서 선택한 파츠의 성능이 실제 레이스 물리에 반영됩니다.</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏁  RACE START", use_container_width=True):
        st.session_state.race_started = True
        st.session_state.ai_cars = generate_ai_cars()
        st.rerun()


def calculate_vehicle_physics(performance):
    """0~100 성능 지표를 브라우저 게임의 물리 계수로 변환합니다."""
    return {
        "maxSpeed": 1.25 + performance["topSpeed"] * 0.009,
        "acceleration": 0.42 + performance["topSpeed"] * 0.0024,
        "steering": 1.15 + performance["cornering"] * 0.010,
        "grip": 0.76 + performance["grip"] * 0.0023,
        "brakePower": 0.75 + performance["braking"] * 0.010,
        "stability": 0.55 + performance["stability"] * 0.004,
        "downforce": performance["downforce"] / 100,
    }


def build_race_game_html(car_data, ai_cars):
    """WASD·AI·HUD·3인칭 카메라가 동작하는 WebGL 레이싱 게임 HTML을 생성합니다."""
    physics = calculate_vehicle_physics(car_data["performance"])
    payload = json.dumps({"player": car_data, "physics": physics, "ai": ai_cars, "laps": TOTAL_LAPS}, ensure_ascii=False)
    return RACE_GAME_TEMPLATE.replace("__RACE_DATA__", payload)


def render_race_game(car_data, ai_cars):
    """Streamlit 안에 새로고침 없이 실행되는 JavaScript 레이싱 게임을 삽입합니다."""
    st.markdown("<div class='race-head'><div class='race-logo'>F1 PHYSICS <b>RACING</b></div><div class='race-step'>WASD DRIVE · ESC PAUSE</div></div>", unsafe_allow_html=True)
    components.html(build_race_game_html(car_data, ai_cars), height=820, scrolling=False)
    if st.button("← 레이스 준비 화면", use_container_width=True):
        st.session_state.race_started = False
        st.rerun()


def main():
    """차량 확인 → 준비 화면 → 실제 레이스 순서로 페이지 흐름을 관리합니다."""
    st.set_page_config(page_title="F1 Physics Racing", page_icon="🏁", layout="wide", initial_sidebar_state="collapsed")
    apply_racing_css()
    car_config = load_my_car_config()
    if not car_config:
        render_no_car_message()
        return
    performance = load_my_car_performance(car_config)
    if not performance:
        render_no_car_message()
        return
    car_data = prepare_car_data(car_config, performance)
    if "race_started" not in st.session_state:
        st.session_state.race_started = False
    if st.session_state.race_started:
        if "ai_cars" not in st.session_state:
            st.session_state.ai_cars = generate_ai_cars()
        render_race_game(car_data, st.session_state.ai_cars)
    else:
        render_race_setup(car_data, performance)


# 아래 HTML은 브라우저 안에서만 실행됩니다. 키 입력 때문에 Streamlit이 재실행되지 않습니다.
RACE_GAME_TEMPLATE = r'''<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body,#game{margin:0;width:100%;height:100%;overflow:hidden;background:#05070a;font-family:Arial;color:#fff}canvas{display:block}.hud{position:absolute;inset:0;pointer-events:none}.box{position:absolute;background:#071019d9;border:1px solid #344657;border-top:2px solid #27d6ff;padding:10px 14px;box-shadow:0 10px 28px #0008}.position{left:18px;top:18px}.position b{font-size:30px}.lap{right:18px;top:18px;text-align:right}.speed{left:50%;bottom:22px;transform:translateX(-50%);text-align:center;background:none}.speed b{font-size:58px;font-style:italic}.speed span{display:block;font-size:11px;letter-spacing:3px}.energy{right:18px;bottom:22px;width:220px}.meter{height:8px;background:#25303a;margin-top:6px}.meter i{display:block;height:100%;background:linear-gradient(90deg,#27d6ff,#35ef9d);width:85%}.map{left:18px;bottom:18px;width:190px;height:145px}.map svg{width:100%;height:105px}.help{left:50%;top:18px;transform:translateX(-50%);font-size:11px;letter-spacing:1px}.count{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:bold 100px Arial;text-shadow:0 0 30px #ff3158;pointer-events:none}.result{display:none;position:absolute;inset:0;background:#05080ddd;align-items:center;justify-content:center}.result-card{width:520px;padding:28px;background:#0d141c;border:1px solid #3a4857;border-top:4px solid #ff3158;text-align:center}.result h1{font-size:36px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:20px 0}.stat{padding:12px;background:#151d26}.lesson{padding:14px;text-align:left;background:#101c1a;border-left:3px solid #35e69a;color:#cce6dc}.result button{pointer-events:auto;margin:16px 5px 0;padding:12px 18px;background:#ff3158;color:#fff;border:0;font-weight:bold;cursor:pointer}
</style><script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.164.1/build/three.module.js"}}</script></head><body><div id="game"></div><div class="hud"><div class="box position">POSITION<br><b id="pos">1 / 7</b></div><div class="box lap">LAP<br><b id="lap">1 / 3</b></div><div class="box help">W 가속 · S 브레이크 · A/D 조향</div><div class="speed"><b id="speed">0</b><span>KM / H</span></div><div class="box energy">ERS <span id="ersText">85%</span><div class="meter"><i id="ers"></i></div><small>DRS · FUTURE UPDATE</small></div><div class="box map"><b>MINIMAP</b><svg viewBox="0 0 180 100"><path d="M22 76C3 56 17 23 42 22L132 8c35-5 47 22 24 37-18 12-39-3-48 13-8 15 32 15 19 29-16 15-54-8-75 3-12 5-22-4-30-14Z" fill="none" stroke="#657382" stroke-width="6"/><circle id="mapPlayer" r="5" fill="#ff3158"/><g id="mapAI"></g></svg></div></div><div class="count" id="count">3</div><div class="result" id="result"><div class="result-card"><h1>🏁 RACE FINISHED</h1><h2 id="finishPos">1 / 7</h2><div class="stats"><div class="stat">BEST LAP<br><b id="best">--:--.---</b></div><div class="stat">TOP SPEED<br><b id="top">0 km/h</b></div><div class="stat">LAPS<br><b>3</b></div></div><div class="lesson" id="lesson"></div><button onclick="location.reload()">다시 레이스</button><button onclick="window.parent.location.href='/'">Garage로 돌아가기</button></div></div>
<script type="module">import * as THREE from 'three';const DATA=__RACE_DATA__;const root=document.getElementById('game'),scene=new THREE.Scene();scene.background=new THREE.Color(0x071019);scene.fog=new THREE.Fog(0x071019,45,145);const camera=new THREE.PerspectiveCamera(62,innerWidth/innerHeight,.1,400),renderer=new THREE.WebGLRenderer({antialias:true});renderer.setSize(innerWidth,innerHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;root.appendChild(renderer.domElement);scene.add(new THREE.HemisphereLight(0xb8dfff,0x182018,2));const sun=new THREE.DirectionalLight(0xffffff,3);sun.position.set(20,35,10);sun.castShadow=true;scene.add(sun);
// 여러 종류의 코너가 생기도록 중심선을 Catmull-Rom 곡선으로 만듭니다.
const pts=[[-34,0,30],[-52,0,5],[-42,0,-34],[-5,0,-45],[38,0,-42],[54,0,-15],[32,0,2],[47,0,24],[20,0,44],[-8,0,29],[-34,0,30]].map(p=>new THREE.Vector3(...p));const curve=new THREE.CatmullRomCurve3(pts,true,'catmullrom',.25),samples=500,roadWidth=9,vertices=[],indices=[];for(let i=0;i<=samples;i++){const t=i/samples,p=curve.getPointAt(t),tan=curve.getTangentAt(t),side=new THREE.Vector3(-tan.z,0,tan.x);vertices.push(p.x+side.x*roadWidth,p.y,p.z+side.z*roadWidth,p.x-side.x*roadWidth,p.y,p.z-side.z*roadWidth);if(i<samples){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2)}}const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.setIndex(indices);geo.computeVertexNormals();const road=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:0x20262c,roughness:.88}));road.receiveShadow=true;scene.add(road);const ground=new THREE.Mesh(new THREE.PlaneGeometry(250,250),new THREE.MeshStandardMaterial({color:0x16251b}));ground.rotation.x=-Math.PI/2;ground.position.y=-.08;scene.add(ground);
function makeCar(color,appearance={}){const g=new THREE.Group(),bodyMat=new THREE.MeshStandardMaterial({color,metalness:.55,roughness:.28}),dark=new THREE.MeshStandardMaterial({color:0x080a0c,roughness:.7});const body=new THREE.Mesh(new THREE.BoxGeometry(1.45,.48,3.5),bodyMat);body.position.y=.6;g.add(body);const nose=new THREE.Mesh(new THREE.ConeGeometry(.48,2.8,18),bodyMat);nose.rotation.x=Math.PI/2;nose.position.set(0,.52,-2.7);g.add(nose);const tyreColor={soft:0xed2939,medium:0xffd326,hard:0xf2f4f6}[appearance.tyres]||0xffd326;[[-1.05,-1.25],[1.05,-1.25],[-1.05,1.3],[1.05,1.3]].forEach(([x,z])=>{const w=new THREE.Mesh(new THREE.CylinderGeometry(.48,.48,.38,18),dark);w.rotation.z=Math.PI/2;w.position.set(x,.42,z);g.add(w);const stripe=new THREE.Mesh(new THREE.TorusGeometry(.48,.035,8,24),new THREE.MeshBasicMaterial({color:tyreColor}));stripe.rotation.y=Math.PI/2;stripe.position.set(x,.42,z);g.add(stripe)});const fs={low:1.5,balanced:1.9,high:2.25}[appearance.frontWing]||1.9,rs={low:1.25,balanced:1.65,high:2.0}[appearance.rearWing]||1.65;const fw=new THREE.Mesh(new THREE.BoxGeometry(fs,.1,.35),bodyMat);fw.position.set(0,.28,-3.65);g.add(fw);const rw=new THREE.Mesh(new THREE.BoxGeometry(rs,.15,.35),bodyMat);rw.position.set(0,1.1,2.15);g.add(rw);g.traverse(o=>{if(o.isMesh)o.castShadow=true});return g}
const player=makeCar(0xff1748,DATA.player.appearance);scene.add(player);const ai=DATA.ai.map((d,i)=>{const car=makeCar(parseInt(d.color.slice(1),16),{frontWing:d.config.front_wing,rearWing:d.config.rear_wing,tyres:d.config.tyres});scene.add(car);return{...d,car,progress:(i+1)*-.004,lap:0,total:0}});let pos=curve.getPointAt(0),heading=Math.atan2(curve.getTangentAt(0).x,curve.getTangentAt(0).z),speed=0,progress=0,lastProgress=0,lap=0,started=false,finished=false,ers=85,topSpeed=0,lapStart=performance.now(),best=Infinity;player.position.copy(pos);const keys={};addEventListener('keydown',e=>{keys[e.key.toLowerCase()]=true;e.preventDefault()});addEventListener('keyup',e=>keys[e.key.toLowerCase()]=false);
function nearestProgress(p,around){let bestT=around,bestD=Infinity;for(let j=-12;j<=12;j++){let t=(around+j/samples+1)%1,d=curve.getPointAt(t).distanceToSquared(p);if(d<bestD){bestD=d;bestT=t}}return[bestT,Math.sqrt(bestD)]}
function updatePlayer(dt){const ph=DATA.physics,max=ph.maxSpeed*(1-ph.downforce*.07);if(keys.w)speed+=ph.acceleration*dt;if(keys.s)speed-=ph.brakePower*dt;speed-=Math.sign(speed)*Math.min(Math.abs(speed),.16*dt);speed=THREE.MathUtils.clamp(speed,-max*.3,max);const steering=(keys.a?1:0)-(keys.d?1:0),speedRatio=Math.min(1,Math.abs(speed)/max),slip=1-(1-ph.grip)*speedRatio;heading+=steering*ph.steering*dt*(.25+speedRatio)*Math.sign(speed||1)*slip;player.rotation.y=heading;player.position.x+=Math.sin(heading)*speed*dt*12;player.position.z+=Math.cos(heading)*speed*dt*12;const found=nearestProgress(player.position,progress);lastProgress=progress;progress=found[0];if(found[1]>roadWidth*.82)speed*=Math.pow(.91,dt*60);if(lastProgress>.9&&progress<.1){lap++;const now=performance.now(),lt=now-lapStart;best=Math.min(best,lt);lapStart=now;if(lap>=DATA.laps)finish()}if(lastProgress<.1&&progress>.9)lap=Math.max(0,lap-1);const kmh=Math.max(0,speed/max*(255+DATA.player.performance.topSpeed*.75));topSpeed=Math.max(topSpeed,kmh);document.getElementById('speed').textContent=Math.round(kmh);document.getElementById('lap').textContent=Math.min(lap+1,DATA.laps)+' / '+DATA.laps;ers=Math.min(100,ers+dt*.5);document.getElementById('ers').style.width=ers+'%';document.getElementById('ersText').textContent=Math.round(ers)+'%'}
function updateAI(dt,time){ai.forEach((a,i)=>{const p=a.performance,curveAhead=curve.getTangentAt((a.progress+.012)%1),curveNow=curve.getTangentAt(a.progress%1),turn=curveAhead.angleTo(curveNow),cornerFactor=Math.max(.48,1-turn*2.8),base=(.072+p.topSpeed*.00042)*a.skill,target=base*cornerFactor*(.72+p.cornering*.0035);a.progress+=target*dt;if(a.progress>=1){a.progress-=1;a.lap++}a.total=a.lap+a.progress;const lane=(i%3-1)*1.5,point=curve.getPointAt(a.progress),tan=curve.getTangentAt(a.progress),side=new THREE.Vector3(-tan.z,0,tan.x);a.car.position.copy(point).addScaledVector(side,lane);a.car.position.y=.05;a.car.rotation.y=Math.atan2(tan.x,tan.z)})}
function updateCamera(dt){const forward=new THREE.Vector3(Math.sin(heading),0,Math.cos(heading)),desired=player.position.clone().addScaledVector(forward,-8-Math.abs(speed)*1.2).add(new THREE.Vector3(0,4.2,0));camera.position.lerp(desired,1-Math.pow(.002,dt));camera.lookAt(player.position.clone().addScaledVector(forward,5).add(new THREE.Vector3(0,1,0)));camera.fov=62+Math.abs(speed)*4;camera.updateProjectionMatrix()}
function hud(){const total=lap+progress,place=1+ai.filter(a=>a.total>total).length;document.getElementById('pos').textContent=place+' / 7';const mp=document.getElementById('mapPlayer'),pt=curve.getPointAt(progress);mp.setAttribute('cx',90+pt.x*1.25);mp.setAttribute('cy',52+pt.z*.85);return place}function fmt(ms){if(!isFinite(ms))return'--:--.---';const m=Math.floor(ms/60000),s=Math.floor(ms%60000/1000),x=Math.floor(ms%1000);return`${m}:${String(s).padStart(2,'0')}.${String(x).padStart(3,'0')}`}
function finish(){finished=true;const place=hud();document.getElementById('result').style.display='flex';document.getElementById('finishPos').textContent=place+' / 7';document.getElementById('best').textContent=fmt(best);document.getElementById('top').textContent=Math.round(topSpeed)+' km/h';const p=DATA.player.performance;document.getElementById('lesson').textContent=p.downforce>p.topSpeed?'이번 차량은 다운포스가 높아 코너에서 안정적이지만 직선 최고속도에서는 손해를 볼 수 있어요.':'이번 차량은 직선 속도에 유리하지만 다운포스가 낮다면 코너에서 더 조심스럽게 조향해야 해요.'}
let previous=performance.now(),count=3;const counter=document.getElementById('count');const timer=setInterval(()=>{count--;if(count>0)counter.textContent=count;else if(count===0)counter.textContent='GO!';else{counter.style.display='none';started=true;lapStart=performance.now();clearInterval(timer)}},900);function loop(now){requestAnimationFrame(loop);const dt=Math.min(.033,(now-previous)/1000);previous=now;if(started&&!finished){updatePlayer(dt);updateAI(dt,now);hud()}updateCamera(dt);renderer.render(scene,camera)}loop(previous);addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)})</script></body></html>'''


if __name__ == "__main__":
    main()
