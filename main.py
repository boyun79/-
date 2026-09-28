import html
from copy import deepcopy

import streamlit as st


# ============================================================
# 1. 파츠 데이터와 물리 개념 설명
# ============================================================
def get_physics_explanations():
    """성능 이름에 마우스를 올렸을 때 보여 줄 쉬운 물리 설명을 반환합니다."""
    return {
        "다운포스": "차가 달릴 때 공기의 힘으로 차를 트랙 쪽으로 눌러 주는 힘이에요. 커지면 코너에서 안정적이지만 공기저항도 함께 커질 수 있어요.",
        "공기저항": "차가 앞으로 움직일 때 공기가 진행을 방해하는 힘이에요. 공기저항이 크면 높은 직선 속도를 내기 어려워져요.",
        "직선 속도": "긴 직선 구간에서 얼마나 빠르게 달릴 수 있는지를 나타내는 게임용 지표예요. 엔진 출력과 공기저항의 영향을 크게 받아요.",
        "코너링": "차가 코너를 얼마나 빠르고 안정적으로 돌 수 있는지를 나타내는 지표예요. 다운포스, 그립, 서스펜션이 중요해요.",
        "그립": "타이어와 트랙 사이에서 차가 미끄러지지 않도록 잡아 주는 힘이에요. 코너링과 제동에 모두 영향을 줘요.",
        "제동 성능": "브레이크를 사용했을 때 속도를 얼마나 효과적으로 줄일 수 있는지를 나타내는 지표예요.",
        "안정성": "가속·제동·코너링 중 차량의 움직임이 얼마나 예측 가능하고 흔들림이 적은지를 나타내요.",
        "무게": "차량 전체의 질량이에요. 무거워지면 관성(현재 움직임을 유지하려는 성질)이 커져 가속·제동·코너링에 불리할 수 있어요.",
    }


def option(name, downforce, drag, straight, cornering, grip, braking, stability, weight, color, lesson):
    """파츠 옵션을 같은 형식으로 만들기 위한 작은 도우미 함수입니다."""
    return {
        "name": name,
        "metrics": {
            "다운포스": downforce, "공기저항": drag, "직선 속도": straight,
            "코너링": cornering, "그립": grip, "제동 성능": braking,
            "안정성": stability,
        },
        "weight": weight,
        "color": color,
        "lesson": lesson,
    }


