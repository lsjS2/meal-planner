import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import json
import os
import google.generativeai as genai

# Set up page configurations
st.set_page_config(
    page_title="오늘 뭐 먹지? - AI 맞춤 식단 플래너",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Premium Styling for Cream Background & Coral Points
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

/* Main App styling */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #FFFDF7 !important;
    color: #2B2D42 !important;
    font-family: 'Outfit', 'Noto Sans KR', sans-serif !important;
}

/* Custom Header Container */
.app-header {
    background: linear-gradient(135deg, #FF6B35 0%, #FF8F5A 100%);
    padding: 35px 40px;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 10px 25px rgba(255, 107, 53, 0.15);
}

.app-header h1 {
    font-weight: 800;
    font-size: 2.8rem;
    margin: 0;
    letter-spacing: -1px;
    color: white !important;
}

.app-header p {
    font-size: 1.15rem;
    opacity: 0.9;
    margin-top: 10px;
    margin-bottom: 0;
    font-weight: 300;
}

/* Premium Card UI */
.meal-card {
    background-color: #FFFFFF;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 25px rgba(255, 107, 53, 0.04);
    border: 1px solid rgba(255, 107, 53, 0.08);
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.meal-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(255, 107, 53, 0.12);
    border-color: rgba(255, 107, 53, 0.4);
}

.meal-card-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #FF6B35;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.meal-card-menu {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2B2D42;
    margin-bottom: 15px;
}

.meal-nutrients {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    text-align: center;
}

.nutrient-badge {
    background-color: #FFFDF7;
    border: 1px solid rgba(255, 107, 53, 0.08);
    border-radius: 10px;
    padding: 8px 4px;
}

.nutrient-val {
    font-size: 0.95rem;
    font-weight: 700;
    color: #FF6B35;
}

.nutrient-label {
    font-size: 0.72rem;
    color: #6C757D;
    margin-top: 2px;
}

/* Highlight metrics */
.calories-summary-box {
    background-color: #FFFFFF;
    border-radius: 16px;
    padding: 20px;
    border-left: 5px solid #FF6B35;
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.05);
    margin-bottom: 25px;
}

.calories-title {
    font-size: 0.95rem;
    color: #6C757D;
    font-weight: 600;
}

.calories-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #FF6B35;
    margin-top: 5px;
}

/* AI Comment Card */
.ai-comment-box {
    background-color: #FFF9F5;
    border: 1px dashed rgba(255, 107, 53, 0.3);
    border-radius: 16px;
    padding: 20px;
    margin-top: 25px;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.03);
}

.ai-comment-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #FF6B35;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.ai-comment-text {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #4A4E69;
}

/* Custom styles for Streamlit native inputs */
div.stButton > button:first-child {
    background-color: #FF6B35 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 1.15rem !important;
    box-shadow: 0 4px 15px rgba(255, 107, 53, 0.25) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    margin-top: 15px;
}

div.stButton > button:first-child:hover {
    background-color: #FF8052 !important;
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.35) !important;
    transform: translateY(-2px) !important;
}

/* Input Fields overrides */
.stTextInput input, .stNumberInput input {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(255, 107, 53, 0.15) !important;
    border-radius: 10px !important;
    color: #2B2D42 !important;
}

.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #FF6B35 !important;
    box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.2) !important;
}

/* Section title custom styling */
.section-title {
    color: #FF6B35;
    font-weight: 700;
    margin-bottom: 15px;
    border-bottom: 2px solid rgba(255, 107, 53, 0.15);
    padding-bottom: 5px;
}
</style>
"""

# Inject custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Main Application Title Header
st.markdown("""
<div class="app-header">
    <h1>오늘 뭐 먹지? 🍱</h1>
    <p>AI 맞춤 영양 분석 및 지능형 하루 식단 계획 플래너</p>
