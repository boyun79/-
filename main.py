"""F1 Physics Garage

실행: streamlit run main.py
필수 패키지: streamlit
3D 렌더링은 Streamlit 안의 Three.js 웹 컴포넌트가 담당합니다.
"""

import html
import json
from copy import deepcopy

import streamlit as st
import streamlit.components.v1 as components


# -----------------------------------------------------------------------------
# 1. 학습 데이터
# -----------------------------------------------------------------------------
METRICS = ["다운포스", "최고속도", "코너링", "그립", "제동", "안정성"]
METRIC_ENGLISH = {
    "다운포스": "DOWNFORCE", "최고속도": "TOP SPEED", "코너링": "CORNERING",
    "그립": "GRIP", "제동": "BRAKING", "안정성": "STABILITY",
}
PHYSICS_HELP = {
    "다운포스": ("차를 트랙 쪽으로 눌러주는 힘", "달릴 때 공기를 이용해 차를 트랙 쪽으로 눌러요. 커지면 코너에서 안정적이지만 공기저항도 커질 수 있어요."),
    "최고속도": ("직선에서 낼 수 있는 속도", "엔진 힘이 크고 공기저항이 작을수록 유리해요. 큰 윙은 코너에는 좋지만 직선 속도를 낮출 수 있어요."),
    "코너링": ("코너를 빠르고 안정적으로 도는 능력", "다운포스, 타이어 그립, 서스펜션이 함께 만드는 종합 성능이에요."),
    "그립": ("타이어가 노면을 붙잡는 힘", "그립이 좋으면 가속·코너링·제동 중 차가 덜 미끄러져요."),
    "제동": ("짧고 안정적으로 감속하는 능력", "브레이크 마찰력뿐 아니라 타이어 그립과 차량 무게도 제동 거리에 영향을 줘요."),
    "안정성": ("차의 움직임을 예측하기 쉬운 정도", "차가 갑자기 미끄러지거나 흔들리지 않고 운전자의 조작에 일정하게 반응하는 정도예요."),
}


def make_option(label, scores, stars, color, explanation, shape=1.0):
    """모든 옵션을 같은 구조로 저장해 새 파츠 추가를 쉽게 합니다."""
    return {"label": label, "scores": scores, "stars": stars, "color": color,
            "explanation": explanation, "shape": shape}


