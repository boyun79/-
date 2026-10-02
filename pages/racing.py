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


BUILDER_JS = '\nfunction createF1Car(color, appearance={}) {\n  const car=new THREE.Group(); car.userData.wheels=[];\n  const bodyMat=new THREE.MeshStandardMaterial({color,metalness:.72,roughness:.23});\n  const carbon=new THREE.MeshStandardMaterial({color:0x11151a,metalness:.55,roughness:.35});\n  const rubber=new THREE.MeshStandardMaterial({color:0x07080a,roughness:.82});\n  const accent=new THREE.MeshStandardMaterial({color:0x27d6ff,metalness:.65,roughness:.22});\n  function add(geometry,material,position=[0,0,0],rotation=[0,0,0],parent=car){\n    const mesh=new THREE.Mesh(geometry,material);mesh.position.set(...position);mesh.rotation.set(...rotation);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh;\n  }\n  function rod(a,b,r=.035,material=carbon){const A=new THREE.Vector3(...a),B=new THREE.Vector3(...b),mid=A.clone().add(B).multiplyScalar(.5);const m=add(new THREE.CylinderGeometry(r,r,A.distanceTo(B),10),material,[mid.x,mid.y,mid.z]);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),B.clone().sub(A).normalize());return m}\n  // 유선형 모노코크, 노즈, 엔진 커버를 곡면 Geometry로 구성합니다.\n  add(new THREE.CapsuleGeometry(.55,2.75,8,24),bodyMat,[0,.62,0],[Math.PI/2,0,0]);\n  add(new THREE.ConeGeometry(.48,3.25,28),bodyMat,[0,.52,-2.65],[-Math.PI/2,0,0]);\n  add(new THREE.SphereGeometry(.82,28,16),bodyMat,[0,.64,1.05],[0,0,0]).scale.set(1.22,.64,1.6);\n  // 콕핏과 Halo\n  add(new THREE.SphereGeometry(.56,24,14),carbon,[0,1.02,-.05],[0,0,0]).scale.set(1,.58,1.25);\n  add(new THREE.TorusGeometry(.58,.055,10,32,Math.PI*1.35),carbon,[0,1.38,-.05],[Math.PI/2,0,.35]);\n  rod([0,1.35,.35],[0,.92,.42],.055,carbon);\n  // 사이드포드\n  [-1,1].forEach(side=>{const pod=add(new THREE.CapsuleGeometry(.38,1.25,8,18),bodyMat,[side*.78,.5,.55],[Math.PI/2,0,0]);pod.scale.set(1,.76,1.1)});\n  // 옵션별 플로어의 폭과 길이를 실제 Mesh 크기로 변경합니다.\n  const floorScale={venturi:1.12,balanced:1,light:.88}[appearance.floor]||1;\n  add(new THREE.BoxGeometry(2.25*floorScale,.10,4.65*floorScale),carbon,[0,.19,.25]);\n  // 타이어는 회전 가능한 원통과 컴파운드 색 띠로 구성됩니다.\n  const tyreRadius={soft:.53,medium:.50,hard:.47}[appearance.tyres]||.50;\n  const tyreColor={soft:0xed2939,medium:0xffd326,hard:0xf2f4f6}[appearance.tyres]||0xffd326;\n  [[-1.32,-1.55],[1.32,-1.55],[-1.43,1.42],[1.43,1.42]].forEach(([x,z],i)=>{\n    const wheel=new THREE.Group();wheel.position.set(x,.5,z);car.add(wheel);car.userData.wheels.push(wheel);\n    add(new THREE.CylinderGeometry(tyreRadius,tyreRadius,.40,28),rubber,[0,0,0],[0,0,Math.PI/2],wheel);\n    add(new THREE.TorusGeometry(tyreRadius*.98,.035,8,36),new THREE.MeshBasicMaterial({color:tyreColor}),[x<0?-.205:.205,0,0],[0,Math.PI/2,0],wheel);\n    const brakeSize={race:.34,balanced:.29,light:.25}[appearance.brakes]||.29;\n    add(new THREE.CylinderGeometry(brakeSize,brakeSize,.045,24),new THREE.MeshStandardMaterial({color:0xff5438,metalness:.8,roughness:.3}),[0,0,0],[0,0,Math.PI/2],wheel);\n  });\n  // 앞·뒤 바퀴와 차체를 연결하는 여러 개의 서스펜션 암입니다.\n  const arm={stiff:.052,balanced:.043,soft:.035}[appearance.suspension]||.043;\n  [[-1.55,1.32],[1.42,1.43]].forEach(([z,wx])=>[-1,1].forEach(side=>{const hub=[side*wx,.5,z];rod([side*.52,.44,z-.38],hub,arm);rod([side*.52,.44,z+.38],hub,arm);rod([side*.48,.92,z],hub,arm*.85)}));\n  // 프론트 윙은 옵션에 따라 폭과 플랩 수가 달라집니다.\n  const fw={low:[2.55,1],balanced:[3.05,2],high:[3.55,3]}[appearance.frontWing]||[3.05,2];\n  for(let i=0;i<fw[1];i++)add(new THREE.CapsuleGeometry(.09,fw[0],6,18),accent,[0,.27+i*.13,-4.05+i*.17],[0,0,Math.PI/2]);\n  [-1,1].forEach(side=>add(new THREE.BoxGeometry(.08,.58,.72),accent,[side*fw[0]*.51,.45,-3.9]));\n  // 리어 윙 역시 높이·폭·플랩 수가 설정에 따라 바뀝니다.\n  const rw={low:[1.85,1,.95],balanced:[2.25,2,1.18],high:[2.65,3,1.42]}[appearance.rearWing]||[2.25,2,1.18];\n  [-1,1].forEach(side=>rod([side*.72,.5,2.0],[side*.72,rw[2],2.2],.055,carbon));\n  for(let i=0;i<rw[1];i++)add(new THREE.CapsuleGeometry(.10,rw[0],6,18),accent,[0,rw[2]+i*.17,2.22-i*.08],[0,0,Math.PI/2]);\n  // 디퓨저 핀 수와 크기도 Garage 설정에 따라 달라집니다.\n  const df={large:[6,1.05],balanced:[4,.82],compact:[3,.58]}[appearance.diffuser]||[4,.82];\n  for(let i=0;i<df[0];i++){const x=-.85+i*(1.7/(df[0]-1));add(new THREE.BoxGeometry(.045,.52,df[1]),carbon,[x,.36,2.32],[.32,0,0])}\n  // 엔진과 ERS는 상부의 입체 커버·발광 링으로 표현합니다.\n  const engineScale={power:1.12,balanced:1,efficient:.88}[appearance.engine]||1;\n  const engine=add(new THREE.CapsuleGeometry(.31,1.0*engineScale,8,18),bodyMat,[0,1.03,1.12],[Math.PI/2,0,0]);\n  const ersColor={attack:0x32f59b,balanced:0xffb21a,recovery:0x27d6ff}[appearance.ers]||0xffb21a;\n  add(new THREE.TorusGeometry(.22,.045,10,26),new THREE.MeshStandardMaterial({color:ersColor,emissive:ersColor,emissiveIntensity:1.2}),[0,1.38,.82],[Math.PI/2,0,0]);\n  car.userData.rotateWheels=(amount)=>car.userData.wheels.forEach(w=>w.rotation.x-=amount);\n  return car;\n}\n'