</div>
""", unsafe_allow_html=True)

# Helper function to parse JSON safely from LLM output
def clean_and_parse_json(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    return json.loads(text)

# Helper to safe-get meal fields
def get_safe_meal(meal_data, default_name="식사"):
    return {
        "메뉴": meal_data.get("메뉴", default_name),
        "칼로리": int(meal_data.get("칼로리", 0)),
        "탄수화물": int(meal_data.get("탄수화물", 0)),
        "단백질": int(meal_data.get("단백질", 0)),
        "지방": int(meal_data.get("지방", 0))
    }

# Mock data fallback function when API fails or key is missing
def get_mock_meal_plan(target_calories, carb_ratio, protein_ratio, fat_ratio, meals):
    total_carb = int(target_calories * (carb_ratio / 100) / 4)
    total_prot = int(target_calories * (protein_ratio / 100) / 4)
    total_fat = int(target_calories * (fat_ratio / 100) / 9)
    
    dist = {
        "아침": 0.25,
        "점심": 0.35,
        "저녁": 0.30,
        "간식": 0.10
    }
    
    result = {}
    for meal, pct in dist.items():
        user_input = meals.get(meal, "").strip()
        cal = int(target_calories * pct)
        c = int(total_carb * pct)
        p = int(total_prot * pct)
        f = int(total_fat * pct)
        
        if user_input:
            menu = f"{user_input}"
        else:
            if meal == "아침":
                menu = "바나나 1개, 오트밀 죽, 삶은 계란 2개"
            elif meal == "점심":
                menu = "현미공기밥 1공기, 구운 닭가슴살 120g, 브로콜리 볶음"
            elif meal == "저녁":
                menu = "연어 스테이크 150g, 찐 고구마 1개, 신선한 그린 샐러드"
            else:
                menu = "아몬드 10알, 그릭 요거트 100g"
                
        result[meal] = {
            "메뉴": menu,
            "칼로리": cal,
            "탄수화물": c,
            "단백질": p,
            "지방": f
        }
    
    result["한마디"] = f"오늘은 요청하신 목표 칼로리({target_calories} kcal)와 탄단지 비율({carb_ratio}:{protein_ratio}:{fat_ratio})을 기준으로 최적의 균형 잡힌 식단을 시뮬레이션했습니다. (※ API 미연동 또는 호출 오류로 인한 대체 데모 식단입니다.)"
    return result

# Main Gemini API meal generation function
def generate_meal_plan(target_calories, carb_ratio, protein_ratio, fat_ratio, meals):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    
    if not api_key:
        return get_mock_meal_plan(target_calories, carb_ratio, protein_ratio, fat_ratio, meals)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
당신은 최고의 AI 맞춤 식단 플래너이자 공인 영양사입니다. 사용자의 목표 칼로리와 탄단지 비율, 그리고 사용자가 이미 입력한 식단 선호를 바탕으로 하루 식단 계획을 작성해 주세요.

[목표 데이터]
- 하루 목표 칼로리: {target_calories} kcal
- 목표 탄단지 비율 (탄수화물:단백질:지방 비율): {carb_ratio}% : {protein_ratio}% : {fat_ratio}%
  (참고: 1g당 칼로리는 탄수화물 4kcal, 단백질 4kcal, 지방 9kcal입니다.)

[사용자 입력 식단]
- 아침: {meals.get('아침', '').strip() if meals.get('아침', '').strip() else '비어 있음 (AI가 자동 추천)'}
- 점심: {meals.get('점심', '').strip() if meals.get('점심', '').strip() else '비어 있음 (AI가 자동 추천)'}
- 저녁: {meals.get('저녁', '').strip() if meals.get('저녁', '').strip() else '비어 있음 (AI가 자동 추천)'}
- 간식: {meals.get('간식', '').strip() if meals.get('간식', '').strip() else '비어 있음 (AI가 자동 추천)'}

[작성 및 계산 지침]
1. 사용자가 특정 끼니에 음식을 입력한 경우(예: '닭가슴살 샐러드', '제육볶음과 현미밥' 등), 그 음식을 기반으로 칼로리와 탄단지(g) 수치를 합리적으로 추정하여 채워주세요.
2. 사용자가 입력칸을 비워둔 끼니는, 남은 칼로리와 탄단지 목표 비율에 맞게 건강하고 맛있는 영양 균형 식단을 직접 추천해 채워주세요.
3. 네 끼니(아침, 점심, 저녁, 간식)의 총 칼로리의 합이 목표 칼로리({target_calories} kcal)의 ±10% 이내가 되도록 칼로리를 정교하게 배분해 주세요.
4. 네 끼니의 총 탄수화물(g), 단백질(g), 지방(g) 총합이 목표 탄단지 비율({carb_ratio}:{protein_ratio}:{fat_ratio})에 최대한 가깝게 맞추어 각 메뉴의 수치(g)를 계산해 주세요. (탄수화물=g*4, 단백질=g*4, 지방=g*9)
5. 각 끼니별 메뉴명은 구체적이고 맛있게 표현해 주세요 (예: '현미밥 1공기와 제육볶음, 시금치나물' 등).
6. '한마디'에는 오늘 제안하는 식단의 전체적인 영양학적 특징, 조언, 응원의 한마디를 다정하고 전문적인 톤(한국어)으로 작성해 주세요.

[응답 형식]
반드시 다음 구조의 JSON 포맷으로 응답해 주세요. 다른 설명 텍스트는 일체 포함하지 마세요.
{{
  "아침": {{"메뉴": "구체적인 메뉴명", "칼로리": 아침칼로리_숫자, "탄수화물": 탄수화물_g_숫자, "단백질": 단백질_g_숫자, "지방": 지방_g_숫자}},
  "점심": {{"메뉴": "구체적인 메뉴명", "칼로리": 점심칼로리_숫자, "탄수화물": 탄수화물_g_숫자, "단백질": 단백질_g_숫자, "지방": 지방_g_숫자}},
  "저녁": {{"메뉴": "구체적인 메뉴명", "칼로리": 저녁칼로리_숫자, "탄수화물": 탄수화물_g_숫자, "단백질": 단백질_g_숫자, "지방": 지방_g_숫자}},
  "간식": {{"메뉴": "구체적인 메뉴명", "칼로리": 간식칼로리_숫자, "탄수화물": 탄수화물_g_숫자, "단백질": 단백질_g_숫자, "지방": 지방_g_숫자}},
  "한마디": "오늘 식단에 대한 영양사의 조언 및 격려"
}}
"""
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        parsed = clean_and_parse_json(response.text)
        result = {}
        for meal_name in ["아침", "점심", "저녁", "간식"]:
            if meal_name in parsed:
                result[meal_name] = get_safe_meal(parsed[meal_name], default_name=f"{meal_name} 식사")
            else:
                result[meal_name] = {"메뉴": "추천 식사", "칼로리": 0, "탄수화물": 0, "단백질": 0, "지방": 0}
        
        result["한마디"] = parsed.get("한마디", "균형 잡힌 식단으로 활기찬 하루를 보내세요!")
        return result
    except Exception as e:
        st.error(f"AI 식단 생성 과정에서 에러가 발생했습니다: {e}. 데모 데이터로 대체합니다.")
        return get_mock_meal_plan(target_calories, carb_ratio, protein_ratio, fat_ratio, meals)