def get_part_data():
    """게임의 모든 파츠 데이터를 반환합니다.

    새 파츠를 추가할 때 이 딕셔너리에 같은 구조로 항목만 추가하면
    선택 화면과 성능 계산에 자동으로 반영되도록 구성했습니다.
    """
    return {
        "프론트 윙": {
            "icon": "FW", "visual": "front_wing",
            "options": {
                "다운포스형": option("다운포스형", 92, 78, 52, 90, 74, 60, 78, 11, "#ff304f", "윙 각도가 커져 앞쪽 다운포스가 증가합니다. 코너 진입은 좋아지지만 직선에서는 저항이 커집니다."),
                "균형형": option("균형형", 72, 56, 72, 74, 68, 60, 75, 9, "#ffb000", "다운포스와 공기저항을 절충한 설정입니다. 다양한 코너와 직선에 고르게 대응합니다."),
                "저저항형": option("저저항형", 48, 30, 91, 56, 58, 58, 62, 7, "#00d4ff", "윙 각도를 줄여 공기저항을 낮췄습니다. 직선은 빨라지지만 앞바퀴가 코너에서 덜 눌립니다."),
            },
        },
        "리어 윙": {
            "icon": "RW", "visual": "rear_wing",
            "options": {
                "고다운포스": option("고다운포스", 94, 82, 48, 91, 72, 58, 91, 15, "#ff304f", "큰 리어 윙은 뒤쪽을 강하게 눌러 코너 안정성을 높이지만 공기저항이 증가합니다."),
                "중간 다운포스": option("중간 다운포스", 73, 58, 70, 75, 67, 58, 78, 12, "#ffb000", "코너 안정성과 직선 속도 사이의 균형을 맞춘 설정입니다."),
                "저저항": option("저저항", 45, 27, 94, 53, 56, 55, 59, 9, "#00d4ff", "작은 리어 윙은 직선 속도를 높이지만 빠른 코너에서 뒤가 불안정할 수 있습니다."),
            },
        },
        "타이어": {
            "icon": "TY", "visual": "tires",
            "options": {
                "소프트": option("소프트", 61, 51, 75, 88, 96, 88, 69, 46, "#e92535", "부드러운 고무가 트랙에 잘 달라붙어 그립이 높지만 실제 경기에서는 빨리 닳습니다."),
                "미디엄": option("미디엄", 60, 49, 77, 77, 80, 79, 79, 48, "#ffd52a", "그립과 내구성의 균형을 잡은 타이어입니다."),
                "하드": option("하드", 58, 47, 78, 65, 68, 69, 86, 50, "#eef3f8", "단단한 고무는 안정적으로 오래 쓰기 좋지만 즉각적인 그립은 낮습니다."),
            },
        },
        "브레이크": {
            "icon": "BR", "visual": "brakes",
            "options": {
                "카본 고성능": option("카본 고성능", 58, 51, 74, 74, 73, 97, 79, 27, "#ff4d35", "높은 온도에서도 큰 마찰력을 내어 짧은 거리에서 감속하지만 무게와 냉각 부담이 있습니다."),
                "균형형": option("균형형", 58, 49, 76, 72, 72, 82, 84, 24, "#ffb000", "제동력과 제어하기 쉬운 반응을 함께 고려한 설정입니다."),
                "경량형": option("경량형", 57, 46, 81, 70, 70, 73, 70, 20, "#00d4ff", "가벼워 가속 반응은 좋아지지만 강한 반복 제동에는 불리할 수 있습니다."),
            },
        },
        "서스펜션": {
            "icon": "SU", "visual": "suspension",
            "options": {
                "단단한 세팅": option("단단한 세팅", 70, 50, 76, 88, 79, 76, 66, 34, "#ff304f", "차체 움직임을 줄여 빠른 코너 반응이 좋아지지만 울퉁불퉁한 노면에서는 그립을 잃기 쉽습니다."),
                "균형 세팅": option("균형 세팅", 66, 49, 76, 79, 80, 78, 86, 36, "#ffb000", "차체 반응과 노면 추종성의 균형을 맞춘 설정입니다."),
                "부드러운 세팅": option("부드러운 세팅", 61, 50, 73, 70, 86, 80, 89, 38, "#00d4ff", "바퀴가 노면 굴곡을 잘 따라가 그립이 안정적이지만 방향 전환 반응은 느려질 수 있습니다."),
            },
        },
        "플로어": {
            "icon": "FL", "visual": "floor",
            "options": {
                "벤투리 고성능": option("벤투리 고성능", 96, 55, 72, 93, 76, 62, 82, 48, "#9b5cff", "차 밑 공기 통로를 좁혀 유속을 높이고 압력을 낮추는 벤투리 효과로 큰 다운포스를 만듭니다."),
                "균형형": option("균형형", 78, 48, 78, 80, 72, 61, 84, 43, "#ffb000", "지상고 변화에도 성능이 급격히 변하지 않도록 균형을 잡았습니다."),
                "경량 저항형": option("경량 저항형", 59, 37, 87, 66, 65, 58, 68, 36, "#00d4ff", "다운포스를 일부 포기해 무게와 저항을 줄인 설정입니다."),
            },
        },
        "디퓨저": {
            "icon": "DF", "visual": "diffuser",
            "options": {
                "대형 확산형": option("대형 확산형", 91, 62, 65, 88, 73, 60, 86, 18, "#9b5cff", "차 밑의 빠른 공기를 뒤에서 부드럽게 확산시켜 압력을 회복하고 바닥 다운포스를 강화합니다."),
                "균형형": option("균형형", 75, 49, 77, 78, 70, 60, 82, 15, "#ffb000", "다운포스 증가와 공기 흐름 안정성을 절충했습니다."),
                "소형 저저항": option("소형 저저항", 53, 34, 88, 61, 62, 57, 67, 12, "#00d4ff", "확산 효과는 작지만 저항과 무게를 줄여 직선에 유리합니다."),
            },
        },
        "엔진": {
            "icon": "PU", "visual": "engine",
            "options": {
                "최고출력형": option("최고출력형", 59, 51, 98, 77, 69, 59, 70, 159, "#ff304f", "큰 출력은 가속과 최고 속도를 높이지만 냉각과 무게 부담이 커집니다."),
                "균형형": option("균형형", 60, 48, 86, 76, 70, 60, 85, 151, "#ffb000", "출력과 신뢰성, 무게를 고르게 고려한 파워 유닛입니다."),
                "경량 효율형": option("경량 효율형", 58, 45, 79, 78, 70, 62, 89, 143, "#00d4ff", "최고 출력은 낮지만 가벼워 방향 전환과 효율에 도움을 줍니다."),
            },
        },
        "ERS": {
            "icon": "ER", "visual": "ers",
            "options": {
                "공격형": option("공격형", 58, 49, 95, 78, 70, 62, 69, 31, "#00ff88", "저장한 전기 에너지를 강하게 사용해 가속을 돕지만 에너지 관리가 어려워집니다."),
                "균형형": option("균형형", 59, 48, 86, 77, 70, 65, 84, 29, "#ffb000", "전기 에너지의 사용과 회수를 균형 있게 설정합니다."),
                "회생 중심형": option("회생 중심형", 58, 49, 77, 74, 69, 74, 88, 30, "#00d4ff", "감속할 때 운동 에너지를 전기로 더 많이 회수합니다. 순간 가속은 낮지만 운용이 안정적입니다."),
            },
        },
    }


