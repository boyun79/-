"""F1 Physics Garage - 3D 자동 주행 시뮬레이션

이 파일만 pages/racing.py에 넣습니다. main.py는 수정하지 않습니다.
"""
import html
import json
from copy import deepcopy
import streamlit as st
import streamlit.components.v1 as components

CAR_CONFIG_KEY = "my_car_config"
CAR_PERFORMANCE_KEY = "my_car_performance"
GARAGE_FALLBACK_KEY = "selections"
TOTAL_LAPS = 3
METRICS = ["다운포스", "최고속도", "코너링", "그립", "제동", "안정성"]


def get_part_scores():
    """Garage와 동일한 옵션 점수입니다. 저장된 성능이 없을 때만 사용합니다."""
    return {
        "front_wing":{"low":[48,94,57,61,60,62],"balanced":[72,77,76,72,67,76],"high":[94,55,92,79,72,84]},
        "rear_wing":{"low":[45,96,54,59,58,56],"balanced":[73,76,76,70,64,78],"high":[96,51,93,77,69,94]},
        "tyres":{"soft":[66,80,92,98,91,71],"medium":[63,81,80,82,82,82],"hard":[60,82,68,70,73,89]},
        "brakes":{"race":[62,78,78,76,98,78],"balanced":[61,80,76,74,84,88],"light":[59,85,75,72,75,72]},
        "suspension":{"stiff":[73,80,91,80,77,67],"balanced":[68,81,82,82,80,88],"soft":[62,78,72,88,83,90]},
        "floor":{"venturi":[98,72,94,80,67,82],"balanced":[81,80,83,75,66,87],"light":[60,89,68,67,62,69]},
        "diffuser":{"large":[93,67,90,76,65,87],"balanced":[77,80,79,71,64,83],"compact":[55,91,63,61,61,68]},
        "engine":{"power":[62,99,82,72,62,70],"balanced":[62,88,80,72,64,87],"efficient":[60,82,79,72,65,92]},
        "ers":{"attack":[60,97,82,71,65,70],"balanced":[61,88,80,71,68,86],"recovery":[60,80,76,70,78,91]},
    }


def load_my_car():
    """Garage에서 만든 파츠와 성능을 그대로 읽습니다."""
    config=st.session_state.get(CAR_CONFIG_KEY) or st.session_state.get(GARAGE_FALLBACK_KEY)
    if not isinstance(config,dict): return None,None
    config=deepcopy(config)
    performance=st.session_state.get(CAR_PERFORMANCE_KEY)
    if not isinstance(performance,dict) or not all(k in performance for k in METRICS):
        performance=calculate_performance(config)
    return config,performance


def calculate_performance(config):
    """Garage 성능 저장값이 없을 때 파츠 평균을 계산합니다."""
    data=get_part_scores(); totals=[0]*6; count=0
    for part,choice in config.items():
        if part in data and choice in data[part]:
            totals=[a+b for a,b in zip(totals,data[part][choice])]; count+=1
    return {name:round(value/count) for name,value in zip(METRICS,totals)} if count else None


def prepare_car_data(config,performance):
    """Garage 이름을 Three.js 생성기가 사용하는 이름으로 한 번만 변환합니다."""
    return {"appearance":{
        "frontWing":config.get("front_wing","balanced"),"rearWing":config.get("rear_wing","balanced"),
        "tyres":config.get("tyres","medium"),"brakes":config.get("brakes","balanced"),
        "suspension":config.get("suspension","balanced"),"floor":config.get("floor","balanced"),
        "diffuser":config.get("diffuser","balanced"),"engine":config.get("engine","balanced"),
        "ers":config.get("ers","balanced")},
        "performance":{"downforce":performance["다운포스"],"topSpeed":performance["최고속도"],
        "cornering":performance["코너링"],"grip":performance["그립"],"braking":performance["제동"],
        "stability":performance["안정성"]},"config":config}


def get_f1_car_builder_javascript():
    """차체·윙·타이어·서스펜션·바닥 등이 모두 실제 3D Mesh인 기존 생성기를 재사용합니다."""
    return BUILDER_JS