# Initialize Session State Variables
if "meal_plan" not in st.session_state:
    st.session_state.meal_plan = None
if "carb_slider" not in st.session_state:
    st.session_state.carb_slider = 50
if "protein_slider" not in st.session_state:
    st.session_state.protein_slider = 30
if "fat_slider" not in st.session_state:
    st.session_state.fat_slider = 20

# Left & Right Columns Layout
col_left, col_right = st.columns([1, 1.25], gap="large")

# ----------------- LEFT COLUMN: INPUT FORM -----------------
with col_left:
    st.markdown("<h2 class='section-title'>⚙️ 식단 설정 및 선호도</h2>", unsafe_allow_html=True)
    
    # 1. Target Calories
    target_calories = st.number_input(
        "🔥 오늘 목표 칼로리 (kcal)",
        min_value=500,
        max_value=8000,
        value=2000,
        step=50,
        help="하루 동안 섭취하고자 하는 총 목표 칼로리 수치입니다."
    )
    
    # 2. Target Type and synchronisation logic
    expected_ratios = {
        "다이어트": (50, 30, 20),
        "유지": (55, 25, 20),
        "근성장": (45, 35, 20)
    }
    
    carb_val = st.session_state.carb_slider
    prot_val = st.session_state.protein_slider
    fat_val = st.session_state.fat_slider
    current_ratios = (carb_val, prot_val, fat_val)
    
    detected_type = "수동 설정"
    for t_type, ratios in expected_ratios.items():
        if current_ratios == ratios:
            detected_type = t_type
            break
            
    type_options = ["다이어트", "유지", "근성장", "수동 설정"]
    default_idx = type_options.index(detected_type)
    
    selected_type = st.radio(
        "🎯 목표 유형 선택",
        ["다이어트", "유지", "근성장", "수동 설정"],
        index=default_idx,
        horizontal=True,
        help="목표 유형에 따라 탄/단/지 비율이 자동으로 지정됩니다."
    )
    
    # Rerun if user clicked a new preset type
    if selected_type != detected_type and selected_type != "수동 설정":
        new_carb, new_prot, new_fat = expected_ratios[selected_type]
        st.session_state.carb_slider = new_carb
        st.session_state.protein_slider = new_prot
        st.session_state.fat_slider = new_fat
        st.rerun()

    # 3. Macro Sliders
    st.markdown("<p style='font-weight:600; margin-bottom: 5px; color:#2B2D42;'>🌾 탄단지 비율 설정 (%)</p>", unsafe_allow_html=True)
    c_slide = st.slider("탄수화물 비율 (Carbohydrates)", 0, 100, key="carb_slider")
    p_slide = st.slider("단백질 비율 (Protein)", 0, 100, key="protein_slider")
    f_slide = st.slider("지방 비율 (Fat)", 0, 100, key="fat_slider")
    
    # Total percentage warning
    total_ratio = c_slide + p_slide + f_slide
    can_generate = True
    
    if total_ratio != 100:
        st.warning(f"⚠️ 탄수화물, 단백질, 지방 비율의 합이 100%이어야 합니다. (현재 합: **{total_ratio}%**)")
        can_generate = False
    else:
        st.success(f"✅ 탄단지 비율의 합이 100%입니다! ({c_slide} : {p_slide} : {f_slide})")

    # 4. Meal inputs
    st.markdown("<p style='font-weight:600; margin-top:20px; margin-bottom: 5px; color:#2B2D42;'>🍽️ 끼니별 선호 음식 입력 (선택사항)</p>", unsafe_allow_html=True)
    st.markdown("<span style='font-size:0.82rem; color:#6C757D;'>직접 입력한 끼니는 AI가 이를 반영하여 수치를 계산하고, 비워둔 칸은 자동으로 건강하게 채워줍니다.</span>", unsafe_allow_html=True)
    
    meal_b = st.text_input("🌅 아침식사", placeholder="예) 계란 2개와 바나나 (비워두면 AI 추천)", key="input_b")
    meal_l = st.text_input("☀️ 점심식사", placeholder="예) 현미밥과 제육볶음 (비워두면 AI 추천)", key="input_l")
    meal_d = st.text_input("🌙 저녁식사", placeholder="예) 닭가슴살 샐러드 (비워두면 AI 추천)", key="input_d")
    meal_s = st.text_input("🍪 간식", placeholder="예) 그릭요거트와 아몬드 (비워두면 AI 추천)", key="input_s")

    # 5. Generate Button
    generate_clicked = st.button("🥗 식단 생성하기", disabled=not can_generate)
    
    if generate_clicked:
        with st.spinner("🧑‍🍳 AI 영양사가 영양 가이드라인에 맞춰 최적의 하루 식단을 짜고 있습니다..."):
            result_plan = generate_meal_plan(target_calories, c_slide, p_slide, f_slide, {
                "아침": meal_b,
                "점심": meal_l,
                "저녁": meal_d,
                "간식": meal_s
            })
            if result_plan:
                st.session_state.meal_plan = result_plan
                st.rerun()

