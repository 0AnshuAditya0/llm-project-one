import streamlit as st
import requests

st.set_page_config(page_title="Document Query System", layout="centered")

st.title("📄 LLM-Powered Document Query System")

with st.form("query_form"):
    doc_url = st.text_input(
        "Document URL",
        value="https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D"
    )
    questions = st.text_area(
        "Questions (one per line)",
        height=140,
        value=(
            "What is the grace period for premium payment?\n"
            "What is the waiting period for pre-existing diseases?\n"
            "Does this policy cover maternity expenses?\n"
            "What is the waiting period for cataract surgery?\n"
            "Are medical expenses for organ donor covered?"
        )
    )
    submitted = st.form_submit_button("Get Answers")

if submitted:
    with st.spinner("Processing..."):
        try:
            resp = requests.post(
                "http://localhost:8000/api/v1/hackrx/run",
                json={
                    "documents": doc_url,
                    "questions": [q for q in questions.splitlines() if q.strip()]
                },
                headers={
                    "Authorization": "Bearer e0789bf301e9f74296fef9ceea624c447d8dd7ebbac17b500a40016ab487954b"
                },
                timeout=120
            )
            if resp.status_code == 200:
                result = resp.json()

                st.success("Results:")
                for i, (q, detail) in enumerate(
                    zip(
                        [q for q in questions.splitlines() if q.strip()],
                        result.get("details", [])
                    )
                ):
                    st.markdown(f"### Q{i+1}: {q}")
                    st.write(f"**Answer:** {detail.get('answer','')}")
                    st.progress(detail.get("confidence", 0.0))
                    st.caption(f"Confidence: {detail.get('confidence', 0.0):.2f}")

                    st.markdown("**Rationale:**")
                    st.write(detail.get("rationale", ""))

                    st.markdown("**Supporting Clauses:**")
                    for clause in detail.get("supporting_clauses", []):
                        st.markdown(
                            f"- *(Page {clause.get('page')})* "
                            f"[score={clause.get('score', 0):.3f}]: "
                            f"{clause.get('text')}"
                        )
                    st.divider()

            else:
                st.error(f"API Error: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown(
    """
    <style>
    .stTextInput>div>div>input, .stTextArea textarea {
        color: #000000;
        background-color: #f8f9fa;
        border-radius: 6px;
        border: 1px solid #dee2e6;
    }
    .stButton>button {
        background-color: #4f8cff;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 0.5em 1.5em;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)