def apply_page_style():
    """사이드바는 건드리지 않고 Racing 본문만 Garage 분위기로 꾸밉니다."""
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@500;700&family=Noto+Sans+KR:wght@400;700&display=swap');
    .stApp{background:radial-gradient(circle at 50% 12%,#202b37,#090c11 48%,#05070a);color:#eff5fa}.block-container{max-width:1450px;padding-top:1rem}
    .head{border-top:3px solid #ff3158;border-bottom:1px solid #2a3542;padding:12px 16px;background:#0c1118;display:flex;justify-content:space-between}.logo{font:700 25px Oxanium}.logo b{color:#ff3158}.step{font:11px Oxanium;color:#8492a0;letter-spacing:2px}
    .card{background:#0d131b;border:1px solid #2a3542;padding:14px}.title{font:700 12px Oxanium;letter-spacing:2px;color:#9aa8b6;border-bottom:1px solid #293542;padding-bottom:9px;margin-bottom:10px}.chips span{display:inline-block;padding:4px 7px;margin:3px;border:1px solid #354353;color:#9eacba;font-size:10px}.bar-row{margin:8px 0}.bar-top{display:flex;justify-content:space-between;font:700 11px Oxanium}.bar{height:9px;background:#232c36;margin-top:5px;transform:skewX(-12deg);overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,#27d6ff,#8065ff)}
    div[data-testid='stButton'] button{width:100%!important;min-height:58px!important;background:#e51d45!important;color:#fff!important;-webkit-text-fill-color:#fff!important;border:1px solid #ff6681!important;font:700 16px Oxanium!important}div[data-testid='stButton'] button *{color:#fff!important;-webkit-text-fill-color:#fff!important}.empty{max-width:650px;margin:90px auto;padding:30px;text-align:center;background:#0e141c;border-top:3px solid #ff3158}
    </style>""",unsafe_allow_html=True)


def build_preview_html(car_data):
    """준비 화면에서 마우스로 360도 확인하는 WebGL 차량을 만듭니다."""
    payload=json.dumps(car_data,ensure_ascii=False); builder=get_f1_car_builder_javascript()
    return f"""<!doctype html><html><head><style>*{{box-sizing:border-box}}html,body,#v{{margin:0;width:100%;height:100%;overflow:hidden;background:radial-gradient(circle,#263541,#080c11 72%)}}#tip{{position:absolute;left:12px;top:10px;color:#d5e0e9;font:11px Arial;background:#05080cb8;padding:7px;border:1px solid #354554}}canvas{{display:block}}</style><script type='importmap'>{{"imports":{{"three":"https://unpkg.com/three@0.164.1/build/three.module.js","three/addons/":"https://unpkg.com/three@0.164.1/examples/jsm/"}}}}</script></head><body><div id='v'></div><div id='tip'>DRAG 360° · WHEEL ZOOM · MY GARAGE CAR</div><script type='module'>import * as THREE from 'three';import {{OrbitControls}} from 'three/addons/controls/OrbitControls.js';const D={payload},root=document.getElementById('v'),scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,root.clientWidth/root.clientHeight,.1,100);camera.position.set(8,5.2,9);const renderer=new THREE.WebGLRenderer({{antialias:true,alpha:true}});renderer.setSize(root.clientWidth,root.clientHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;root.appendChild(renderer.domElement);scene.add(new THREE.HemisphereLight(0xc9e6ff,0x101418,2.5));const sun=new THREE.DirectionalLight(0xffffff,4);sun.position.set(6,10,4);sun.castShadow=true;scene.add(sun);{builder}const car=createF1Car(0xff1748,D.appearance);scene.add(car);const ground=new THREE.Mesh(new THREE.CylinderGeometry(6,6.3,.18,72),new THREE.MeshStandardMaterial({{color:0x111820,metalness:.55,roughness:.4}}));ground.receiveShadow=true;scene.add(ground);const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.target.set(0,.75,0);controls.minDistance=5;controls.maxDistance=18;function loop(){{requestAnimationFrame(loop);controls.update();renderer.render(scene,camera)}}loop();addEventListener('resize',()=>{{camera.aspect=root.clientWidth/root.clientHeight;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,root.clientHeight)}})</script></body></html>"""


def render_performance(performance):
    """준비 화면에는 주행에 반영되는 핵심 성능만 간단히 표시합니다."""
    for name in METRICS:
        value=int(performance[name]); st.markdown(f"<div class='bar-row'><div class='bar-top'><span>{name}</span><span>{value}</span></div><div class='bar'><i style='width:{value}%'></i></div></div>",unsafe_allow_html=True)


def render_setup(car_data,performance):
    """자동 주행을 시작하기 전 내 차량과 테스트 트랙을 확인합니다."""
    st.markdown("<div class='head'><div class='logo'>VIRTUAL <b>RACE</b></div><div class='step'>AUTOMATIC 3D TEST · 3 LAPS</div></div>",unsafe_allow_html=True)
    left,right=st.columns([1.65,.85],gap='medium')
    with left:
        st.markdown("<div class='title'>MY 3D F1 CAR · TRACK TEST CIRCUIT</div>",unsafe_allow_html=True)
        components.html(build_preview_html(car_data),height=470,scrolling=False)
        chips=''.join(f"<span>{html.escape(k.replace('_',' ').upper())} · {html.escape(str(v).upper())}</span>" for k,v in car_data['config'].items())
        st.markdown(f"<div class='chips'>{chips}</div>",unsafe_allow_html=True)
    with right:
        st.markdown("<div class='card'><div class='title'>CAR PERFORMANCE</div>",unsafe_allow_html=True);render_performance(performance);st.markdown("</div>",unsafe_allow_html=True)
    if st.button("🏁  SIMULATION START",use_container_width=True): st.session_state.auto_simulation=True;st.rerun()


def calculate_simulation_physics(performance):
    """Garage 성능을 직선 속도와 코너 통과 속도로 단순하게 연결합니다."""
    return {"straightSpeed":.075+performance["최고속도"]*.00034,
            "cornerRetention":.50+(performance["다운포스"]+performance["코너링"]+performance["그립"])/600,
            "braking":.55+performance["제동"]*.0045,"stability":.65+performance["안정성"]*.003}


def build_simulation_html(car_data):
    """웨이포인트 곡선을 따라 3랩 자동 주행하는 WebGL 시뮬레이션을 생성합니다."""
    data={"car":car_data,"physics":calculate_simulation_physics({"다운포스":car_data['performance']['downforce'],"최고속도":car_data['performance']['topSpeed'],"코너링":car_data['performance']['cornering'],"그립":car_data['performance']['grip'],"제동":car_data['performance']['braking'],"안정성":car_data['performance']['stability']}),"laps":TOTAL_LAPS}
    return SIMULATION_HTML.replace('__DATA__',json.dumps(data,ensure_ascii=False)).replace('__CAR_BUILDER__',get_f1_car_builder_javascript())


def render_simulation(car_data):
    """사용자 조작 없이 차량이 스스로 주행하는 화면을 표시합니다."""
    st.markdown("<div class='head'><div class='logo'>VIRTUAL <b>RACE</b></div><div class='step'>AUTOMATIC DRIVING SIMULATION</div></div>",unsafe_allow_html=True)
    components.html(build_simulation_html(car_data),height=820,scrolling=False)
    if st.button("← 준비 화면",use_container_width=True): st.session_state.auto_simulation=False;st.rerun()


def render_no_car():
    """Garage 차량이 없을 때 오류 대신 안내합니다."""
    st.markdown("<div class='empty'><h2>🏎 아직 Garage 차량이 없어요</h2><p>Garage에서 차량을 설계한 뒤 다시 Racing 페이지를 열어주세요.</p></div>",unsafe_allow_html=True)
    if st.button("Garage로 이동",use_container_width=True): st.switch_page('main.py')


def main():
    """준비 화면과 자동 시뮬레이션만 관리합니다."""
    # 사이드바를 숨기는 CSS는 사용하지 않으며 기본 페이지 탐색을 항상 펼쳐 둡니다.
    st.set_page_config(page_title='F1 3D Auto Simulation',page_icon='🏁',layout='wide',initial_sidebar_state='expanded')
    apply_page_style(); config,performance=load_my_car()
    if not config or not performance: render_no_car();return
    car_data=prepare_car_data(config,performance)
    if 'auto_simulation' not in st.session_state: st.session_state.auto_simulation=False
    render_simulation(car_data) if st.session_state.auto_simulation else render_setup(car_data,performance)


BUILDER_JS = '\nfunction createF1Car(color, appearance={}) {\n  const car=new THREE.Group(); car.userData.wheels=[];\n  const bodyMat=new THREE.MeshStandardMaterial({color,metalness:.72,roughness:.23});\n  const carbon=new THREE.MeshStandardMaterial({color:0x11151a,metalness:.55,roughness:.35});\n  const rubber=new THREE.MeshStandardMaterial({color:0x07080a,roughness:.82});\n  const accent=new THREE.MeshStandardMaterial({color:0x27d6ff,metalness:.65,roughness:.22});\n  function add(geometry,material,position=[0,0,0],rotation=[0,0,0],parent=car){\n    const mesh=new THREE.Mesh(geometry,material);mesh.position.set(...position);mesh.rotation.set(...rotation);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh;\n  }\n  function rod(a,b,r=.035,material=carbon){const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b),mid=A.clone().add(B).multiplyScalar(.5);const m=add(new THREE.CylinderGeometry(r,r,A.distanceTo(B),10),material,[mid.x,mid.y,mid.z]);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.clone().sub(A).normalize());return m}\n  // 유선형 모노코크, 노즈, 엔진 커버를 곡면 Geometry로 구성합니다.\n  add(new THREE.CapsuleGeometry(.55,2.75,8,24),bodyMat,[0,.62,0],[Math.PI/2,0,0]);\n  add(new THREE.ConeGeometry(.48,3.25,28),bodyMat,[0,.52,-2.65],[-Math.PI/2,0,0]);\n  add(new THREE.SphereGeometry(.82,28,16),bodyMat,[0,.64,1.05],[0,0,0]).scale.set(1.22,.64,1.6);\n  // 콕핏과 Halo\n  add(new THREE.SphereGeometry(.56,24,14),carbon,[0,1.02,-.05],[0,0,0]).scale.set(1,.58,1.25);\n  add(new THREE.TorusGeometry(.58,.055,10,32,Math.PI*1.35),carbon,[0,1.38,-.05],[Math.PI/2,0,.35]);\n  rod([0,1.35,.35],[0,.92,.42],.055,carbon);\n  // 사이드포드\n  [-1,1].forEach(side=>{const pod=add(new THREE.CapsuleGeometry(.38,1.25,8,18),bodyMat,[side*.78,.5,.55],[Math.PI/2,0,0]);pod.scale.set(1,.76,1.1)});\n  // 옵션별 플로어의 폭과 길이를 실제 Mesh 크기로 변경합니다.\n  const floorScale={venturi:1.12,balanced:1,light:.88}[appearance.floor]||1;\n  add(new THREE.BoxGeometry(2.25*floorScale,.10,4.65*floorScale),carbon,[0,.19,.25]);\n  // 타이어는 회전 가능한 원통과 컴파운드 색 띠로 구성됩니다.\n  const tyreRadius={soft:.53,medium:.50,hard:.47}[appearance.tyres]||.50;\n  const tyreColor={soft:0xed2939,medium:0xffd326,hard:0xf2f4f6}[appearance.tyres]||0xffd326;\n  [[-1.32,-1.55],[1.32,-1.55],[-1.43,1.42],[1.43,1.42]].forEach(([x,z],i)=>{\n    const wheel=new THREE.Group();wheel.position.set(x,.5,z);car.add(wheel);car.userData.wheels.push(wheel);\n    add(new THREE.CylinderGeometry(tyreRadius,tyreRadius,.40,28),rubber,[0,0,0],[0,0,Math.PI/2],wheel);\n    add(new THREE.TorusGeometry(tyreRadius*.98,.035,8,36),new THREE.MeshBasicMaterial({color:tyreColor}),[x<0?-.205:.205,0,0],[0,Math.PI/2,0],wheel);\n    const brakeSize={race:.34,balanced:.29,light:.25}[appearance.brakes]||.29;\n    add(new THREE.CylinderGeometry(brakeSize,brakeSize,.045,24),new THREE.MeshStandardMaterial({color:0xff5438,metalness:.8,roughness:.3}),[0,0,0],[0,0,Math.PI/2],wheel);\n  });\n  // 앞·뒤 바퀴와 차체를 연결하는 여러 개의 서스펜션 암입니다.\n  const arm={stiff:.052,balanced:.043,soft:.035}[appearance.suspension]||.043;\n  [[-1.55,1.32],[1.42,1.43]].forEach(([z,wx])=>[-1,1].forEach(side=>{const hub=[side*wx,.5,z];rod([side*.52,.44,z-.38],hub,arm);rod([side*.52,.44,z+.38],hub,arm);rod([side*.48,.92,z],hub,arm*.85)}));\n  // 프론트 윙은 옵션에 따라 폭과 플랩 수가 달라집니다.\n  const fw={low:[2.55,1],balanced:[3.05,2],high:[3.55,3]}[appearance.frontWing]||[3.05,2];\n  for(let i=0;i<fw[1];i++)add(new THREE.CapsuleGeometry(.09,fw[0],6,18),accent,[0,.27+i*.13,-4.05+i*.17],[0,0,Math.PI/2]);\n  [-1,1].forEach(side=>add(new THREE.BoxGeometry(.08,.58,.72),accent,[side*fw[0]*.51,.45,-3.9]));\n  // 리어 윙 역시 높이·폭·플랩 수가 설정에 따라 바뀝니다.\n  const rw={low:[1.85,1,.95],balanced:[2.25,2,1.18],high:[2.65,3,1.42]}[appearance.rearWing]||[2.25,2,1.18];\n  [-1,1].forEach(side=>rod([side*.72,.5,2.0],[side*.72,rw[2],2.2],.055,carbon));\n  for(let i=0;i<rw[1];i++)add(new THREE.CapsuleGeometry(.10,rw[0],6,18),accent,[0,rw[2]+i*.17,2.22-i*.08],[0,0,Math.PI/2]);\n  // 디퓨저 핀 수와 크기도 Garage 설정에 따라 달라집니다.\n  const df={large:[6,1.05],balanced:[4,.82],compact:[3,.58]}[appearance.diffuser]||[4,.82];\n  for(let i=0;i<df[0];i++){const x=-.85+i*(1.7/(df[0]-1));add(new THREE.BoxGeometry(.045,.52,df[1]),carbon,[x,.36,2.32],[.32,0,0])}\n  // 엔진과 ERS는 상부의 입체 커버·발광 링으로 표현합니다.\n  const engineScale={power:1.12,balanced:1,efficient:.88}[appearance.engine]||1;\n  const engine=add(new THREE.CapsuleGeometry(.31,1.0*engineScale,8,18),bodyMat,[0,1.03,1.12],[Math.PI/2,0,0]);\n  const ersColor={attack:0x32f59b,balanced:0xffb21a,recovery:0x27d6ff}[appearance.ers]||0xffb21a;\n  add(new THREE.TorusGeometry(.22,.045,10,26),new THREE.MeshStandardMaterial({color:ersColor,emissive:ersColor,emissiveIntensity:1.2}),[0,1.38,.82],[Math.PI/2,0,0]);\n  car.userData.rotateWheels=(amount)=>car.userData.wheels.forEach(w=>w.rotation.x-=amount);\n  return car;\n}\n'

SIMULATION_HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body,#game{margin:0;width:100%;height:100%;overflow:hidden;background:#071019;color:#fff;font-family:Arial}canvas{display:block}.hud{position:absolute;inset:0;pointer-events:none}.panel{position:absolute;background:#071019dc;border:1px solid #354758;border-top:2px solid #27d6ff;padding:10px 14px}.pos{left:18px;top:18px}.lap{right:18px;top:18px;text-align:right}.speed{left:50%;bottom:24px;transform:translateX(-50%);text-align:center;background:none}.speed b{font-size:56px}.speed span{display:block;font-size:11px;letter-spacing:3px}.count{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:bold 105px Arial;text-shadow:0 0 32px #ff3158}.result{display:none;position:absolute;inset:0;background:#05080de8;align-items:center;justify-content:center}.result-card{width:510px;padding:28px;text-align:center;background:#0d141c;border:1px solid #3a4857;border-top:4px solid #ff3158}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:20px 0}.stat{padding:12px;background:#151d26}.lesson{padding:13px;text-align:left;background:#101c1a;border-left:3px solid #35e69a;color:#cce6dc}.result button{pointer-events:auto;margin-top:15px;padding:12px 18px;background:#ff3158;color:white;border:0;font-weight:bold;cursor:pointer}
</style><script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.164.1/build/three.module.js"}}</script></head><body><div id="game"></div><div class="hud"><div class="panel pos">POSITION<br><b>1 / 1</b></div><div class="panel lap">LAP<br><b id="lap">1 / 3</b></div><div class="speed"><b id="speed">0</b><span>KM / H</span></div></div><div class="count" id="count">3</div><div class="result" id="result"><div class="result-card"><h1>🏁 SIMULATION COMPLETE</h1><div class="stats"><div class="stat">LAPS<br><b>3</b></div><div class="stat">TOP SPEED<br><b id="top">0 km/h</b></div><div class="stat">BEST LAP<br><b id="best">--:--.---</b></div></div><div class="lesson" id="lesson"></div><button onclick="location.reload()">다시 시뮬레이션</button></div></div>
<script type="module">import * as THREE from 'three';const DATA=__DATA__,root=document.getElementById('game'),scene=new THREE.Scene();scene.background=new THREE.Color(0x08121a);scene.fog=new THREE.Fog(0x08121a,55,165);const camera=new THREE.PerspectiveCamera(58,root.clientWidth/root.clientHeight,.1,400),renderer=new THREE.WebGLRenderer({antialias:true});renderer.setSize(root.clientWidth,root.clientHeight);renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;root.appendChild(renderer.domElement);scene.add(new THREE.HemisphereLight(0xc9e6ff,0x182316,2.2));const sun=new THREE.DirectionalLight(0xffffff,3.4);sun.position.set(25,40,15);sun.castShadow=true;scene.add(sun);
__CAR_BUILDER__
// 직선, 좌·우 코너가 이어지는 폐쇄형 3D 테스트 트랙 중심선입니다.
const points=[[-42,0,28],[-48,0,-5],[-32,0,-38],[8,0,-45],[45,0,-28],[48,0,10],[27,0,38],[-8,0,43],[-42,0,28]].map(v=>new THREE.Vector3(...v));const curve=new THREE.CatmullRomCurve3(points,true,'catmullrom',.25),samples=420,roadHalf=7,vertices=[],indices=[];for(let i=0;i<=samples;i++){const t=i/samples,p=curve.getPointAt(t),tan=curve.getTangentAt(t),side=new THREE.Vector3(-tan.z,0,tan.x);vertices.push(p.x+side.x*roadHalf,.12,p.z+side.z*roadHalf,p.x-side.x*roadHalf,.12,p.z-side.z*roadHalf);if(i<samples){const a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2)}}const roadGeo=new THREE.BufferGeometry();roadGeo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));roadGeo.setIndex(indices);roadGeo.computeVertexNormals();const road=new THREE.Mesh(roadGeo,new THREE.MeshStandardMaterial({color:0x272d32,roughness:.9});road.receiveShadow=true;scene.add(road);const grass=new THREE.Mesh(new THREE.PlaneGeometry(240,240),new THREE.MeshStandardMaterial({color:0x17341f,roughness:1}));grass.rotation.x=-Math.PI/2;scene.add(grass);
// 트랙 경계와 커브를 실제 3D 박스로 배치합니다.
for(let i=0;i<samples;i+=5){const t=i/samples,p=curve.getPointAt(t),tan=curve.getTangentAt(t),side=new THREE.Vector3(-tan.z,0,tan.x),angle=Math.atan2(tan.x,tan.z);[-1,1].forEach(sign=>{const curb=new THREE.Mesh(new THREE.BoxGeometry(1.9,.18,.65),new THREE.MeshStandardMaterial({color:(i/5)%2?0xffffff:0xff3158}));curb.position.copy(p).addScaledVector(side,sign*(roadHalf-.2));curb.position.y=.18;curb.rotation.y=angle;scene.add(curb)})}const start=curve.getPointAt(0),startLine=new THREE.Mesh(new THREE.BoxGeometry(roadHalf*2,.025,.8),new THREE.MeshStandardMaterial({color:0xffffff}));startLine.position.set(start.x,.16,start.z);startLine.rotation.y=Math.atan2(curve.getTangentAt(0).x,curve.getTangentAt(0).z);scene.add(startLine);
const car=createF1Car(0xff1748,DATA.car.appearance);scene.add(car);let progress=0,lap=0,started=false,finished=false,topSpeed=0,best=Infinity,lapStart=0,last=performance.now();function curvature(t){const a=curve.getTangentAt(t),b=curve.getTangentAt((t+.016)%1);return a.angleTo(b)}function fmt(ms){const m=Math.floor(ms/60000),s=Math.floor(ms%60000/1000),x=Math.floor(ms%1000);return `${m}:${String(s).padStart(2,'0')}.${String(x).padStart(3,'0')}`}
function update(dt,now){const turn=curvature(progress),corner=Math.max(.38,1-turn*5.2),p=DATA.physics,target=p.straightSpeed*(corner+(1-corner)*p.cornerRetention);progress+=target*dt;if(progress>=1){progress-=1;lap++;const lapTime=now-lapStart;best=Math.min(best,lapTime);lapStart=now;if(lap>=DATA.laps){finish();return}}const point=curve.getPointAt(progress),tan=curve.getTangentAt(progress);car.position.copy(point);car.position.y=.14;car.rotation.y=Math.atan2(tan.x,tan.z);car.userData.rotateWheels(target*dt*170);const kmh=(245+DATA.car.performance.topSpeed*.9)*(target/p.straightSpeed);topSpeed=Math.max(topSpeed,kmh);document.getElementById('speed').textContent=Math.round(kmh);document.getElementById('lap').textContent=Math.min(lap+1,DATA.laps)+' / '+DATA.laps;const behind=point.clone().addScaledVector(tan,-10).add(new THREE.Vector3(0,5.1,0)),look=point.clone().addScaledVector(tan,5).add(new THREE.Vector3(0,1,0));camera.position.lerp(behind,1-Math.pow(.002,dt));camera.lookAt(look)}function finish(){finished=true;document.getElementById('top').textContent=Math.round(topSpeed)+' km/h';document.getElementById('best').textContent=fmt(best);const p=DATA.car.performance;document.getElementById('lesson').textContent=p.downforce+p.cornering>p.topSpeed*2?'다운포스와 코너링 성능이 높아 코너에서 속도 손실이 비교적 적었어요.':'최고속도가 높아 직선에서 빠르지만 코너에서는 속도를 더 많이 줄였어요.';document.getElementById('result').style.display='flex'}let n=3;const count=document.getElementById('count'),timer=setInterval(()=>{n--;if(n>0)count.textContent=n;else if(n===0)count.textContent='GO!';else{count.style.display='none';started=true;lapStart=performance.now();clearInterval(timer)}},900);function loop(now){requestAnimationFrame(loop);const dt=Math.min(.033,(now-last)/1000);last=now;if(started&&!finished)update(dt,now);renderer.render(scene,camera)}const p0=curve.getPointAt(0),t0=curve.getTangentAt(0);car.position.copy(p0);car.rotation.y=Math.atan2(t0.x,t0.z);camera.position.copy(p0).addScaledVector(t0,-10).add(new THREE.Vector3(0,5,0));loop(last);addEventListener('resize',()=>{camera.aspect=root.clientWidth/root.clientHeight;camera.updateProjectionMatrix();renderer.setSize(root.clientWidth,root.clientHeight)})</script></body></html>"""

if __name__=='__main__': main()
