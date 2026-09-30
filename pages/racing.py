"""F1 Physics Garage - Racing page

이 파일만 프로젝트의 pages/racing.py 위치에 복사하면 됩니다.
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
        # 모든 Garage 파츠를 3D 모델 생성기에 전달해 외형 차이를 실제 Mesh로 반영합니다.
        "appearance": {
            "frontWing": car_config.get("front_wing", "balanced"),
            "rearWing": car_config.get("rear_wing", "balanced"),
            "tyres": car_config.get("tyres", "medium"),
            "brakes": car_config.get("brakes", "balanced"),
            "suspension": car_config.get("suspension", "balanced"),
            "floor": car_config.get("floor", "balanced"),
            "diffuser": car_config.get("diffuser", "balanced"),
            "engine": car_config.get("engine", "balanced"),
            "ers": car_config.get("ers", "balanced"),
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
    .block-container{max-width:1500px;padding:1rem 1.4rem 2rem}
    .race-head{border-top:3px solid var(--red);border-bottom:1px solid var(--line);padding:12px 16px;background:#0c1118;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
    .race-logo{font:700 25px 'Oxanium';letter-spacing:2px}.race-logo b{color:var(--red)}.race-step{font:600 11px 'Oxanium';color:#8391a0;letter-spacing:2px}
    .panel{background:linear-gradient(145deg,#111821,#090d12);border:1px solid var(--line);padding:15px;min-height:100%}.panel-title{font:700 12px 'Oxanium';letter-spacing:2px;color:#9daab8;border-bottom:1px solid #293542;padding-bottom:9px;margin-bottom:12px}
    .track-card{height:330px;background:radial-gradient(circle,#1e2a34,#080c11);display:flex;align-items:center;justify-content:center;border:1px solid #2b3744}.track-svg{width:92%;height:92%}.track-line{fill:none;stroke:#59636e;stroke-width:30;stroke-linecap:round;stroke-linejoin:round}.track-edge{fill:none;stroke:#dce4eb;stroke-width:35;stroke-dasharray:3 7}.track-center{fill:none;stroke:#13191f;stroke-width:25}
    .car-card{text-align:center;padding:14px;background:#0b1016;border:1px solid #283440}.car-name{font:700 17px 'Oxanium';letter-spacing:2px}.config-chip{display:inline-block;margin:3px;padding:4px 7px;border:1px solid #344252;color:#9cabb9;font-size:10px}
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


def get_f1_car_builder_javascript():
    """준비 화면과 레이스가 함께 사용하는 입체 F1 차량 생성 코드를 반환합니다.

    차량은 HTML/CSS 그림이 아니라 Three.js Mesh, 재질, 조명에 반응하는
    실제 3차원 Geometry들로 구성됩니다.
    """
    return r"""
