# 🍱 오늘 뭐 먹지? - AI 맞춤 식단 플래너

사용자의 목표 칼로리와 탄단지 비율에 맞춰 AI가 최적의 건강 식단을 추천하고 시각화 분석을 제공하는 Streamlit 웹 애플리케이션입니다.

---

## ✨ 주요 기능

- **🎯 맞춤 목표 설정**: 다이어트, 유지, 근성장 등 목표에 따른 탄단지(탄수화물/단백질/지방) 비율 자동 세팅 및 수동 세부 조절 기능.
- **🍽️ 지능형 끼니 설계**: 사용자가 먹고 싶은 메뉴를 입력하면 해당 음식을 기반으로 칼로리를 역산하고, 비워둔 끼니는 남은 칼로리에 맞춰 AI가 똑똑하게 건강 식단으로 채워줍니다.
- **📊 영양 분석 시각화**: Plotly 기반의 **탄단지 비율 도넛 차트** 및 **목표 칼로리 달성도 게이지 차트**를 통한 시각적 피드백 제공.
- **💡 AI 영양사 코칭**: 오늘 식단 구성의 특징과 영양학적 조언을 담은 친근한 한마디 코멘트 기능.

---

## 🛠️ 기술 스택

- **Frontend & App Logic**: Python, Streamlit
- **AI Engine**: Google Gemini API (`gemini-1.5-flash` 모델)
- **Data Visualization**: Plotly (Donut, Gauge Chart)

---

## 🚀 시작 가이드

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. API Key 설정
`.streamlit/secrets.toml` 파일에 Gemini API 키를 입력합니다.
```toml
GEMINI_API_KEY = "발급받은_API_키"
```

### 3. 애플리케이션 실행
```bash
streamlit run app.py
```
