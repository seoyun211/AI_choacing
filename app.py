import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/coaching"

st.set_page_config(page_title="AI 면접 코치", page_icon="💼")
st.title("AI 면접 코치")
st.caption("답변을 입력하면 AI가 평가하고 개선안을 제시합니다")

job = st.text_input("관심 직무", placeholder="예) 백엔드 개발자")
question = st.text_input("면접 질문", value="어떤 프로젝트를 해보셨나요?")
answer = st.text_area("내 답변", height=150,
                      placeholder="답변을 자유롭게 작성해 주세요")

if st.button("코칭 받기", type="primary"):
    if not job or not answer:
        st.warning("직무와 답변을 모두 입력해 주세요.")
    else:
        with st.spinner("AI가 답변을 분석하는 중입니다..."):
            try:
                res = requests.post(
                    API_URL,
                    json={"job": job, "question": question, "answer": answer},
                    timeout=120,
                )
            except requests.exceptions.RequestException as e:
                st.error(f"서버에 연결할 수 없습니다: {e}")
                st.stop()

        if res.status_code == 422:
            st.error("입력값이 형식에 맞지 않습니다.")
            st.json(res.json())
            st.stop()

        if res.status_code != 200:
            st.error(f"오류가 발생했습니다 (코드 {res.status_code})")
            st.stop()

        result = res.json()

        st.divider()
        st.metric("점수", f"{result['score']}점")
        st.progress(result["score"] / 100)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("잘한 점")
            for item in result["strengths"]:
                st.success(item)
        with col2:
            st.subheader("개선할 점")
            for item in result["improvements"]:
                st.warning(item)

        st.subheader("다듬은 답변")
        st.info(result["revised_answer"])