def get_part_data():
    """파츠별 옵션·성능·3D 색상·쉬운 물리 설명을 반환합니다."""
    return {
        "front_wing": {"name": "Front Wing", "ko": "프론트 윙", "icon": "⌁", "part": "frontWing",
            "options": {
                "low": make_option("LOW DRAG", [48, 94, 57, 61, 60, 62], [2,5,2], "#27d6ff", "윙 각도를 줄여 공기를 덜 막아요. 직선은 빨라지지만 앞바퀴를 누르는 힘은 작아져요.", .82),
                "balanced": make_option("BALANCED", [72, 77, 76, 72, 67, 76], [4,4,4], "#ffb21a", "다운포스와 직선 속도를 고르게 맞춘 설정이에요.", 1.0),
                "high": make_option("HIGH DOWNFORCE", [94, 55, 92, 79, 72, 84], [5,2,5], "#ff3158", "큰 윙이 앞쪽을 강하게 눌러 코너 진입은 좋아지지만 공기저항이 커져요.", 1.18)}},
        "rear_wing": {"name": "Rear Wing", "ko": "리어 윙", "icon": "≋", "part": "rearWing",
            "options": {
                "low": make_option("LOW DRAG", [45, 96, 54, 59, 58, 56], [2,5,2], "#27d6ff", "작은 리어 윙은 직선에 유리하지만 빠른 코너에서 차 뒤쪽이 가벼워질 수 있어요.", .78),
                "balanced": make_option("BALANCED", [73, 76, 76, 70, 64, 78], [4,4,4], "#ffb21a", "직선 속도와 뒤쪽 안정성을 고르게 맞췄어요.", 1.0),
                "high": make_option("HIGH DOWNFORCE", [96, 51, 93, 77, 69, 94], [5,2,5], "#ff3158", "큰 리어 윙은 차 뒤를 강하게 눌러 코너에 유리하지만 공기를 더 많이 막아요.", 1.25)}},
        "tyres": {"name": "Tyres", "ko": "타이어", "icon": "◉", "part": "tyres",
            "options": {
                "soft": make_option("SOFT", [66, 80, 92, 98, 91, 71], [4,4,5], "#ed2939", "부드러운 고무가 노면에 잘 달라붙어 그립이 높지만 실제 경기에서는 빨리 닳아요."),
                "medium": make_option("MEDIUM", [63, 81, 80, 82, 82, 82], [4,4,4], "#ffd326", "그립과 내구성의 균형을 잡은 타이어예요."),
                "hard": make_option("HARD", [60, 82, 68, 70, 73, 89], [3,4,3], "#f4f5f6", "단단해 오래 쓰기 좋지만 즉각적인 그립은 낮아요.")}},
        "brakes": {"name": "Brakes", "ko": "브레이크", "icon": "⊙", "part": "brakes",
            "options": {
                "race": make_option("RACE CARBON", [62, 78, 78, 76, 98, 78], [4,4,5], "#ff5038", "뜨거운 상태에서도 큰 마찰력으로 강하게 감속해요."),
                "balanced": make_option("BALANCED", [61, 80, 76, 74, 84, 88], [4,4,4], "#ffb21a", "제동력과 다루기 쉬운 반응을 함께 고려했어요."),
                "light": make_option("LIGHTWEIGHT", [59, 85, 75, 72, 75, 72], [3,5,3], "#27d6ff", "가벼워 반응은 좋지만 반복되는 강한 제동에는 불리해요.")}},
        "suspension": {"name": "Suspension", "ko": "서스펜션", "icon": "⌇", "part": "suspension",
            "options": {
                "stiff": make_option("STIFF", [73, 80, 91, 80, 77, 67], [4,4,5], "#ff3158", "차체 움직임이 작아 빠른 코너 반응이 좋아요. 울퉁불퉁한 노면에서는 불리할 수 있어요."),
                "balanced": make_option("BALANCED", [68, 81, 82, 82, 80, 88], [4,4,4], "#ffb21a", "반응성과 노면을 따라가는 능력의 균형을 맞췄어요."),
                "soft": make_option("SOFT", [62, 78, 72, 88, 83, 90], [3,4,4], "#27d6ff", "바퀴가 노면 굴곡을 잘 따라가지만 방향 전환은 조금 느려져요.")}},
        "floor": {"name": "Floor", "ko": "플로어", "icon": "▰", "part": "floor",
            "options": {
                "venturi": make_option("VENTURI", [98, 72, 94, 80, 67, 82], [5,3,5], "#9a62ff", "차 밑 공기를 빠르게 흘려 압력을 낮추고 차를 아래로 끌어당겨요."),
                "balanced": make_option("BALANCED", [81, 80, 83, 75, 66, 87], [4,4,4], "#ffb21a", "차 높이가 조금 변해도 안정적으로 다운포스를 만들어요."),
                "light": make_option("LIGHTWEIGHT", [60, 89, 68, 67, 62, 69], [3,5,3], "#27d6ff", "다운포스를 일부 포기하고 저항과 무게를 줄인 설정이에요.")}},
        "diffuser": {"name": "Diffuser", "ko": "디퓨저", "icon": "⋙", "part": "diffuser",
            "options": {
                "large": make_option("LARGE EXIT", [93, 67, 90, 76, 65, 87], [5,3,5], "#9a62ff", "차 밑의 빠른 공기를 뒤에서 부드럽게 넓혀 바닥 다운포스를 강화해요.", 1.2),
                "balanced": make_option("BALANCED", [77, 80, 79, 71, 64, 83], [4,4,4], "#ffb21a", "다운포스와 공기 흐름 안정성을 절충했어요.", 1.0),
                "compact": make_option("COMPACT", [55, 91, 63, 61, 61, 68], [3,5,3], "#27d6ff", "크기가 작아 저항은 낮지만 바닥 다운포스가 줄어요.", .78)}},
        "engine": {"name": "Engine", "ko": "엔진", "icon": "⚙", "part": "engine",
            "options": {
                "power": make_option("MAX POWER", [62, 99, 82, 72, 62, 70], [3,5,4], "#ff3158", "출력이 커 직선과 가속에 유리하지만 냉각과 안정성 부담이 커져요."),
                "balanced": make_option("BALANCED", [62, 88, 80, 72, 64, 87], [3,4,4], "#ffb21a", "출력과 신뢰성을 고르게 맞춘 파워 유닛이에요."),
                "efficient": make_option("EFFICIENT", [60, 82, 79, 72, 65, 92], [3,4,4], "#27d6ff", "최고 출력보다 효율과 일정한 성능에 집중했어요.")}},
        "ers": {"name": "ERS", "ko": "에너지 회수", "icon": "ϟ", "part": "ers",
            "options": {
                "attack": make_option("ATTACK", [60, 97, 82, 71, 65, 70], [3,5,4], "#32f59b", "저장한 전기 에너지를 빠르게 사용해 순간 가속을 높여요."),
                "balanced": make_option("BALANCED", [61, 88, 80, 71, 68, 86], [3,4,4], "#ffb21a", "전기 에너지 사용과 회수를 균형 있게 관리해요."),
                "recovery": make_option("RECOVERY", [60, 80, 76, 70, 78, 91], [3,4,4], "#27d6ff", "감속할 때 운동 에너지를 전기로 더 많이 되찾아요.")}},
    }