def build_simulation_html(car_data):
    """준비 화면부터 결과까지 하나의 iframe에서 실행하여 rerun에 따른 중단을 방지합니다."""
    data = {"car": car_data, "laps": TOTAL_LAPS}
    # </script> 삽입을 막고 기존 Garage 값의 JSON 구조는 그대로 유지합니다.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return SIMULATION_HTML.replace("__DATA__", payload).replace("__CAR_BUILDER__", BUILDER_JS)


def main():
    st.set_page_config(page_title="F1 3D Auto Simulation", page_icon="🏁",
                       layout="wide", initial_sidebar_state="expanded")
    apply_page_style()
    config, performance = load_my_car()
    if not config or not performance:
        st.warning("Garage에서 차량을 먼저 설계해 주세요.")
        return
    car_data = prepare_car_data(config, performance)
    st.markdown("<div class='head'><div class='logo'>VIRTUAL <b>RACE</b></div>"
                "<div class='step'>MY 3D F1 CAR · TRACK TEST CIRCUIT</div></div>",
                unsafe_allow_html=True)
    # Streamlit 버튼으로 iframe을 교체하지 않습니다. JS 내부 버튼이 곧바로 카운트다운을 시작합니다.
    components.html(build_simulation_html(car_data), height=650, scrolling=False)
    left, right = st.columns([1.6, 1])
    with left:
        chips = "".join(
            f"<span>{html.escape(str(k).replace('_', ' ').upper())} · {html.escape(str(v).upper())}</span>"
            for k, v in config.items()
        )
        st.markdown(f"<div class='title'>GARAGE SETUP</div><div class='chips'>{chips}</div>",
                    unsafe_allow_html=True)
    with right:
        st.markdown("<div class='title'>CAR PERFORMANCE</div>", unsafe_allow_html=True)
        for name in METRICS:
            try:
                value = max(0, min(100, float(performance[name])))
            except (TypeError, ValueError):
                value = 50
            st.markdown(
                f"<div class='bar-row'><div class='bar-top'><span>{name}</span><span>{value:.0f}</span></div>"
                f"<div class='bar'><i style='width:{value:.0f}%'></i></div></div>",
                unsafe_allow_html=True,
            )


