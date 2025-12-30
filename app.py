import streamlit as st
import pandas as pd

# 1. 页面基础配置：设置标题、图标和布局
st.set_page_config(
    page_title="招生问答智能咨询系统",
    page_icon="🎓",
    layout="wide" # 使用宽屏模式，让视觉更开阔
)

# 2. 自定义 CSS 样式 (装修核心)
st.markdown("""
    <style>
    /* 修改主背景颜色 */
    .stApp {
        background-color: #f8f9fa;
    }
    /* 美化卡片容器 */
    .qa-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #4D96FF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    /* 修改标题字体 */
    h1 {
        color: #1E2E5D;
        font-family: 'Microsoft YaHei';
    }
    </style>
    """, unsafe_allow_html=True)

def char_match_similarity(user_input, standard_question):
    """算法逻辑保持不变"""
    if not user_input: return 0.0
    user_chars = set(user_input)
    standard_chars = set(str(standard_question))
    intersection = user_chars.intersection(standard_chars)
    union = user_chars.union(standard_chars)
    base_score = len(intersection) / len(union)
    if user_input in str(standard_question):
        base_score += 0.5
    return min(base_score, 1.0)

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        return df[['标准问题', '答案']].dropna()
    except Exception as e:
        st.error(f"无法读取文件: {e}")
        return None

# --- 侧边栏装修 ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/144/000000/university.png", width=100) # 添加一个学校图标
    st.title("系统控制台")
    st.markdown("---")
    file_path = "招生问答汇总20210615（加标准问题）.xlsx"
    top_n = st.slider("🔍 推荐显示数量", 1, 10, 5)
    st.info("💡 提示：输入关键词如“体育”、“录取”获取最精准解答。")

# --- 主界面装修 ---
st.title("🎓 招生问答智能咨询系统")
st.caption("专业的智能咨询助手，为您解答每一个报考疑惑")

# 创建搜索框（美化版）
user_input = st.text_input("", placeholder="🔍 请在此输入您想咨询的问题...", label_visibility="collapsed")

data = load_data(file_path)

if data is not None and user_input:
    qa_pairs = data.values.tolist()
    results = []
    for q, a in qa_pairs:
        sim = char_match_similarity(user_input.lower(), str(q).lower())
        if sim > 0:
            results.append((q, a, sim))
    
    results.sort(key=lambda x: x[2], reverse=True)
    matched_questions = results[:top_n]

    if not matched_questions:
        st.error("😕 抱歉，没有找到相关结果，请尝试简化您的关键词。")
    else:
        # 1. 精准匹配特效
        exact_match = next((item for item in matched_questions if user_input == str(item[0]).strip()), None)
        
        if exact_match:
            st.balloons() # 庆祝气球特效
            st.success(f"🎯 找到精准匹配：{exact_match[0]}")
            st.markdown(f"""<div class='qa-card' style='border-left-color: #2ecc71;'>
                <strong>官方权威回答：</strong><br>{exact_match[1]}
            </div>""", unsafe_allow_html=True)
        
        # 2. 推荐列表美化
        st.subheader("💡 您可能想找：")
        for idx, (q, a, sim) in enumerate(matched_questions, start=1):
            # 使用 HTML 创建卡片样式
            st.markdown(f"""
                <div class="qa-card">
                    <span style="color: #4D96FF; font-weight: bold;">推荐 {idx}</span>
                    <h4 style="margin: 5px 0;">{q}</h4>
                    <small>匹配程度: {sim:.1%}</small>
                </div>
            """, unsafe_allow_html=True)
            
            # 答案依然放在展开栏里，保持页面清爽
            with st.expander("点击查看详细解答"):
                st.write(a)
                st.button(f"对该回答满意 👍", key=f"btn_{idx}")

# --- 底部美化 ---
st.markdown("---")
footer_col1, footer_col2 = st.columns([3, 1])
with footer_col1:
    st.caption("© 2025 某某学院招生办公室 | 智能问答系统 v3.0")
with footer_col2:
    if st.button("🔄 重置搜索"):
        st.rerun()