# ============================================================
# 2. 차량 성능 계산
# ============================================================
def calculate_car_performance(part_data, selected_parts):
    """선택한 파츠들의 점수를 평균 내어 차량 전체 성능을 계산합니다.

    이 값은 실제 SI 물리량이 아니라 학습용 게임 지표입니다. 무게만 각 파츠의
    kg 값을 합산하고, 기본 차체·운전자·연료 무게 309kg을 더합니다.
    """
    metric_names = ["다운포스", "공기저항", "직선 속도", "코너링", "그립", "제동 성능", "안정성"]
    totals = {metric: 0 for metric in metric_names}
    total_weight = 309

    for part_name, option_name in selected_parts.items():
        selected_option = part_data[part_name]["options"][option_name]
        for metric in metric_names:
            totals[metric] += selected_option["metrics"][metric]
        total_weight += selected_option["weight"]

    part_count = len(selected_parts)
    performance = {metric: round(totals[metric] / part_count) for metric in metric_names}
    performance["무게"] = total_weight
    return performance


def calculate_performance_difference(current_performance, previous_performance):
    """파츠를 바꾸기 전과 후의 차이를 계산해 상승·하락 표시를 만들 때 사용합니다."""
    if previous_performance is None:
        return {metric: 0 for metric in current_performance}
    return {
        metric: current_performance[metric] - previous_performance.get(metric, current_performance[metric])
        for metric in current_performance
    }


def find_changed_part(current_selections, previous_selections):
    """어떤 파츠가 바뀌었는지 찾아 변화 설명에 사용합니다."""
    if not previous_selections:
        return None
    for part_name, option_name in current_selections.items():
        if previous_selections.get(part_name) != option_name:
            return part_name
    return None


