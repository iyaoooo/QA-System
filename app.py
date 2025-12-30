import streamlit as st
import pandas as pd

# 设置网页标题和图标
st.set_page_config(page_title="招生问答系统", page_icon="🎓")


def char_match_similarity(user_input, standard_question):
    """核心算法逻辑保持不变"""
    if not user_input:
        return 0.0
    user_chars = set(user_input)
    standard_chars = set(str(standard_question))
    intersection = user_chars.intersection(standard_chars)
    union = user_chars.union(standard_chars)
    base_score = len(intersection) / len(union)
    if user_input in str(standard_question):
        base_score += 0.5
    return min(base_score, 1.0)


@st.cache_data  # 缓存数据，避免每次操作都重新读取Excel
def load_data(file_path):
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        return df[['标准问题', '答案']].dropna()
    except Exception as e:
        st.error(f"无法读取文件: {e}")
        return None


# --- 界面部分 ---
st.title("🎓 招生问答智能咨询系统")
st.markdown("---")

# 侧边栏配置
with st.sidebar:
    st.header("系统设置")
    file_path = "招生问答汇总20210615（加标准问题）.xlsx"
    st.info(f"当前数据库: {file_path}")
    top_n = st.slider("推荐问题数量", 1, 10, 5)

data = load_data(file_path)

if data is not None:
    # 搜索框
    user_input = st.text_input("💬 请输入您想咨询的问题（例如：体育、录取）：", "")

    if user_input:
        # 计算相似度
        qa_pairs = data.values.tolist()
        results = []
        for q, a in qa_pairs:
            sim = char_match_similarity(user_input.lower(), str(q).lower())
            if sim > 0:
                results.append((q, a, sim))

        # 排序
        results.sort(key=lambda x: x[2], reverse=True)
        matched_questions = results[:top_n]

        if not matched_questions:
            st.warning("❌ 未找到相关问题，请换个词试试。")
        else:
            # 1. 精准匹配检查
            exact_match = next((item for item in matched_questions if user_input == str(item[0]).strip()), None)

            if exact_match:
                st.success(f"🎯 找到精准匹配：{exact_match[0]}")
                st.info(f"💡 **回答：** {exact_match[1]}")
            else:
                st.subheader(f"🔍 为您找到以下 {len(matched_questions)} 个相似问题：")

                # 使用 Streamlit 的 Expander (折叠面板) 展示结果
                for idx, (q, a, sim) in enumerate(matched_questions, start=1):
                    with st.expander(f"{idx}. {q} (匹配度: {sim:.2f})"):
                        st.write(f"**回答：** {a}")
                        st.progress(sim)  # 可视化展示匹配分数

else:
    st.warning("请确保 Excel 文件与代码在同一目录下。")

# 页脚
st.markdown("---")
st.caption("© 2023 招生咨询系统 | Powered by Streamlit & Pandas")