import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="금융 기상청 RDI", layout="wide")

st.title("📊 금융 기상청 : Recovery Duration Index (RDI)")
st.markdown("""
PDF 수식 기반 **회복기간 분포 → 분위수 → 로그 스케일 → 0–100 지수화**를 구현한 데모입니다.
""")

cases = {
    "2008 글로벌 금융위기": {
        "t_q": {0.2: 120, 0.5: 198, 0.8: 320},
        "weather": "🌪 태풍",
        "comment": "금융 시스템 붕괴로 회복 위험률이 장기간 낮았던 국면"
    },
    "2020 코로나 쇼크": {
        "t_q": {0.2: 35, 0.5: 63, 0.8: 110},
        "weather": "🌦 소나기",
        "comment": "정책 대응으로 회복 위험률이 빠르게 정상화된 국면"
    }
}

def calculate_rdi(T_star, Z_min, Z_max):
    Z = np.log(1 + T_star)
    rdi = 100 * (Z_max - Z) / (Z_max - Z_min)
    return np.clip(rdi, 0, 100)

selected = st.selectbox("📂 하방 이벤트 선택", list(cases.keys()))
data = cases[selected]

q = st.radio(
    "📌 회복 시나리오 선택",
    options=[0.2, 0.5, 0.8],
    format_func=lambda x: f"{int(x*100)}% 분위수 ({'낙관' if x==0.2 else '기준' if x==0.5 else '보수'})"
)

T_star = data["t_q"][q]

all_T = [v for c in cases.values() for v in c["t_q"].values()]
Z_values = np.log(1 + np.array(all_T))
Z_min, Z_max = Z_values.min(), Z_values.max()

RDI = calculate_rdi(T_star, Z_min, Z_max)

col1, col2, col3 = st.columns(3)
col1.metric("회복기간 분위수 (일)", f"{T_star}")
col2.metric("RDI 점수", f"{RDI:.1f}")
col3.metric("금융 기상 상태", data["weather"])

st.markdown("### 🧠 해석")
st.info(
    f"""
    선택한 시나리오({int(q*100)}% 분위수)는  
    **회복기간이 {T_star}일 이하일 확률이 {int(q*100)}%**임을 의미합니다.  
    로그 변환 및 역방향 정규화를 통해 **시간 리스크를 0–100 지수(RDI)**로 변환했습니다.
    
    👉 {data["comment"]}
    """
)

st.markdown("### 📈 회복기간 시나리오 비교")

df_plot = pd.DataFrame({
    "Scenario": ["20%", "50%", "80%"],
    "Recovery Days": [
        data["t_q"][0.2],
        data["t_q"][0.5],
        data["t_q"][0.8]
    ]
})

st.bar_chart(df_plot.set_index("Scenario"))

st.caption("""
RDI 정의: 회복기간 분위수 기반 로그 스케일링 후  
0–100 범위로 정규화한 회복 지연 리스크 지표
""")