# ============================================================
# 3. CSS와 공통 UI 구성 요소
# ============================================================
def apply_custom_css():
    """Streamlit 기본 화면을 레이싱 게임 HUD처럼 보이게 꾸밉니다."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@400;600;700&family=Noto+Sans+KR:wght@400;600;700&display=swap');
    :root { --red:#ff304f; --cyan:#00d4ff; --panel:#111720; --line:#2a3442; --text:#eef4fa; }
    .stApp { background: radial-gradient(circle at 50% 18%, #202a36 0, #0a0d12 46%, #050608 100%); color:var(--text); }
    .block-container { max-width:1500px; padding-top:1.2rem; padding-bottom:2rem; }
    html, body, [class*="css"] { font-family:'Noto Sans KR',sans-serif; }
    h1,h2,h3,.hud-title { font-family:'Oxanium','Noto Sans KR',sans-serif; }
    #MainMenu, footer, header { visibility:hidden; }
    .top-hud { border-top:3px solid var(--red); border-bottom:1px solid var(--line); padding:12px 18px; background:linear-gradient(90deg,#131922,#0c1016); display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; }
    .brand { font:700 28px 'Oxanium'; letter-spacing:2px; } .brand b{color:var(--red)}
    .stage { color:#8f9cac; font:600 12px 'Oxanium'; letter-spacing:1.5px; }
    .panel { background:linear-gradient(145deg,rgba(18,24,33,.97),rgba(9,13,18,.97)); border:1px solid var(--line); border-left:3px solid var(--red); padding:16px; border-radius:4px; box-shadow:0 14px 40px #0007; }
    .panel-title { font:700 14px 'Oxanium'; letter-spacing:2px; color:#fff; margin-bottom:12px; }
    .small-note { color:#8895a5; font-size:11px; line-height:1.55; }
    div[data-testid="stSelectbox"] label { color:#cbd5df!important; font-size:12px!important; font-weight:700!important; }
    div[data-baseweb="select"] > div { background:#10151d!important; border-color:#344150!important; color:#fff!important; }
    .metric-row { margin:9px 0 12px; }
    .metric-line { display:flex; justify-content:space-between; align-items:center; font-size:12px; margin-bottom:5px; }
    .metric-name { color:#c5cfda; font-weight:700; } .metric-value { font:700 13px 'Oxanium'; color:#fff; }
    .bar-bg { height:7px; background:#252d38; overflow:hidden; transform:skewX(-16deg); }
    .bar-fill { height:100%; background:linear-gradient(90deg,var(--cyan),#7d5cff); box-shadow:0 0 12px #00d4ff77; }
    .delta-up{color:#38ed98;font-size:11px;margin-left:6px}.delta-down{color:#ff5b70;font-size:11px;margin-left:6px}.delta-zero{color:#667382;font-size:11px;margin-left:6px}
    .tooltip { position:relative; display:inline-block; margin-left:5px; width:15px; height:15px; border:1px solid #667382; border-radius:50%; color:#aeb9c5; text-align:center; line-height:13px; font-size:10px; cursor:help; }
    .tooltip .tooltip-text { visibility:hidden; opacity:0; width:260px; background:#020305; color:#eaf1f7; border:1px solid #465466; padding:10px; border-radius:4px; position:absolute; z-index:9999; left:20px; top:-8px; line-height:1.55; font-size:11px; transition:.15s; box-shadow:0 8px 25px #000; }
    .tooltip:hover .tooltip-text { visibility:visible; opacity:1; }
    .lesson { margin-top:12px; padding:12px; background:#0b1118; border-left:3px solid var(--cyan); color:#c7d2dd; font-size:12px; line-height:1.65; }
    .change-box { padding:12px; margin-top:12px; background:linear-gradient(90deg,#15231f,#10171b); border:1px solid #285344; color:#d7f8e9; font-size:12px; line-height:1.65; }
    .car-stage { min-height:600px; background:radial-gradient(ellipse at center,#273340 0,#111720 46%,#080b0f 78%); border:1px solid #2d3845; position:relative; overflow:hidden; }
    .car-stage:before { content:''; position:absolute; inset:0; background:repeating-linear-gradient(90deg,transparent 0,transparent 49px,#ffffff08 50px),repeating-linear-gradient(0deg,transparent 0,transparent 49px,#ffffff08 50px); }
    .car-caption { text-align:center; font:700 13px 'Oxanium'; letter-spacing:3px; color:#9eabb9; padding-top:16px; }
    .selected-chip { display:inline-block; padding:4px 8px; margin:3px; background:#161e28; border:1px solid #354253; color:#9facba; font-size:10px; }
    .footer-help { margin-top:16px; padding:14px 18px; border:1px solid #283342; background:#0c1118; color:#9ba8b6; font-size:12px; }
    @media(max-width:900px){.car-stage{min-height:430px}.tooltip .tooltip-text{left:auto;right:20px}.brand{font-size:21px}}
    </style>
    """, unsafe_allow_html=True)


def render_tooltip(metric_name, explanations):
    """CSS hover 방식의 물음표 툴팁 HTML을 만듭니다."""
    safe_text = html.escape(explanations[metric_name])
    return f'<span class="tooltip">?<span class="tooltip-text">{safe_text}</span></span>'


