import streamlit as st
import requests
import json
import time
from typing import List, Dict
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="HackRX - LLM Document Processor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processing_history' not in st.session_state:
    st.session_state.processing_history = []
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000"

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 HackRX LLM Document Processor</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # API Configuration
        st.markdown("### 🔗 API Settings")
        api_url = st.text_input(
            "API Base URL", 
            value=st.session_state.api_base_url,
            help="URL of your FastAPI backend"
        )
        st.session_state.api_base_url = api_url
        
        # Test API connection
        if st.button("🔍 Test API Connection"):
            test_api_connection(api_url)
        
        st.markdown("---")
        
        # Sample queries
        st.markdown("### 📝 Sample Questions")
        sample_questions = [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?",
            "What is the waiting period for cataract surgery?",
            "Are medical expenses for organ donors covered?",
            "What is the No Claim Discount offered?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a Hospital?",
            "What is the coverage for AYUSH treatments?",
            "Are there sub-limits on room rent for Plan A?"
        ]
        
        selected_samples = st.multiselect(
            "Select sample questions:",
            sample_questions,
            help="Choose from pre-defined questions or write your own"
        )
        
        if st.button("📋 Use Selected Samples"):
            st.session_state.selected_questions = selected_samples
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📄 Document Processing</h2>', unsafe_allow_html=True)
        
        # Document URL input
        st.markdown("### 🔗 Document URL")
        doc_url = st.text_input(
            "Enter PDF Document URL:",
            value="https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
            help="Paste the URL of the PDF document to analyze"
        )
        
        # Questions input
        st.markdown("### ❓ Questions")
        
        # Check if we have selected questions from sidebar
        initial_questions = ""
        if 'selected_questions' in st.session_state and st.session_state.selected_questions:
            initial_questions = "\n".join(st.session_state.selected_questions)
        
        questions_text = st.text_area(
            "Enter questions (one per line):",
            value=initial_questions,
            height=200,
            help="Enter each question on a new line"
        )
        
        # Process button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn2:
            process_btn = st.button("🚀 Process Document", type="primary", use_container_width=True)
    
    with col2:
        st.markdown('<h2 class="sub-header">📊 System Status</h2>', unsafe_allow_html=True)
        
        # System metrics placeholder
        metrics_placeholder = st.empty()
        update_metrics(metrics_placeholder)
        
        # Processing history
        st.markdown("### 📋 Recent Processes")
        if st.session_state.processing_history:
            history_df = pd.DataFrame(st.session_state.processing_history)
            st.dataframe(history_df.tail(5), use_container_width=True)
        else:
            st.info("No processing history yet")
    
    # Processing logic
    if process_btn:
        if not doc_url.strip():
            st.error("Please enter a document URL")
            return
        
        if not questions_text.strip():
            st.error("Please enter at least one question")
            return
        
        # Parse questions
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        if not questions:
            st.error("Please enter valid questions")
            return
        
        # Process the request
        process_document_questions(api_url, doc_url, questions)
    
    # Results display area
    st.markdown("---")
    display_results()

def test_api_connection(api_url: str):
    """Test connection to the API"""
    try:
        with st.spinner("Testing API connection..."):
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API connection successful!")
            else:
                st.error(f"❌ API returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure your FastAPI server is running.")
    except Exception as e:
        st.error(f"❌ Error testing API: {str(e)}")

def update_metrics(placeholder):
    """Update system metrics display"""
    with placeholder.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>⚡</h3>
                <p><strong>Speed</strong></p>
                <p>< 10 sec</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>🎯</h3>
                <p><strong>Accuracy</strong></p>
                <p>90%+</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📊</h3>
                <p><strong>Processed</strong></p>
                <p>{}</p>
            </div>
            """.format(len(st.session_state.processing_history)), unsafe_allow_html=True)

def process_document_questions(api_url: str, doc_url: str, questions: List[str]):
    """Process document with questions"""
    
    # Create request payload
    payload = {
        "documents": doc_url,
        "questions": questions
    }
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Update progress
        status_text.text("📥 Sending request to API...")
        progress_bar.progress(20)
        
        # Make API request
        start_time = time.time()
        response = requests.post(
            f"{api_url}/hackrx/run",
            json=payload,
            timeout=60
        )
        
        progress_bar.progress(60)
        status_text.text("🤖 Processing with AI...")
        
        if response.status_code == 200:
            progress_bar.progress(100)
            status_text.text("✅ Processing complete!")
            
            # Parse response
            result = response.json()
            answers = result.get('answers', [])
            
            processing_time = time.time() - start_time
            
            # Store in session state for display
            st.session_state.latest_result = {
                'questions': questions,
                'answers': answers,
                'processing_time': processing_time,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to history
            st.session_state.processing_history.append({
                'Timestamp': time.strftime("%H:%M:%S"),
                'Questions': len(questions),
                'Time (s)': f"{processing_time:.2f}",
                'Status': '✅ Success'
            })
            
            st.success(f"✅ Successfully processed {len(questions)} questions in {processing_time:.2f} seconds!")
            
        else:
            st.error(f"❌ API Error: {response.status_code} - {response.text}")
            st.session_state.processing_history.append({
                'Timestamp': time.strftime("%H:%M:%S"),
                'Questions': len(questions),
                'Time (s)': 'N/A',
                'Status': f'❌ Error {response.status_code}'
            })
    
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The document might be too large or the server is overloaded.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure your FastAPI server is running.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.session_state.processing_history.append({
            'Timestamp': time.strftime("%H:%M:%S"),
            'Questions': len(questions),
            'Time (s)': 'N/A',
            'Status': '❌ Error'
        })
    
    finally:
        progress_bar.empty()
        status_text.empty()

def display_results():
    """Display processing results"""
    if 'latest_result' in st.session_state:
        result = st.session_state.latest_result
        
        st.markdown('<h2 class="sub-header">🎯 Results</h2>', unsafe_allow_html=True)
        
        # Results summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Questions Processed", len(result['questions']))
        with col2:
            st.metric("Processing Time", f"{result['processing_time']:.2f}s")
        with col3:
            st.metric("Avg Time per Question", f"{result['processing_time']/len(result['questions']):.2f}s")
        
        # Display Q&A pairs
        st.markdown("### 💬 Questions & Answers")
        
        for i, (question, answer) in enumerate(zip(result['questions'], result['answers'])):
            with st.expander(f"❓ Question {i+1}: {question}", expanded=True):
                st.markdown(f"""
                <div class="info-box">
                    <strong>Answer:</strong><br>
                    {answer}
                </div>
                """, unsafe_allow_html=True)
        
        # Export options
        st.markdown("### 📤 Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            json_data = {
                'timestamp': result['timestamp'],
                'processing_time': result['processing_time'],
                'qa_pairs': [
                    {'question': q, 'answer': a} 
                    for q, a in zip(result['questions'], result['answers'])
                ]
            }
            
            st.download_button(
                label="📄 Download as JSON",
                data=json.dumps(json_data, indent=2),
                file_name=f"hackrx_results_{int(time.time())}.json",
                mime="application/json"
            )
        
        with col2:
            # CSV export
            csv_data = pd.DataFrame({
                'Question': result['questions'],
                'Answer': result['answers']
            })
            
            st.download_button(
                label="📊 Download as CSV",
                data=csv_data.to_csv(index=False),
                file_name=f"hackrx_results_{int(time.time())}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()