# ----------------- RIGHT COLUMN: OUTPUT & VISUALS -----------------
with col_right:
    st.markdown("<h2 class='section-title'>🍽️ 생성된 AI 맞춤 식단 계획</h2>", unsafe_allow_html=True)
    
    if st.session_state.meal_plan:
        plan = st.session_state.meal_plan
        
        # Calculate daily aggregates
        total_cal = sum(plan[m]["칼로리"] for m in ["아침", "점심", "저녁", "간식"])
        total_carb = sum(plan[m]["탄수화물"] for m in ["아침", "점심", "저녁", "간식"])
        total_prot = sum(plan[m]["단백질"] for m in ["아침", "점심", "저녁", "간식"])
        total_fat = sum(plan[m]["지방"] for m in ["아침", "점심", "저녁", "간식"])
        
        # 1. Total calorie aggregate card
        st.markdown(f"""
        <div class="calories-summary-box">
            <div class="calories-title">🍱 오늘 제안된 식단의 총 섭취량</div>
            <div class="calories-value">{total_cal:,} kcal <span style='font-size:1.25rem; font-weight:400; color:#6C757D;'>/ 목표 {target_calories:,} kcal</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Meal Cards Grid (2x2 layout inside Streamlit using sub-columns)
        st.markdown("<p style='font-weight:600; margin-bottom:12px; color:#2B2D42;'>🍲 끼니별 식단 상세 정보</p>", unsafe_allow_html=True)
        col_m1, col_m2 = st.columns(2)
        
        meal_display_info = [
            ("아침", "🌅 아침 식사", col_m1),
            ("점심", "☀️ 점심 식사", col_m2),
            ("저녁", "🌙 저녁 식사", col_m1),
            ("간식", "🍪 간식", col_m2)
        ]
        
        for key, title_text, target_col in meal_display_info:
            m_data = plan[key]
            with target_col:
                st.markdown(f"""
                <div class="meal-card">
                    <div class="meal-card-title">{title_text}</div>
                    <div class="meal-card-menu">{m_data['메뉴']}</div>
                    <div class="meal-nutrients">
                        <div class="nutrient-badge">
                            <div class="nutrient-val">{m_data['칼로리']}</div>
                            <div class="nutrient-label">kcal</div>
                        </div>
                        <div class="nutrient-badge">
                            <div class="nutrient-val">{m_data['탄수화물']}g</div>
                            <div class="nutrient-label">탄수화물</div>
                        </div>
                        <div class="nutrient-badge">
                            <div class="nutrient-val">{m_data['단백질']}g</div>
                            <div class="nutrient-label">단백질</div>
                        </div>
                        <div class="nutrient-badge">
                            <div class="nutrient-val">{m_data['지방']}g</div>
                            <div class="nutrient-label">지방</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        # 3. Plotly Charts side-by-side
        st.markdown("<p style='font-weight:600; margin-top:10px; margin-bottom:12px; color:#2B2D42;'>📊 영양 성분 구성 및 칼로리 달성도</p>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        
        # 3a. Donut Chart (Macronutrients)
        with col_c1:
            labels = ['탄수화물 (Carbs)', '단백질 (Protein)', '지방 (Fat)']
            values = [total_carb, total_prot, total_fat]
            colors = ['#FF6B35', '#FF9F1C', '#FFD166']
            
            fig_donut = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=.45,
                marker=dict(colors=colors, line=dict(color='#FFFDF7', width=2.5)),
                hoverinfo='label+percent+value',
                textinfo='percent',
                textfont=dict(size=12, family='Outfit, Noto Sans KR', color='#2B2D42')
            )])
            
            fig_donut.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=10, b=50, l=10, r=10),
                height=220,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#2B2D42', family='Outfit, Noto Sans KR')
            )
            st.plotly_chart(fig_donut, use_container_width=True, key="macro_donut_chart")
            
        # 3b. Gauge Chart (Calorie Target)
        with col_c2:
            max_gauge = max(target_calories * 1.2, total_cal * 1.1)
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_cal,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "목표 칼로리 달성도 (%)", 'font': {'size': 14, 'color': '#2B2D42', 'family': 'Outfit, Noto Sans KR'}},
                number={'suffix': " kcal", 'font': {'color': '#FF6B35', 'size': 20, 'family': 'Outfit, Noto Sans KR'}},
                gauge={
                    'axis': {'range': [0, max_gauge], 'tickwidth': 1, 'tickcolor': "#FF6B35"},
                    'bar': {'color': "#FF6B35"},
                    'bgcolor': "#FFFFFF",
                    'borderwidth': 1.5,
                    'bordercolor': "rgba(255, 107, 53, 0.2)",
                    'steps': [
                        {'range': [0, target_calories * 0.9], 'color': 'rgba(255, 107, 53, 0.04)'},
                        {'range': [target_calories * 0.9, target_calories * 1.1], 'color': 'rgba(255, 107, 53, 0.15)'},
                        {'range': [target_calories * 1.1, max_gauge], 'color': 'rgba(231, 29, 54, 0.08)'}
                    ],
                    'threshold': {
                        'line': {'color': "#FF6B35", 'width': 3},
                        'thickness': 0.75,
                        'value': target_calories
                    }
                }
            ))
            
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=220,
                margin=dict(t=30, b=10, l=10, r=10),
                font=dict(color='#2B2D42', family='Outfit, Noto Sans KR')
            )
            st.plotly_chart(fig_gauge, use_container_width=True, key="calorie_gauge_chart")
            
        # 4. AI Coach Comment
        st.markdown(f"""
        <div class="ai-comment-box">
            <div class="ai-comment-title">💡 AI 영양사의 한마디</div>
            <div class="ai-comment-text">{plan.get('한마디', '균형 잡힌 식단으로 건강한 삶을 꾸려보세요!')}</div>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # Appetite stimulating / beautiful welcome placeholder card
        st.markdown("""
        <div style="background-color: #FFFFFF; border-radius: 16px; padding: 60px 40px; text-align: center; border: 1px dashed rgba(255, 107, 53, 0.25); box-shadow: 0 8px 25px rgba(255, 107, 53, 0.02); margin-top: 25px;">
            <span style="font-size: 5rem; display: block; margin-bottom: 20px;">🥗🥗</span>
            <h3 style="color: #FF6B35; margin-top: 10px; font-weight: 700;">맞춤형 식단 계획을 받아보세요!</h3>
            <p style="color: #6C757D; max-width: 500px; margin: 15px auto 30px auto; line-height: 1.6; font-size: 0.95rem;">
                왼쪽 설정 폼에서 <b>오늘 목표 칼로리</b>와 <b>원하는 탄단지 구성 비율</b>을 설정하고, 알고 있거나 직접 먹고 싶은 메뉴가 있다면 끼니별 칸에 적어주세요. 나머지는 AI가 완벽하게 채워드립니다!
            </p>
            <div style="display: inline-block; padding: 10px 24px; background-color: #FFFDF7; border-radius: 25px; border: 1px solid rgba(255, 107, 53, 0.15); font-size: 0.88rem; color: #FF6B35; font-weight: 600; box-shadow: 0 4px 10px rgba(255,107,53,0.03);">
                ✨ 다이어트(탄50/단30/지20) | 유지(탄55/단25/지20) | 근성장(탄45/단35/지20)
            </div>
        </div>
        """, unsafe_allow_html=True)