def render_metric_bar(metric_name, value, explanations, difference=0, inverse=False):
    """성능 숫자, 변화량, 진행 막대를 한 줄로 표시합니다."""
    display_width = max(0, min(100, value))
    if difference > 0:
        delta_class, arrow = ("delta-down", "↑") if inverse else ("delta-up", "↑")
        delta_text = f"{arrow} +{difference}"
    elif difference < 0:
        delta_class, arrow = ("delta-up", "↓") if inverse else ("delta-down", "↓")
        delta_text = f"{arrow} {difference}"
    else:
        delta_class, delta_text = "delta-zero", "—"
    tooltip = render_tooltip(metric_name, explanations)
    unit = " kg" if metric_name == "무게" else ""
    # 무게는 kg이므로 막대에서는 650~850kg 구간을 0~100으로 바꿔 표현합니다.
    if metric_name == "무게":
        display_width = max(0, min(100, (value - 650) / 2))
    return f"""
    <div class="metric-row">
      <div class="metric-line"><span class="metric-name">{metric_name}{tooltip}</span>
      <span class="metric-value">{value}{unit}<span class="{delta_class}">{delta_text}</span></span></div>
      <div class="bar-bg"><div class="bar-fill" style="width:{display_width}%"></div></div>
    </div>"""


# ============================================================
# 4. 차량 SVG 시각화
# ============================================================
def render_car(part_data, selected_parts):
    """선택한 파츠 색상과 형태가 반영되는 F1 차량 SVG를 화면 중앙에 그립니다."""
    colors = {part_data[name]["visual"]: part_data[name]["options"][choice]["color"] for name, choice in selected_parts.items()}
    front_choice = selected_parts["프론트 윙"]
    rear_choice = selected_parts["리어 윙"]
    front_width = {"다운포스형": 310, "균형형": 280, "저저항형": 245}[front_choice]
    rear_width = {"고다운포스": 245, "중간 다운포스": 215, "저저항": 180}[rear_choice]
    chips = "".join(f'<span class="selected-chip">{html.escape(name)} · {html.escape(choice)}</span>' for name, choice in selected_parts.items())

    svg = f"""
    <div class="car-stage"><div class="car-caption">ASSEMBLY BAY // TOP VIEW</div>
    <svg viewBox="0 0 700 850" width="100%" height="520" role="img" aria-label="조립한 F1 차량의 위쪽 모습">
      <defs>
        <linearGradient id="body" x1="0" x2="1"><stop offset="0" stop-color="#b30f28"/><stop offset=".5" stop-color="#ff304f"/><stop offset="1" stop-color="#7b071a"/></linearGradient>
        <filter id="glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>
      <ellipse cx="350" cy="430" rx="250" ry="365" fill="#000" opacity=".42"/>
      <!-- 타이어: 선택한 컴파운드 색상으로 옆면 테두리가 바뀝니다. -->
      <g fill="#07090b" stroke="{colors['tires']}" stroke-width="8">
        <rect x="92" y="195" width="115" height="185" rx="24"/><rect x="493" y="195" width="115" height="185" rx="24"/>
        <rect x="72" y="565" width="140" height="210" rx="28"/><rect x="488" y="565" width="140" height="210" rx="28"/>
      </g>
      <!-- 프론트 윙과 리어 윙은 옵션에 따라 실제 SVG 폭도 달라집니다. -->
      <g fill="{colors['front_wing']}" filter="url(#glow)"><rect x="{350-front_width/2}" y="65" width="{front_width}" height="28" rx="5"/><rect x="{350-front_width/2+20}" y="100" width="{front_width-40}" height="12" rx="4"/></g>
      <g fill="{colors['rear_wing']}" filter="url(#glow)"><rect x="{350-rear_width/2}" y="778" width="{rear_width}" height="34" rx="5"/><rect x="{350-rear_width/2+15}" y="752" width="{rear_width-30}" height="12" rx="4"/></g>
      <!-- 차체와 바닥 -->
      <path d="M270 715 Q235 620 265 520 L300 360 Q315 230 335 125 L365 125 Q385 230 400 360 L435 520 Q465 620 430 715 Z" fill="{colors['floor']}" opacity=".85"/>
      <path d="M305 690 Q280 590 310 470 L326 315 L338 145 L362 145 L374 315 L390 470 Q420 590 395 690 Z" fill="url(#body)" stroke="#ff6a7e" stroke-width="3"/>
      <path d="M310 530 L220 610 L190 690 L305 660 M390 530 L480 610 L510 690 L395 660" fill="{colors['diffuser']}" opacity=".9"/>
      <path d="M325 335 Q350 295 375 335 L386 445 Q350 485 314 445 Z" fill="#080b10" stroke="#6f7b88" stroke-width="5"/>
      <ellipse cx="350" cy="405" rx="25" ry="31" fill="#f0b38e"/><path d="M326 402 Q350 365 374 402 L370 416 L330 416Z" fill="#1d2631"/>
      <rect x="325" y="500" width="50" height="98" rx="20" fill="{colors['engine']}" opacity=".8"/>
      <path d="M305 245 L215 300 L210 345 L316 320 M395 245 L485 300 L490 345 L384 320" fill="{colors['suspension']}" opacity=".85"/>
      <g stroke="{colors['brakes']}" stroke-width="9"><line x1="195" y1="285" x2="225" y2="285"/><line x1="505" y1="285" x2="475" y2="285"/><line x1="190" y1="660" x2="220" y2="660"/><line x1="510" y1="660" x2="480" y2="660"/></g>
      <circle cx="350" cy="555" r="13" fill="{colors['ers']}" filter="url(#glow)"/>
      <text x="350" y="255" text-anchor="middle" fill="#fff" font-size="34" font-family="Oxanium" font-weight="700">01</text>
      <g fill="#738191" font-family="Oxanium" font-size="12"><text x="34" y="40">AERO MAP</text><text x="570" y="40">READY</text><text x="34" y="825">PIT // GARAGE</text></g>
    </svg><div style="text-align:center;padding:0 12px 15px">{chips}</div></div>
    """
    st.markdown(svg, unsafe_allow_html=True)