function createF1Car(color, appearance={}) {
  const car=new THREE.Group(); car.userData.wheels=[];
  const bodyMat=new THREE.MeshStandardMaterial({color,metalness:.72,roughness:.23});
  const carbon=new THREE.MeshStandardMaterial({color:0x11151a,metalness:.55,roughness:.35});
  const rubber=new THREE.MeshStandardMaterial({color:0x07080a,roughness:.82});
  const accent=new THREE.MeshStandardMaterial({color:0x27d6ff,metalness:.65,roughness:.22});
  function add(geometry,material,position=[0,0,0],rotation=[0,0,0],parent=car){
    const mesh=new THREE.Mesh(geometry,material);mesh.position.set(...position);mesh.rotation.set(...rotation);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh;
  }
  function rod(a,b,r=.035,material=carbon){const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b),mid=A.clone().add(B).multiplyScalar(.5);const m=add(new THREE.CylinderGeometry(r,r,A.distanceTo(B),10),material,[mid.x,mid.y,mid.z]);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.clone().sub(A).normalize());return m}
  // 유선형 모노코크, 노즈, 엔진 커버를 곡면 Geometry로 구성합니다.
  add(new THREE.CapsuleGeometry(.55,2.75,8,24),bodyMat,[0,.62,0],[Math.PI/2,0,0]);
  add(new THREE.ConeGeometry(.48,3.25,28),bodyMat,[0,.52,-2.65],[-Math.PI/2,0,0]);
  add(new THREE.SphereGeometry(.82,28,16),bodyMat,[0,.64,1.05],[0,0,0]).scale.set(1.22,.64,1.6);
  // 콕핏과 Halo
  add(new THREE.SphereGeometry(.56,24,14),carbon,[0,1.02,-.05],[0,0,0]).scale.set(1,.58,1.25);
  add(new THREE.TorusGeometry(.58,.055,10,32,Math.PI*1.35),carbon,[0,1.38,-.05],[Math.PI/2,0,.35]);
  rod([0,1.35,.35],[0,.92,.42],.055,carbon);
  // 사이드포드
  [-1,1].forEach(side=>{const pod=add(new THREE.CapsuleGeometry(.38,1.25,8,18),bodyMat,[side*.78,.5,.55],[Math.PI/2,0,0]);pod.scale.set(1,.76,1.1)});
  // 옵션별 플로어의 폭과 길이를 실제 Mesh 크기로 변경합니다.
  const floorScale={venturi:1.12,balanced:1,light:.88}[appearance.floor]||1;
  add(new THREE.BoxGeometry(2.25*floorScale,.10,4.65*floorScale),carbon,[0,.19,.25]);
  // 타이어는 회전 가능한 원통과 컴파운드 색 띠로 구성됩니다.
  const tyreRadius={soft:.53,medium:.50,hard:.47}[appearance.tyres]||.50;
  const tyreColor={soft:0xed2939,medium:0xffd326,hard:0xf2f4f6}[appearance.tyres]||0xffd326;
  [[-1.32,-1.55],[1.32,-1.55],[-1.43,1.42],[1.43,1.42]].forEach(([x,z],i)=>{
    const wheel=new THREE.Group();wheel.position.set(x,.5,z);car.add(wheel);car.userData.wheels.push(wheel);
    add(new THREE.CylinderGeometry(tyreRadius,tyreRadius,.40,28),rubber,[0,0,0],[0,0,Math.PI/2],wheel);
    add(new THREE.TorusGeometry(tyreRadius*.98,.035,8,36),new THREE.MeshBasicMaterial({color:tyreColor}),[x<0?-.205:.205,0,0],[0,Math.PI/2,0],wheel);
    const brakeSize={race:.34,balanced:.29,light:.25}[appearance.brakes]||.29;
    add(new THREE.CylinderGeometry(brakeSize,brakeSize,.045,24),new THREE.MeshStandardMaterial({color:0xff5438,metalness:.8,roughness:.3}),[0,0,0],[0,0,Math.PI/2],wheel);
  });
  // 앞·뒤 바퀴와 차체를 연결하는 여러 개의 서스펜션 암입니다.
  const arm={stiff:.052,balanced:.043,soft:.035}[appearance.suspension]||.043;
  [[-1.55,1.32],[1.42,1.43]].forEach(([z,wx])=>[-1,1].forEach(side=>{const hub=[side*wx,.5,z];rod([side*.52,.44,z-.38],hub,arm);rod([side*.52,.44,z+.38],hub,arm);rod([side*.48,.92,z],hub,arm*.85)}));
  // 프론트 윙은 옵션에 따라 폭과 플랩 수가 달라집니다.
  const fw={low:[2.55,1],balanced:[3.05,2],high:[3.55,3]}[appearance.frontWing]||[3.05,2];
  for(let i=0;i<fw[1];i++)add(new THREE.CapsuleGeometry(.09,fw[0],6,18),accent,[0,.27+i*.13,-4.05+i*.17],[0,0,Math.PI/2]);
  [-1,1].forEach(side=>add(new THREE.BoxGeometry(.08,.58,.72),accent,[side*fw[0]*.51,.45,-3.9]));
  // 리어 윙 역시 높이·폭·플랩 수가 설정에 따라 바뀝니다.
  const rw={low:[1.85,1,.95],balanced:[2.25,2,1.18],high:[2.65,3,1.42]}[appearance.rearWing]||[2.25,2,1.18];
  [-1,1].forEach(side=>rod([side*.72,.5,2.0],[side*.72,rw[2],2.2],.055,carbon));
  for(let i=0;i<rw[1];i++)add(new THREE.CapsuleGeometry(.10,rw[0],6,18),accent,[0,rw[2]+i*.17,2.22-i*.08],[0,0,Math.PI/2]);
  // 디퓨저 핀 수와 크기도 Garage 설정에 따라 달라집니다.
  const df={large:[6,1.05],balanced:[4,.82],compact:[3,.58]}[appearance.diffuser]||[4,.82];
  for(let i=0;i<df[0];i++){const x=-.85+i*(1.7/(df[0]-1));add(new THREE.BoxGeometry(.045,.52,df[1]),carbon,[x,.36,2.32],[.32,0,0])}
  // 엔진과 ERS는 상부의 입체 커버·발광 링으로 표현합니다.
  const engineScale={power:1.12,balanced:1,efficient:.88}[appearance.engine]||1;
  const engine=add(new THREE.CapsuleGeometry(.31,1.0*engineScale,8,18),bodyMat,[0,1.03,1.12],[Math.PI/2,0,0]);
  const ersColor={attack:0x32f59b,balanced:0xffb21a,recovery:0x27d6ff}[appearance.ers]||0xffb21a;
  add(new THREE.TorusGeometry(.22,.045,10,26),new THREE.MeshStandardMaterial({color:ersColor,emissive:ersColor,emissiveIntensity:1.2}),[0,1.38,.82],[Math.PI/2,0,0]);
  car.userData.rotateWheels=(amount)=>car.userData.wheels.forEach(w=>w.rotation.x-=amount);
  return car;
}
"""


def build_car_inspection_html(car_data):
    """OrbitControls로 360도 확인 가능한 실제 WebGL 차량 검사 화면을 만듭니다."""
    payload=json.dumps(car_data,ensure_ascii=False)
    builder=get_f1_car_builder_javascript()
    return f"""<!doctype html><html><head><style>*{{box-sizing:border-box}}html,body,#view{{margin:0;width:100%;height:100%;overflow:hidden;background:radial-gradient(circle,#263541,#080c11 72%)}}#tip{{position:absolute;left:12px;top:10px;color:#c8d3dd;font:11px Arial;background:#05080ca8;padding:7px 9px;border:1px solid #354554}}canvas{{display:block}}</style><script type='importmap'>{{"imports":{{"three":"https://unpkg.com/three@0.164.1/build/three.module.js","three/addons/":"https://unpkg.com/three@0.164.1/examples/jsm/"}}}}</script></head><body><div id='view'></div><div id='tip'>DRAG 360° · WHEEL ZOOM · GARAGE CAR</div><script type='module'>import * as THREE from 'three';import {{OrbitControls}} from 'three/addons/controls/OrbitControls.js';const DATA={payload},root=document.getElementById('view'),scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,root.clientWidth/root.clientHeight,.1,100);camera.position.set(8,5.2,9);const renderer=new THREE.WebGLRenderer({{antialias:true,alpha:true}});renderer.setSize(root.clientWidth,root.clientHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;root.appendChild(renderer.domElement);scene.add(new THREE.HemisphereLight(0xc9e6ff,0x101418,2.4));const key=new THREE.DirectionalLight(0xffffff,4);key.position.set(6,10,4);key.castShadow=true;scene.add(key);const rim=new THREE.PointLight(0xff3158,28,18);rim.position.set(-5,3,-4);scene.add(rim);{builder}const car=createF1Car(0xff1748,DATA.appearance);scene.add(car);const ground=new THREE.Mesh(new THREE.CylinderGeometry(6,6.3,.18,72),new THREE.MeshStandardMaterial({{color:0x111820,metalness:.55,roughness:.4}}));ground.position.y=-.02;ground.receiveShadow=true;scene.add(ground);const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.target.set(0,.75,0);controls.minDistance=5;controls.maxDistance=18;function loop(){{requestAnimationFrame(loop);controls.update();renderer.render(scene,camera)}}loop();addEventListener('resize',()=>{{camera.aspect=root.clientWidth/root.clientHeight;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,root.clientHeight)}})</script></body></html>"""


