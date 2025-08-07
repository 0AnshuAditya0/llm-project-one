import streamlit as st
import requests

st.set_page_config(page_title="Document Query System", layout="centered")

st.title("📄 Document Query System")

with st.form("query_form"):
    doc_url = st.text_input("Document URL", 
        value="https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D")
    questions = st.text_area("Questions (one per line)", height=120, value=
        "What is the grace period for premium payment?\n"
        "What is the waiting period for pre-existing diseases?\n"
        "Does this policy cover maternity expenses?\n"
        "What is the waiting period for cataract surgery?\n"
        "Are medical expenses for organ donor covered?"
    )
    submitted = st.form_submit_button("Get Answers")

if submitted:
    with st.spinner("Processing..."):
        try:
            resp = requests.post(
                "http://localhost:8000/hackrx/run",
                json={"documents": doc_url, "questions": [q for q in questions.splitlines() if q.strip()]},
                timeout=120
            )
            if resp.status_code == 200:
                result = resp.json()
                st.success("Answers:")
                for i, (q, a) in enumerate(zip([q for q in questions.splitlines() if q.strip()], result["answers"])):
                    st.markdown(f"**Q{i+1}: {q}**\n\n> {a}")
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