# ============================================================
# 5. 선택 패널과 성능 패널
# ============================================================
def render_part_selector(part_data):
    """왼쪽 패널에서 사용자 선택값을 받고 선택한 파츠 딕셔너리를 반환합니다."""
    st.markdown('<div class="panel-title">01 // PARTS LOADOUT</div>', unsafe_allow_html=True)
    selected_parts = {}
    for part_name, info in part_data.items():
        option_names = list(info["options"].keys())
        selected_parts[part_name] = st.selectbox(
            f"{info['icon']}  {part_name}", option_names,
            key=f"part_{part_name}",
            help=f"{part_name} 옵션을 선택하면 차량 성능과 중앙 차량 모습이 즉시 바뀝니다.",
        )
    st.markdown('<div class="small-note">모든 선택은 즉시 반영됩니다. 각 점수는 실제 측정값이 아닌 학습용 0~100 게임 지표입니다.</div>', unsafe_allow_html=True)
    return selected_parts


def render_selected_part_details(part_data, selected_parts, active_part, explanations):
    """현재 바뀐 파츠의 개별 성능과 물리 설명을 보여 줍니다."""
    part_name = active_part or "프론트 윙"
    selected_option = part_data[part_name]["options"][selected_parts[part_name]]
    st.markdown(f'<div class="panel-title">02 // {html.escape(part_name.upper())} ANALYSIS</div>', unsafe_allow_html=True)
    st.markdown(f"**{selected_option['name']}**")
    for metric, value in selected_option["metrics"].items():
        st.markdown(render_metric_bar(metric, value, explanations), unsafe_allow_html=True)
    st.markdown(f'<div class="metric-line"><span class="metric-name">파츠 무게{render_tooltip("무게", explanations)}</span><span class="metric-value">{selected_option["weight"]} kg</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="lesson"><b>PHYSICS NOTE</b><br>{html.escape(selected_option["lesson"])}</div>', unsafe_allow_html=True)