SIMULATION_HTML = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#071019;color:#fff;font-family:Arial,sans-serif}
#game{position:relative;width:100%;height:100%;overflow:hidden;background:#071019}
canvas{display:block;width:100%;height:100%}.hud{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.panel{position:absolute;top:12px;max-width:42%;padding:8px 12px;background:#071019dc;border:1px solid #354758;border-top:2px solid #27d6ff;font-size:11px;letter-spacing:1px}
.panel b{font-size:clamp(16px,2.8vw,26px);white-space:nowrap}.pos{left:12px}.lap{right:12px;text-align:right}
.speed{position:absolute;bottom:15px;left:50%;transform:translateX(-50%);white-space:nowrap;background:#071019df;border:1px solid #354758;padding:8px 18px;font-size:clamp(14px,2.5vw,24px)}
#overlay{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none;text-align:center;text-shadow:0 3px 10px #000}
#overlay h1{margin:0;font-size:clamp(35px,8vw,88px);color:#ff3158}#overlay p{margin:6px;font-size:clamp(14px,2vw,22px)}
#start{pointer-events:auto;cursor:pointer;margin-top:24px;padding:14px 27px;border:1px solid #ff6681;background:#e51d45;color:white;font-weight:900;font-size:17px}
#result{display:none;background:#08111eea;border:1px solid #ff3158;padding:20px;line-height:1.8;min-width:min(340px,85vw)}
#result strong{color:#ff3158;font-size:23px}#error{position:absolute;left:12px;bottom:10px;color:#ff7186;background:#08111e}
</style><script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.164.1/build/three.module.js"}}</script>
</head><body><div id="game"><div class="hud" id="hud" hidden><div class="panel pos">POSITION<br><b id="position">1 / 5</b></div><div class="panel lap">LAP<br><b id="lap">1 / 3</b></div><div class="speed">SPEED <b id="speed">0</b> km/h</div></div>
<div id="overlay"><p id="message">MY 3D F1 CAR · TRACK TEST CIRCUIT</p><h1 id="count"></h1><button id="start">SIMULATION START</button><div id="result"></div></div><div id="error"></div></div>
<script type="module">
import * as THREE from 'three';
const DATA=__DATA__,root=document.getElementById('game');
const scene=new THREE.Scene();scene.background=new THREE.Color(0x08121a);
const camera=new THREE.PerspectiveCamera(52,1,.1,500);
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.shadowMap.enabled=true;root.insertBefore(renderer.domElement,root.firstChild);
scene.add(new THREE.HemisphereLight(0xd2e8ff,0x13231b,2.1));
const sun=new THREE.DirectionalLight(0xffffff,2.9);sun.position.set(-25,65,20);sun.castShadow=true;scene.add(sun);
const ground=new THREE.Mesh(new THREE.PlaneGeometry(260,260),new THREE.MeshStandardMaterial({color:0x10201e,roughness:1}));
ground.rotation.x=-Math.PI/2;ground.position.y=-.08;ground.receiveShadow=true;scene.add(ground);
__CAR_BUILDER__
// 하나의 폐쇄형 중심선이 미리보기·노면·주행 모두에 사용됩니다.
function createWaypoints(){return [[-48,0,25],[-42,0,-23],[-30,0,-39],[12,0,-42],[42,0,-29],[50,0,-8],[42,0,15],[20,0,26],[37,0,37],[11,0,43],[-12,0,27],[-34,0,35]].map(p=>new THREE.Vector3(...p))}
const trackWaypoints=createWaypoints();
const curve=new THREE.CatmullRomCurve3(trackWaypoints,true,'catmullrom',.35);
const roadWidth=12, length=curve.getLength();
function frameAt(t){const p=curve.getPointAt((t+1)%1),v=curve.getTangentAt((t+1)%1).normalize();return {p,v,side:new THREE.Vector3(v.z,0,-v.x)}}
function createTrack(){
  const N=500,vertices=[],indices=[],roadMat=new THREE.MeshStandardMaterial({color:0x282e34,roughness:.94,side:THREE.DoubleSide});
  for(let i=0;i<=N;i++){let {p,side}=frameAt(i/N);for(let s of [-1,1]){let q=p.clone().addScaledVector(side,s*roadWidth/2);vertices.push(q.x,.012,q.z)}}
  for(let i=0;i<N;i++){let a=i*2;indices.push(a,a+1,a+2,a+1,a+3,a+2)}
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(vertices,3));geo.setIndex(indices);geo.computeVertexNormals();
  const road=new THREE.Mesh(geo,roadMat);road.receiveShadow=true;scene.add(road);
  // 커브·중앙선·스타트 라인은 노면과 같은 곡선에서 생성합니다.
  for(let i=0;i<N;i+=7){let t=i/N,{p,v,side}=frameAt(t),angle=Math.atan2(-v.x,-v.z);
    for(let sign of [-1,1]){let curb=new THREE.Mesh(new THREE.BoxGeometry(.85,.09,2.0),new THREE.MeshStandardMaterial({color:(i/7)%2?0xffffff:0xe7274e}));
      curb.position.copy(p).addScaledVector(side,sign*roadWidth/2);curb.position.y=.065;curb.rotation.y=angle;scene.add(curb)}
    if(i%21===0){let mark=new THREE.Mesh(new THREE.BoxGeometry(.15,.025,2.3),new THREE.MeshBasicMaterial({color:0xb7c1c4}));mark.position.copy(p);mark.position.y=.035;mark.rotation.y=angle;scene.add(mark)}
  }
  const start=frameAt(0),line=new THREE.Group();
  for(let j=0;j<12;j++){let box=new THREE.Mesh(new THREE.BoxGeometry(roadWidth/12,.018,1.4),new THREE.MeshBasicMaterial({color:j%2?0xffffff:0x16191d,side:THREE.DoubleSide}));box.position.copy(start.p).addScaledVector(start.side,(j-5.5)*roadWidth/12);box.position.y=.05;box.rotation.y=Math.atan2(-start.v.x,-start.v.z);line.add(box)}
  scene.add(line);
}
createTrack();
function score(name){let n=Number(DATA.car.performance[name]);return Number.isFinite(n)?Math.max(0,Math.min(1,n/100)):.5}
function createPlayerCar(){let mesh=createF1Car(0xff1748,DATA.car.appearance);scene.add(mesh);return {mesh,progress:0,laps:0,speed:0,finished:false,base:1,top:0,lapStart:0,lastLap:0,best:Infinity,finishTime:Infinity}}
function createAICars(){return [0.91,0.96,0.88,1.00].map((base,i)=>{let mesh=createF1Car([0x24bbfa,0xfcc935,0x8de76b,0xb277fa][i],DATA.car.appearance);scene.add(mesh);return {mesh,progress:0,laps:0,speed:0,finished:false,base,top:0,lapStart:0,lastLap:0,best:Infinity,finishTime:Infinity}})}
const player=createPlayerCar(),ais=createAICars(),cars=[player,...ais];
// 차량은 출발선 근처 5열 그리드에 놓되, 선수차는 정확히 출발선 위에 둡니다.
function placeCar(car,index){const f=frameAt(car.progress),offset=index===0?0:(index%2? -2.2:2.2);car.mesh.position.copy(f.p).addScaledVector(f.side,offset);car.mesh.position.y=.10;car.mesh.rotation.y=Math.atan2(-f.v.x,-f.v.z)}
cars.forEach((car,i)=>{car.progress=i===0?0:1-i*.009;placeCar(car,i)});
// 랩 완주 전 코너 반경을 미리 읽어 자연스럽게 감속하고 탈출할 때 가속합니다.
function cornerSeverity(t){let a=curve.getTangentAt((t+.012)%1),b=curve.getTangentAt((t+.035)%1);return Math.min(1,a.angleTo(b)*5.0)}
function updateCar(car,dt,elapsed,index){if(car.finished)return;
  const isPlayer=index===0,turn=cornerSeverity(car.progress),top=isPlayer?235+score('topSpeed')*95:270*car.base;
  const corner=isPlayer?.48+.22*score('cornering')+.13*score('downforce')+.10*score('grip'):.73;
  const target=top*(1-turn*(1-corner));
  const brake=isPlayer?2.1+score('braking')*5:4.4,accel=isPlayer?1.1+score('grip')*1.4:1.8;
  const stability=isPlayer?.5+score('stability')*.5:.8;
  car.speed+= (target-car.speed)*(1-Math.exp(-(target<car.speed?brake:accel)*stability*dt));
  car.top=Math.max(car.top,car.speed);
  // 시간·거리 일관성: km/h → m/s → 정규화된 트랙 거리.
  const old=car.progress;car.progress+=(car.speed/3.6)*dt/length;
  if(car.progress>=1){car.progress-=1;car.laps++;car.lastLap=elapsed-car.lapStart;car.best=Math.min(car.best,car.lastLap);car.lapStart=elapsed;
    if(car.laps>=DATA.laps){car.finished=true;car.finishTime=elapsed;car.progress=0;car.speed=0}}
  placeCar(car,index);if(!car.finished&&car.mesh.userData.rotateWheels)car.mesh.userData.rotateWheels(car.speed*dt*.06);
}
function updatePlayerCar(dt,elapsed){updateCar(player,dt,elapsed,0)}
function updateAICars(dt,elapsed){ais.forEach((car,i)=>updateCar(car,dt,elapsed,i+1))}
function rank(){let distance=c=>c.finished?DATA.laps+1+(100000-c.finishTime)*.00000001:c.laps+c.progress;return 1+ais.filter(c=>distance(c)>distance(player)).length}
const targetCamera=new THREE.Vector3();
function updateCamera(dt){let f=frameAt(player.progress);targetCamera.copy(player.mesh.position).addScaledVector(f.v,-16).add(new THREE.Vector3(0,8,0));camera.position.lerp(targetCamera,1-Math.exp(-4*dt));camera.lookAt(player.mesh.position.x,1,player.mesh.position.z)}
function updateHUD(){document.getElementById('position').textContent=rank()+' / 5';document.getElementById('lap').textContent=Math.min(3,player.laps+1)+' / 3';document.getElementById('speed').textContent=Math.round(player.speed)}
let phase='preview',countEnd=0,startTime=0,lastFrame=performance.now(),elapsed=0;
function startCountdown(){if(phase!=='preview')return;phase='countdown';document.getElementById('start').hidden=true;document.getElementById('message').textContent='RACE STARTING';document.getElementById('hud').hidden=false;countEnd=performance.now()+4000}
function startSimulation(now){phase='running';startTime=now;lastFrame=now;document.getElementById('count').textContent='';document.getElementById('message').textContent='';document.getElementById('overlay').style.display='none'}
function finishSimulation(){phase='complete';document.getElementById('overlay').style.display='flex';document.getElementById('result').style.display='block';document.getElementById('result').innerHTML='<strong>SIMULATION COMPLETE</strong><br>POSITION '+rank()+' / 5<br>LAPS 3<br>TOP SPEED '+Math.round(player.top)+' km/h<br>LAP TIME '+player.lastLap.toFixed(2)+' sec<br>BEST LAP '+player.best.toFixed(2)+' sec';document.getElementById('hud').hidden=true}
function handleResize(){let w=Math.max(root.clientWidth,1),h=Math.max(root.clientHeight,1);renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();if(phase==='preview'){const distance=Math.max(125,125/camera.aspect);camera.position.set(0,distance,2);camera.lookAt(0,0,0)}}
window.addEventListener('resize',handleResize);new ResizeObserver(handleResize).observe(root);handleResize();document.getElementById('start').addEventListener('click',startCountdown);
// requestAnimationFrame은 모든 상태에서 유지되므로 카운트다운 뒤에도 캔버스가 사라지지 않습니다.
function animate(now){requestAnimationFrame(animate);const dt=Math.min((now-lastFrame)/1000,.05);lastFrame=now;
  if(phase==='countdown'){let remaining=countEnd-now;document.getElementById('count').textContent=remaining>1000?String(Math.ceil((remaining-1000)/1000)):'GO';updateCamera(dt);if(remaining<=0)startSimulation(now)}
  else if(phase==='running'){elapsed=(now-startTime)/1000;updatePlayerCar(dt,elapsed);updateAICars(dt,elapsed);updateCamera(dt);updateHUD();if(player.finished)finishSimulation()}
  renderer.render(scene,camera)}requestAnimationFrame(animate);
</script></body></html>'''


if __name__ == "__main__":
    main()