def render_car_preview_3d(car_data):
    """SVG 대신 PerspectiveCamera와 WebGLRenderer 기반 3D 차량을 표시합니다."""
    components.html(build_car_inspection_html(car_data),height=330,scrolling=False)


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
        st.markdown("<div class='panel-title'>02 / YOUR GARAGE CAR · REAL 3D</div>", unsafe_allow_html=True)
        render_car_preview_3d(car_data)
        st.markdown(f"<div class='car-card'><div class='car-name'>MY F1 CAR</div>{chips}</div>", unsafe_allow_html=True)
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
    return RACE_GAME_TEMPLATE.replace("__RACE_DATA__", payload).replace("__F1_CAR_BUILDER__", get_f1_car_builder_javascript())


def render_race_game(car_data, ai_cars):
    """Streamlit 안에 새로고침 없이 실행되는 JavaScript 레이싱 게임을 삽입합니다."""
    st.markdown("<div class='race-head'><div class='race-logo'>F1 PHYSICS <b>RACING</b></div><div class='race-step'>WASD DRIVE · ESC PAUSE</div></div>", unsafe_allow_html=True)
    components.html(build_race_game_html(car_data, ai_cars), height=820, scrolling=False)
    if st.button("← 레이스 준비 화면", use_container_width=True):
        st.session_state.race_started = False
        st.rerun()