# -----------------------------------------------------------------------------
# 2. 성능 계산
# -----------------------------------------------------------------------------
def calculate_car_performance(parts, selections):
    """선택한 모든 파츠 점수의 평균으로 이해하기 쉬운 게임 지표를 만듭니다."""
    totals = {metric: 0 for metric in METRICS}
    for part_key, option_key in selections.items():
        option_scores = parts[part_key]["options"][option_key]["scores"]
        for metric, score in zip(METRICS, option_scores):
            totals[metric] += score
    return {metric: round(total / len(selections)) for metric, total in totals.items()}


def calculate_performance_difference(current, previous):
    """직전 설정과 현재 설정을 비교해 상승·하락 방향을 계산합니다."""
    if previous is None:
        return {metric: 0 for metric in METRICS}
    return {metric: current[metric] - previous[metric] for metric in METRICS}


# -----------------------------------------------------------------------------
# 3. 화면 스타일
# -----------------------------------------------------------------------------
def apply_game_css():
    """Streamlit 기본 화면을 단순한 F1 Garage 게임 화면으로 바꿉니다."""
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@500;600;700&family=Noto+Sans+KR:wght@400;600;700&display=swap');
    :root{--bg:#080b10;--panel:#10151d;--line:#27313d;--muted:#8290a0;--red:#ff3158;--cyan:#27d6ff}
    .stApp{background:radial-gradient(circle at 52% 17%,#202a36 0,#090c11 47%,#05070a 100%);color:#eef3f8}
    .block-container{max-width:1680px;padding:1rem 1.4rem 2rem}.stApp,button{font-family:'Noto Sans KR',sans-serif}
    h1,h2,h3,.race{font-family:'Oxanium','Noto Sans KR',sans-serif}header,#MainMenu,footer{visibility:hidden}
    .garage-head{display:flex;align-items:center;justify-content:space-between;border-top:3px solid var(--red);border-bottom:1px solid var(--line);padding:10px 16px;background:#0c1118;margin-bottom:10px}
    .logo{font:700 25px 'Oxanium';letter-spacing:2px}.logo b{color:var(--red)}.step{font:600 11px 'Oxanium';color:#8794a3;letter-spacing:2px}
    .intro{display:flex;gap:22px;align-items:center;padding:9px 15px;margin-bottom:12px;background:#10161ed9;border:1px solid #27313d;color:#c5cfda;font-size:12px}.intro strong{color:#fff;font:700 14px 'Oxanium'}
    .section-label{font:700 12px 'Oxanium';letter-spacing:2px;color:#9aa7b5;border-bottom:1px solid #27313d;padding-bottom:9px;margin-bottom:8px}
    div.stButton>button{width:100%;min-height:44px;text-align:left;background:#10161e;border:1px solid #27313d;color:#dbe3eb;border-radius:4px;font-weight:700}
    div.stButton>button:hover{border-color:#27d6ff;color:#fff;background:#15202a;box-shadow:inset 3px 0 #27d6ff}
    .active-part{border-left:3px solid var(--red);background:#181f29;padding:10px 12px;margin:4px 0 10px;font:700 13px 'Oxanium';color:#fff}
    .perf{padding:9px 0}.perf-top{display:flex;justify-content:space-between;align-items:end}.perf-name{font:700 13px 'Oxanium';color:#fff}.perf-help{font-size:10px;color:#8290a0;margin-top:2px}.perf-num{font:700 19px 'Oxanium'}
    .track{height:8px;background:#242d38;margin-top:7px;overflow:hidden;transform:skewX(-14deg)}.fill{height:100%;background:linear-gradient(90deg,#27d6ff,#8a68ff)}
    .up{color:#37eca0}.down{color:#ff5872}.same{color:#6e7b89}.why{margin:12px 0;padding:11px;border-left:3px solid #27d6ff;background:#0c131b;color:#c9d4de;font-size:12px;line-height:1.55}
    .option-card{border:1px solid #2a3542;background:#0d1219;padding:10px;margin:7px 0}.option-title{font:700 13px 'Oxanium';color:#fff}.stars{color:#ffc52e;letter-spacing:1px;font-size:12px}.option-mini{font-size:10px;color:#8491a0;margin-top:6px}
    .selected-option{border-color:#ff3158;box-shadow:inset 3px 0 #ff3158}.footnote{color:#718090;font-size:10px;margin-top:12px;line-height:1.5}
    @media(max-width:1000px){.intro{flex-wrap:wrap}.block-container{padding:.6rem}.garage-head{position:static}}
    </style>""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. 실제 WebGL 3D 차량
# -----------------------------------------------------------------------------
def build_3d_html(parts, selections, active_part):
    """Three.js로 회전·확대·레이캐스팅이 가능한 3D F1 차량을 만듭니다.

    차량은 평면 이미지가 아니라 여러 개의 곡면 3D 메시로 구성됩니다. 각 메시에는
    실제 파츠 이름을 저장해 두어 마우스 오버와 클릭을 구별할 수 있습니다.
    """
    visual = {}
    for key, selected in selections.items():
        option = parts[key]["options"][selected]
        visual[parts[key]["part"]] = {"color": option["color"], "shape": option["shape"], "key": key}
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>
    *{{box-sizing:border-box}}html,body,#app{{margin:0;width:100%;height:100%;overflow:hidden;background:#080b10;font-family:Arial,sans-serif}}
    #app{{background:radial-gradient(ellipse at 50% 42%,#273440 0,#10161e 49%,#07090d 80%)}}
    canvas{{display:block}}#hint{{position:absolute;left:18px;top:16px;color:#cbd5df;font-size:12px;background:#070a0ebd;border:1px solid #34404d;padding:8px 11px;pointer-events:none}}
    #badge{{position:absolute;right:18px;top:16px;color:#7f8c9a;font:11px monospace;letter-spacing:1px}}
    #info{{position:absolute;left:50%;bottom:18px;transform:translateX(-50%);min-width:300px;text-align:center;background:#070a0edb;border:1px solid #354251;border-top:2px solid #27d6ff;color:#fff;padding:9px 14px;opacity:0;transition:.15s;pointer-events:none}}
    #info b{{font-size:13px;letter-spacing:1px}}#info span{{display:block;color:#aab5c1;font-size:10px;margin-top:3px}}
    .label{{color:#dce6ef;background:#080b10d9;border:1px solid #3b4856;padding:4px 7px;font:bold 9px Arial;letter-spacing:.8px;white-space:nowrap;pointer-events:none}}
    .label.active{{color:#fff;border-color:#ff3158;box-shadow:0 0 12px #ff315888}}
    </style><script type='importmap'>{{"imports":{{"three":"https://unpkg.com/three@0.164.1/build/three.module.js","three/addons/":"https://unpkg.com/three@0.164.1/examples/jsm/"}}}}</script></head>
    <body><div id='app'></div><div id='hint'>DRAG 회전 · WHEEL 확대/축소 · PART 클릭</div><div id='badge'>REAL-TIME 3D / WEBGL</div><div id='info'></div>
    <script type='module'>
    import * as THREE from 'three';
    import {{OrbitControls}} from 'three/addons/controls/OrbitControls.js';
    import {{CSS2DRenderer,CSS2DObject}} from 'three/addons/renderers/CSS2DRenderer.js';
    const cfg={json.dumps(visual, ensure_ascii=False)}, active='{active_part}';
    const app=document.getElementById('app'), scene=new THREE.Scene();
    scene.fog=new THREE.Fog(0x080b10,16,34);
    const camera=new THREE.PerspectiveCamera(38,app.clientWidth/app.clientHeight,.1,100);camera.position.set(10,6.5,12);
    const renderer=new THREE.WebGLRenderer({{antialias:true,alpha:true}});renderer.setSize(app.clientWidth,app.clientHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.outputColorSpace=THREE.SRGBColorSpace;app.appendChild(renderer.domElement);
    const labels=new CSS2DRenderer();labels.setSize(app.clientWidth,app.clientHeight);labels.domElement.style.cssText='position:absolute;inset:0;pointer-events:none';app.appendChild(labels.domElement);
    const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=7;controls.maxDistance=24;controls.target.set(0,.4,0);controls.maxPolarAngle=Math.PI*.78;
    scene.add(new THREE.HemisphereLight(0xb9dcff,0x111216,2.0));const key=new THREE.DirectionalLight(0xffffff,3.4);key.position.set(6,10,5);key.castShadow=true;scene.add(key);const rim=new THREE.PointLight(0xff3158,32,18);rim.position.set(-6,3,-5);scene.add(rim);
    const platform=new THREE.Mesh(new THREE.CylinderGeometry(7.1,7.5,.25,96),new THREE.MeshStandardMaterial({{color:0x11171e,metalness:.75,roughness:.36}}));platform.position.y=-1.42;platform.receiveShadow=true;scene.add(platform);
    const ring=new THREE.Mesh(new THREE.TorusGeometry(6.65,.025,8,120),new THREE.MeshBasicMaterial({{color:0x27d6ff}}));ring.rotation.x=Math.PI/2;ring.position.y=-1.27;scene.add(ring);
    const car=new THREE.Group();car.rotation.y=-Math.PI/2;scene.add(car);const pickable=[], partGroups={{}};
    const mat=(color,metal=.45,rough=.32)=>new THREE.MeshStandardMaterial({{color,metalness:metal,roughness:rough}});
    function group(name){{const g=new THREE.Group();g.userData.part=name;partGroups[name]=g;car.add(g);return g}}
    function mesh(g,geo,material,pos=[0,0,0],rot=[0,0,0],scale=[1,1,1]){{const m=new THREE.Mesh(geo,material);m.position.set(...pos);m.rotation.set(...rot);m.scale.set(...scale);m.castShadow=true;m.receiveShadow=true;m.userData.part=g.userData.part;g.add(m);pickable.push(m);return m}}
    function capsule(length,radius){{return new THREE.CapsuleGeometry(radius,length,8,20)}}
    // 매끈한 곡면 차체: 길쭉한 캡슐과 유선형 노즈를 겹쳐 실제 포뮬러카 실루엣을 만듭니다.
    const body=group('body'), red=mat(0xd91536,.72,.24);mesh(body,capsule(3.1,.65),red,[0,.05,0],[Math.PI/2,0,0],[1,1,1]);mesh(body,new THREE.ConeGeometry(.62,4.5,32),red,[0,-.08,3.35],[Math.PI/2,0,0],[1,.55,1]);
    mesh(body,new THREE.SphereGeometry(1.0,32,18),red,[0,.05,-1.35],[0,0,0],[1.35,.78,1.75]);
    // 콕핏과 Halo
    const cockpit=group('cockpit');mesh(cockpit,new THREE.SphereGeometry(.64,28,16,0,Math.PI*2,0,Math.PI*.62),mat(0x111820,.15,.16),[0,.65,-.25],[0,0,0],[1,.62,1.45]);
    const haloMat=mat(0x242c35,.75,.2);mesh(cockpit,new THREE.TorusGeometry(.62,.055,10,36,Math.PI*1.25),haloMat,[0,1.08,-.05],[Math.PI/2,0,.39]);mesh(cockpit,new THREE.CylinderGeometry(.06,.06,.72,12),haloMat,[0,.82,.35],[0,0,0]);
    // 사이드포드: 앞은 넓고 뒤로 갈수록 좁아지는 곡면
    const side=group('sidepods');[-1,1].forEach(s=>{{mesh(side,capsule(1.35,.52),red,[s*1.02,-.05,-.65],[Math.PI/2,0,0],[1,.72,1.25]);mesh(side,new THREE.ConeGeometry(.48,2.2,24),red,[s*.94,-.08,-2.0],[-Math.PI/2,0,0],[.75,1,.9])}});
    // 타이어는 실제 회전축을 가진 두꺼운 Torus 3D 메시입니다.
    const tyres=group('tyres'), tyreMat=mat(0x08090b,.05,.72), stripe=mat(cfg.tyres.color,.15,.38);[[-1.55,1.95,.56], [1.55,1.95,.56],[-1.72,-2.15,.72],[1.72,-2.15,.72]].forEach(p=>{{const [x,z,r]=p;mesh(tyres,new THREE.TorusGeometry(r,r*.38,18,42),tyreMat,[x,-.35,z],[0,Math.PI/2,0]);mesh(tyres,new THREE.TorusGeometry(r*.99,.035,8,48),stripe,[x,-.35,z],[0,Math.PI/2,0])}});
    // 프론트 윙: 날개 단면을 가진 여러 곡선형 엘리먼트
    const fw=group('frontWing'), fwM=mat(cfg.frontWing.color,.65,.22), f=cfg.frontWing.shape;[-.16,.12].forEach((y,i)=>mesh(fw,new THREE.CapsuleGeometry(.11,3.2*f,6,20),fwM,[0,-.58+y,3.62-i*.25],[0,0,Math.PI/2],[1,1,1]));[-1,1].forEach(s=>mesh(fw,new THREE.ExtrudeGeometry(new THREE.Shape().moveTo(0,0).lineTo(.44,.12).lineTo(.28,.65).lineTo(0,.52),{{depth:.06,bevelEnabled:true,bevelSize:.025,bevelThickness:.025}}),fwM,[s*1.75*f,-.88,3.35],[0,s<0?0:Math.PI,0]));
    // 리어 윙: 선택에 따라 폭과 높이가 실제로 변합니다.
    const rw=group('rearWing'), rwM=mat(cfg.rearWing.color,.68,.2), r=cfg.rearWing.shape;mesh(rw,new THREE.CapsuleGeometry(.16,2.55*r,6,20),rwM,[0,1.05,-3.24],[0,0,Math.PI/2]);mesh(rw,new THREE.CapsuleGeometry(.09,2.35*r,6,20),rwM,[0,.72,-3.0],[0,0,Math.PI/2]);[-1,1].forEach(s=>mesh(rw,new THREE.CylinderGeometry(.045,.06,1.3,10),rwM,[s*.92*r,.35,-3.05],[0,0,0]));
    const floor=group('floor');const floorShape=new THREE.Shape().moveTo(-1.25,-2.7).lineTo(-1.25,1.4).lineTo(-.8,2.8).lineTo(.8,2.8).lineTo(1.25,1.4).lineTo(1.25,-2.7).lineTo(-1.25,-2.7);mesh(floor,new THREE.ExtrudeGeometry(floorShape,{{depth:.09,bevelEnabled:true,bevelSize:.04,bevelThickness:.03}}),mat(cfg.floor.color,.7,.25),[0,-.92,0],[Math.PI/2,0,0]);
    const diffuser=group('diffuser'), dm=mat(cfg.diffuser.color,.72,.22);[-.72,-.24,.24,.72].forEach(x=>mesh(diffuser,new THREE.BoxGeometry(.055,.7,1.35*cfg.diffuser.shape),dm,[x,-.62,-3.08],[.38,0,0]));
    const brakes=group('brakes');[[-1.55,1.95],[1.55,1.95],[-1.72,-2.15],[1.72,-2.15]].forEach(p=>mesh(brakes,new THREE.CylinderGeometry(.32,.32,.06,24),mat(cfg.brakes.color,.8,.28),[p[0],-.35,p[1]],[0,0,Math.PI/2]));
    const suspension=group('suspension');[1.95,-2.15].forEach(z=>[-1,1].forEach(s=>{{mesh(suspension,new THREE.CylinderGeometry(.025,.025,1.35,8),mat(cfg.suspension.color,.8,.2),[s*.82,-.34,z],[0,0,s*.85])}}));
    const engine=group('engine');mesh(engine,new THREE.CapsuleGeometry(.42,1.2,8,18),mat(cfg.engine.color,.65,.24),[0,.22,-1.75],[Math.PI/2,0,0]);
    const ers=group('ers');mesh(ers,new THREE.TorusGeometry(.24,.055,10,28),mat(cfg.ers.color,.5,.15),[0,.68,-1.38],[Math.PI/2,0,0]);
    const names={{frontWing:'FRONT WING',rearWing:'REAR WING',tyres:'TYRES',brakes:'BRAKES',suspension:'SUSPENSION',floor:'FLOOR',diffuser:'DIFFUSER',engine:'ENGINE',ers:'ERS',cockpit:'COCKPIT',sidepods:'SIDEPOD'}};
    const labelPos={{frontWing:[0,.15,3.65],rearWing:[0,1.65,-3.15],tyres:[-2.2,.4,1.9],floor:[1.6,-.6,.1],diffuser:[1.4,.1,-3],engine:[0,1.2,-1.7],ers:[.8,1,-1.2],cockpit:[0,1.7,.1],sidepods:[1.65,.55,-.45]}};
    Object.entries(labelPos).forEach(([n,p])=>{{const d=document.createElement('div');d.className='label'+(cfg[n]?.key===active?' active':'');d.textContent=names[n];const l=new CSS2DObject(d);l.position.set(...p);partGroups[n]?.add(l)}});
    const ray=new THREE.Raycaster(),mouse=new THREE.Vector2(),info=document.getElementById('info');let hovered=null;
    function hit(e){{const rect=renderer.domElement.getBoundingClientRect();mouse.x=((e.clientX-rect.left)/rect.width)*2-1;mouse.y=-((e.clientY-rect.top)/rect.height)*2+1;ray.setFromCamera(mouse,camera);return ray.intersectObjects(pickable,false)[0]?.object||null}}
    renderer.domElement.addEventListener('pointermove',e=>{{const obj=hit(e);pickable.forEach(m=>m.material.emissive?.setHex(0));if(obj){{obj.material.emissive?.setHex(0x243344);hovered=obj.userData.part;renderer.domElement.style.cursor='pointer';info.style.opacity=1;info.innerHTML='<b>'+names[hovered]+'</b><span>클릭하면 설정 패널이 열립니다</span>'}}else{{hovered=null;renderer.domElement.style.cursor='grab';info.style.opacity=0}}}});
    renderer.domElement.addEventListener('click',()=>{{const key=cfg[hovered]?.key;if(key){{const u=new URL(window.parent.location.href);u.searchParams.set('part',key);window.parent.location.href=u.toString()}}}});
    window.addEventListener('resize',()=>{{camera.aspect=app.clientWidth/app.clientHeight;camera.updateProjectionMatrix();renderer.setSize(app.clientWidth,app.clientHeight);labels.setSize(app.clientWidth,app.clientHeight)}});
    function animate(){{requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);labels.render(scene,camera)}}animate();
    </script></body></html>"""


def render_3d_car(parts, selections, active_part):
    """중앙의 가장 큰 영역에 실제 WebGL 3D 뷰어를 삽입합니다."""
    components.html(build_3d_html(parts, selections, active_part), height=650, scrolling=False)


# -----------------------------------------------------------------------------
# 5. 게임 조작 패널
# -----------------------------------------------------------------------------
def render_help_message():
    """처음 온 사용자가 3초 안에 조작법을 이해하도록 짧게 안내합니다."""
    st.markdown("""<div class='intro'><strong>🏎 MY F1 CAR</strong><span>① 차량을 드래그해서 360°로 살펴보세요</span><span>② 부품을 클릭해 설정을 바꾸세요</span><span>③ 성능에 마우스를 올려 물리를 배워보세요</span></div>""", unsafe_allow_html=True)


def render_part_menu(parts, active_part):
    """왼쪽에 파츠만 크게 표시하고, 클릭한 파츠를 활성화합니다."""
    st.markdown("<div class='section-label'>01 / PARTS</div>", unsafe_allow_html=True)
    for key, data in parts.items():
        if st.button(f"{data['icon']}   {data['name']}", key=f"menu_{key}", use_container_width=True):
            st.session_state.active_part = key
            st.query_params["part"] = key
            st.rerun()
    st.markdown(f"<div class='active-part'>SELECTED · {parts[active_part]['name'].upper()}</div>", unsafe_allow_html=True)


def stars(value):
    """숫자를 처음 보는 사용자도 빠르게 비교할 수 있도록 별점으로 바꿉니다."""
    return "★" * value + "☆" * (5 - value)


def render_part_detail(parts, active_part, selections):
    """선택한 파츠 옵션을 게임 카드처럼 보여 주고 버튼으로 교체합니다."""
    data = parts[active_part]
    st.markdown(f"<div class='section-label'>SETUP / {data['name'].upper()}</div>", unsafe_allow_html=True)
    for option_key, option in data["options"].items():
        selected_class = " selected-option" if selections[active_part] == option_key else ""
        st.markdown(f"""<div class='option-card{selected_class}'><div class='option-title'>{option['label']}</div>
        <div class='option-mini'>최고속도 <span class='stars'>{stars(option['stars'][1])}</span><br>다운포스 <span class='stars'>{stars(option['stars'][0])}</span><br>코너링 <span class='stars'>{stars(option['stars'][2])}</span></div></div>""", unsafe_allow_html=True)
        if st.button("장착됨 ✓" if selections[active_part] == option_key else "이 파츠 장착", key=f"equip_{active_part}_{option_key}", disabled=selections[active_part] == option_key, use_container_width=True):
            # 사용자가 옵션을 누르면 선택값을 저장하고 Streamlit 전체를 즉시 다시 계산합니다.
            st.session_state.selections[active_part] = option_key
            st.session_state.last_changed_part = active_part
            st.rerun()


def render_physics_tooltip(metric):
    """브라우저 기본 툴팁을 이용해 추가 라이브러리 없이 물리 설명을 제공합니다."""
    short, long_text = PHYSICS_HELP[metric]
    return f"<span title='{html.escape(long_text, quote=True)}' style='cursor:help'>{html.escape(short)} ⓘ</span>"


def render_performance_panel(performance, differences, changed_part, parts, selections):
    """오른쪽에는 핵심 성능만 크게 표시하고 변화 방향을 색으로 강조합니다."""
    st.markdown("<div class='section-label'>02 / CAR PERFORMANCE</div>", unsafe_allow_html=True)
    for metric in METRICS:
        value, difference = performance[metric], differences[metric]
        if difference > 0:
            delta = f"<span class='up'>↑ {difference}</span>"
        elif difference < 0:
            delta = f"<span class='down'>↓ {abs(difference)}</span>"
        else:
            delta = "<span class='same'>━</span>"
        st.markdown(f"""<div class='perf'><div class='perf-top'><div><div class='perf-name'>{METRIC_ENGLISH[metric]}</div><div class='perf-help'>{render_physics_tooltip(metric)}</div></div><div class='perf-num'>{value} {delta}</div></div><div class='track'><div class='fill' style='width:{value}%'></div></div></div>""", unsafe_allow_html=True)
    if changed_part:
        option = parts[changed_part]["options"][selections[changed_part]]
        st.markdown(f"<div class='why'><b>왜 변했나요?</b><br>{html.escape(option['explanation'])}</div>", unsafe_allow_html=True)
    st.markdown("<div class='footnote'>0~100은 실제 측정값이 아니라 물리적 경향을 쉽게 비교하기 위한 학습용 게임 지표입니다.</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. 메인 실행 흐름
# -----------------------------------------------------------------------------
def main():
    """데이터 준비 → 사용자 입력 → 계산 → 3D 및 UI 렌더링 순서로 앱을 실행합니다."""
    st.set_page_config(page_title="F1 Physics Garage 3D", page_icon="🏁", layout="wide", initial_sidebar_state="collapsed")
    apply_game_css()
    parts = get_part_data()

    # 첫 실행에서는 모든 파츠를 다루기 쉬운 균형형 설정으로 시작합니다.
    defaults = {key: list(data["options"].keys())[1] for key, data in parts.items()}
    if "selections" not in st.session_state:
        st.session_state.selections = defaults
    query_part = st.query_params.get("part")
    if query_part in parts:
        st.session_state.active_part = query_part
    if "active_part" not in st.session_state:
        st.session_state.active_part = "front_wing"
    if "last_changed_part" not in st.session_state:
        st.session_state.last_changed_part = None

    selections = st.session_state.selections
    active_part = st.session_state.active_part
    current_performance = calculate_car_performance(parts, selections)
    previous_performance = st.session_state.get("previous_performance")
    differences = calculate_performance_difference(current_performance, previous_performance)

    st.markdown("<div class='garage-head'><div class='logo'>F1 <b>PHYSICS</b> GARAGE</div><div class='step'>BUILD 02 · INTERACTIVE 3D SETUP</div></div>", unsafe_allow_html=True)
    render_help_message()

    left, center, right = st.columns([0.78, 2.45, 1.05], gap="medium")
    with left:
        render_part_menu(parts, active_part)
        render_part_detail(parts, active_part, selections)
    with center:
        st.markdown("<div class='section-label'>3D CAR / DRAG TO EXPLORE</div>", unsafe_allow_html=True)
        render_3d_car(parts, selections, active_part)
    with right:
        render_performance_panel(current_performance, differences, st.session_state.last_changed_part, parts, selections)

    # 이번 성능을 다음 재실행의 비교 기준으로 저장합니다.
    st.session_state.previous_performance = deepcopy(current_performance)
    st.session_state.last_changed_part = None


if __name__ == "__main__":
    main()