def render_performance_panel(car_performance, performance_difference, explanations, changed_part, part_data, selected_parts):
    """오른쪽 HUD에 차량 전체 성능과 직전 선택 대비 변화량을 표시합니다."""
    st.markdown('<div class="panel-title">03 // MY F1 CAR</div>', unsafe_allow_html=True)
    for metric, value in car_performance.items():
        st.markdown(
            render_metric_bar(metric, value, explanations, performance_difference.get(metric, 0), inverse=metric in ["공기저항", "무게"]),
            unsafe_allow_html=True,
        )
    if changed_part:
        chosen_option = part_data[changed_part]["options"][selected_parts[changed_part]]
        positive = [m for m, d in performance_difference.items() if d > 0 and m != "무게"]
        negative = [m for m, d in performance_difference.items() if d < 0 and m != "무게"]
        summary = f"<b>{html.escape(changed_part)}</b>를 <b>{html.escape(chosen_option['name'])}</b>(으)로 변경했습니다. "
        if positive:
            summary += f"{', '.join(positive)} 지표가 상승했습니다. "
        if negative:
            summary += f"{', '.join(negative)} 지표는 낮아졌습니다. "
        summary += html.escape(chosen_option["lesson"])
        st.markdown(f'<div class="change-box">{summary}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="change-box">파츠를 바꾸면 직전 설정과 비교한 ↑ 상승 / ↓ 하락 수치가 여기에 표시됩니다.</div>', unsafe_allow_html=True)


def render_help_section():
    """게임 지표와 실제 물리량의 차이를 명확히 안내합니다."""
    st.markdown("""
    <div class="footer-help"><b>LEARNING MODE 안내</b> · 이 앱의 0~100 수치는 실제 F1 팀의 측정 데이터가 아니라 물리적 경향을 쉽게 비교하기 위한 게임용 지표입니다.
    실제 차량 성능은 속도, 날씨, 트랙, 타이어 온도, 차량 자세 등 훨씬 많은 조건에 따라 달라집니다. 공기저항과 무게는 수치가 낮을수록 대체로 유리하지만, 냉각·안정성·내구성과의 균형이 필요합니다.</div>
    """, unsafe_allow_html=True)


# ============================================================
# 6. 메인 함수: 데이터, 계산, 화면을 순서대로 연결
# ============================================================
def main():
    """Streamlit 앱 전체 실행 흐름을 관리합니다."""
    st.set_page_config(page_title="F1 Physics Garage", page_icon="🏁", layout="wide", initial_sidebar_state="collapsed")
    apply_custom_css()

    # 화면과 계산에서 함께 사용할 원본 데이터를 한 번만 준비합니다.
    part_data = get_part_data()
    explanations = get_physics_explanations()

    st.markdown('<div class="top-hud"><div class="brand">F1 <b>PHYSICS</b> GARAGE</div><div class="stage">BUILD 01 · AERO & PERFORMANCE LAB</div></div>', unsafe_allow_html=True)

    # 왼쪽에서 사용자의 파츠 선택값을 받은 뒤 전체 차량 성능을 즉시 다시 계산합니다.
    left_column, center_column, right_column = st.columns([0.9, 1.75, 1.0], gap="medium")
    with left_column:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        selected_parts = render_part_selector(part_data)
        st.markdown('</div>', unsafe_allow_html=True)

    current_performance = calculate_car_performance(part_data, selected_parts)

    # session_state에 직전 설정을 보관해야 Streamlit이 재실행된 뒤에도 변화량을 비교할 수 있습니다.
    previous_selections = st.session_state.get("previous_selections")
    previous_performance = st.session_state.get("previous_performance")
    changed_part = find_changed_part(selected_parts, previous_selections)
    performance_difference = calculate_performance_difference(current_performance, previous_performance)

    with center_column:
        render_car(part_data, selected_parts)
        st.markdown('<div class="panel" style="margin-top:14px">', unsafe_allow_html=True)
        render_selected_part_details(part_data, selected_parts, changed_part, explanations)
        st.markdown('</div>', unsafe_allow_html=True)

    with right_column:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        render_performance_panel(current_performance, performance_difference, explanations, changed_part, part_data, selected_parts)
        st.markdown('</div>', unsafe_allow_html=True)

    render_help_section()

    # 현재 값을 깊은 복사로 저장하여 다음 파츠 변경 때 비교 기준으로 사용합니다.
    st.session_state["previous_selections"] = deepcopy(selected_parts)
    st.session_state["previous_performance"] = deepcopy(current_performance)


if __name__ == "__main__":
    main()