def main():
    """차량 확인 → 준비 화면 → 실제 레이스 순서로 페이지 흐름을 관리합니다."""
    # Streamlit 기본 페이지 탐색 사이드바가 Racing에서도 항상 보이도록 expanded를 사용합니다.
    st.set_page_config(page_title="F1 Physics Racing", page_icon="🏁", layout="wide", initial_sidebar_state="expanded")
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
__F1_CAR_BUILDER__
const player=createF1Car(0xff1748,DATA.player.appearance);scene.add(player);const ai=DATA.ai.map((d,i)=>{const appearance={frontWing:d.config.front_wing,rearWing:d.config.rear_wing,tyres:d.config.tyres,brakes:d.config.brakes,suspension:d.config.suspension,floor:d.config.floor,diffuser:d.config.diffuser,engine:d.config.engine,ers:d.config.ers};const car=createF1Car(parseInt(d.color.slice(1),16),appearance);scene.add(car);return{...d,car,progress:(i+1)*-.004,lap:0,total:0}});let pos=curve.getPointAt(0),heading=Math.atan2(curve.getTangentAt(0).x,curve.getTangentAt(0).z),speed=0,progress=0,lastProgress=0,lap=0,started=false,finished=false,ers=85,topSpeed=0,lapStart=performance.now(),best=Infinity;player.position.copy(pos);const keys={};addEventListener('keydown',e=>{keys[e.key.toLowerCase()]=true;e.preventDefault()});addEventListener('keyup',e=>keys[e.key.toLowerCase()]=false);
function nearestProgress(p,around){let bestT=around,bestD=Infinity;for(let j=-12;j<=12;j++){let t=(around+j/samples+1)%1,d=curve.getPointAt(t).distanceToSquared(p);if(d<bestD){bestD=d;bestT=t}}return[bestT,Math.sqrt(bestD)]}
function updatePlayer(dt){const ph=DATA.physics,max=ph.maxSpeed*(1-ph.downforce*.07);if(keys.w)speed+=ph.acceleration*dt;if(keys.s)speed-=ph.brakePower*dt;speed-=Math.sign(speed)*Math.min(Math.abs(speed),.16*dt);speed=THREE.MathUtils.clamp(speed,-max*.3,max);const steering=(keys.a?1:0)-(keys.d?1:0),speedRatio=Math.min(1,Math.abs(speed)/max),slip=1-(1-ph.grip)*speedRatio;heading+=steering*ph.steering*dt*(.25+speedRatio)*Math.sign(speed||1)*slip;player.rotation.y=heading;player.position.x+=Math.sin(heading)*speed*dt*12;player.position.z+=Math.cos(heading)*speed*dt*12;player.userData.rotateWheels(speed*dt*8);const found=nearestProgress(player.position,progress);lastProgress=progress;progress=found[0];if(found[1]>roadWidth*.82)speed*=Math.pow(.91,dt*60);if(lastProgress>.9&&progress<.1){lap++;const now=performance.now(),lt=now-lapStart;best=Math.min(best,lt);lapStart=now;if(lap>=DATA.laps)finish()}if(lastProgress<.1&&progress>.9)lap=Math.max(0,lap-1);const kmh=Math.max(0,speed/max*(255+DATA.player.performance.topSpeed*.75));topSpeed=Math.max(topSpeed,kmh);document.getElementById('speed').textContent=Math.round(kmh);document.getElementById('lap').textContent=Math.min(lap+1,DATA.laps)+' / '+DATA.laps;ers=Math.min(100,ers+dt*.5);document.getElementById('ers').style.width=ers+'%';document.getElementById('ersText').textContent=Math.round(ers)+'%'}
function updateAI(dt,time){ai.forEach((a,i)=>{const p=a.performance,curveAhead=curve.getTangentAt((a.progress+.012)%1),curveNow=curve.getTangentAt(a.progress%1),turn=curveAhead.angleTo(curveNow),cornerFactor=Math.max(.48,1-turn*2.8),base=(.072+p.topSpeed*.00042)*a.skill,target=base*cornerFactor*(.72+p.cornering*.0035);a.progress+=target*dt;if(a.progress>=1){a.progress-=1;a.lap++}a.total=a.lap+a.progress;const lane=(i%3-1)*1.5,point=curve.getPointAt(a.progress),tan=curve.getTangentAt(a.progress),side=new THREE.Vector3(-tan.z,0,tan.x);a.car.position.copy(point).addScaledVector(side,lane);a.car.position.y=.05;a.car.rotation.y=Math.atan2(tan.x,tan.z);a.car.userData.rotateWheels(target*dt*55)})}
function updateCamera(dt){const forward=new THREE.Vector3(Math.sin(heading),0,Math.cos(heading)),desired=player.position.clone().addScaledVector(forward,-8-Math.abs(speed)*1.2).add(new THREE.Vector3(0,4.2,0));camera.position.lerp(desired,1-Math.pow(.002,dt));camera.lookAt(player.position.clone().addScaledVector(forward,5).add(new THREE.Vector3(0,1,0)));camera.fov=62+Math.abs(speed)*4;camera.updateProjectionMatrix()}
function hud(){const total=lap+progress,place=1+ai.filter(a=>a.total>total).length;document.getElementById('pos').textContent=place+' / 7';const mp=document.getElementById('mapPlayer'),pt=curve.getPointAt(progress);mp.setAttribute('cx',90+pt.x*1.25);mp.setAttribute('cy',52+pt.z*.85);return place}function fmt(ms){if(!isFinite(ms))return'--:--.---';const m=Math.floor(ms/60000),s=Math.floor(ms%60000/1000),x=Math.floor(ms%1000);return`${m}:${String(s).padStart(2,'0')}.${String(x).padStart(3,'0')}`}
function finish(){finished=true;const place=hud();document.getElementById('result').style.display='flex';document.getElementById('finishPos').textContent=place+' / 7';document.getElementById('best').textContent=fmt(best);document.getElementById('top').textContent=Math.round(topSpeed)+' km/h';const p=DATA.player.performance;document.getElementById('lesson').textContent=p.downforce>p.topSpeed?'이번 차량은 다운포스가 높아 코너에서 안정적이지만 직선 최고속도에서는 손해를 볼 수 있어요.':'이번 차량은 직선 속도에 유리하지만 다운포스가 낮다면 코너에서 더 조심스럽게 조향해야 해요.'}
let previous=performance.now(),count=3;const counter=document.getElementById('count');const timer=setInterval(()=>{count--;if(count>0)counter.textContent=count;else if(count===0)counter.textContent='GO!';else{counter.style.display='none';started=true;lapStart=performance.now();clearInterval(timer)}},900);function loop(now){requestAnimationFrame(loop);const dt=Math.min(.033,(now-previous)/1000);previous=now;if(started&&!finished){updatePlayer(dt);updateAI(dt,now);hud()}updateCamera(dt);renderer.render(scene,camera)}loop(previous);addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)})</script></body></html>'''


if __name__ == "__main__":
    main()
