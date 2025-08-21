
import streamlit as st
import requests
import json
import time
from typing import Dict, List, Any
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="HR Resource Query Chatbot",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
API_BASE_URL = "http://localhost:8000"

class HRChatbotUI:
    def __init__(self):
        self.api_url = API_BASE_URL

    def send_chat_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        """Send chat message to the API"""
        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json={"message": message, "session_id": session_id},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection Error: {str(e)}"}

    def search_employees(self, **filters) -> Dict[str, Any]:
        """Search employees with filters"""
        try:
            # Remove None values from filters
            clean_filters = {k: v for k, v in filters.items() if v is not None and v != ""}

            response = requests.get(
                f"{self.api_url}/employees/search",
                params=clean_filters,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection Error: {str(e)}"}

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API Error: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection Error: {str(e)}"}
        finally:
            print("finally block")

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}"
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = HRChatbotUI()

def render_chat():
    """Display the main chat interface"""
    st.title("👥 HR Resource Query Chatbot")
    st.markdown("Ask me to find employees with specific skills, experience, or project backgrounds!")

    # Display example queries
    with st.expander("💡 Example Queries", expanded=False):
        example_queries = [
            "Find Python developers with 3+ years experience",
            "Who has worked on healthcare projects?",
            "Suggest people for a React Native project",
            "Find developers who know both AWS and Docker",
            "I need someone experienced with machine learning for a healthcare project",
            "Who can help with DevOps and cloud architecture?",
            "Find frontend developers with React experience",
            "Show me cybersecurity experts"
        ]

        cols = st.columns(2)
        for i, query in enumerate(example_queries):
            with cols[i % 2]:
                if st.button(query, key=f"example_{i}", use_container_width=True):
                    st.session_state.example_query = query

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

                # Display candidates if available
                if message["role"] == "assistant" and "candidates" in message:
                    if message["candidates"]:
                        with st.expander(f"👥 Found {len(message['candidates'])} candidate(s)", expanded=True):
                            for candidate in message["candidates"]:
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.markdown(f"""
                                    **{candidate['name']}** - {candidate['department']}
                                    - 🎯 **Specialization:** {candidate['specialization']}
                                    - 💼 **Experience:** {candidate['experience_years']} years
                                    - 🛠️ **Skills:** {', '.join(candidate['skills'][:5])}{'...' if len(candidate['skills']) > 5 else ''}
                                    - 📋 **Projects:** {', '.join(candidate['projects'][:2])}{'...' if len(candidate['projects']) > 2 else ''}
                                    - ✅ **Availability:** {candidate['availability']}
                                    """)
                                with col2:
                                    similarity = candidate.get('similarity_score', 0)
                                    st.metric("Match Score", f"{similarity:.2f}")
                                st.divider()

    # Handle example query
    if "example_query" in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
        process_user_message(query)

def process_user_message(prompt: str):
    """Process user message and get bot response"""
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Searching for candidates..."):
            response = st.session_state.chatbot.send_chat_message(
                prompt, st.session_state.session_id
            )

        if "error" in response:
            error_msg = f"❌ {response['error']}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": error_msg
            })
        else:
            # Display response
            st.write(response["response"])

            # Add to chat history with candidates
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["response"],
                "candidates": response.get("candidates", [])
            })

def render_sidebar():
    """Display sidebar with additional features"""
    with st.sidebar:
        st.header("🔍 Advanced Search")

        # Manual employee search
        with st.expander("Employee Search", expanded=False):
            skills_input = st.text_input("Skills (comma-separated)", placeholder="Python, React, AWS")

            col1, col2 = st.columns(2)
            with col1:
                min_exp = st.number_input("Min Experience", min_value=0, max_value=20, value=0)
            with col2:
                max_exp = st.number_input("Max Experience", min_value=0, max_value=20, value=20)

            department = st.selectbox(
                "Department",
                ["", "Engineering", "AI Research", "Data Science", "Mobile Development", 
                 "DevOps", "Frontend Development", "Security", "Design", "Backend Development",
                 "Business Intelligence", "Blockchain", "Quality Assurance", "Product",
                 "Systems Programming", "Cloud Engineering"]
            )

            availability = st.selectbox("Availability", ["", "available", "busy"])

            if st.button("🔍 Search Employees", use_container_width=True):
                filters = {
                    "skills": skills_input if skills_input else None,
                    "experience_min": min_exp if min_exp > 0 else None,
                    "experience_max": max_exp if max_exp < 20 else None,
                    "department": department if department else None,
                    "availability": availability if availability else None
                }

                search_results = st.session_state.chatbot.search_employees(**filters)

                if "error" in search_results:
                    st.error(search_results["error"])
                else:
                    st.success(f"Found {search_results['count']} employees")
                    if search_results["employees"]:
                        df = pd.DataFrame(search_results["employees"])
                        st.dataframe(
                            df[["name", "department", "experience_years", "availability"]],
                            use_container_width=True
                        )

        # Statistics
        st.header("📊 Database Stats")
        if st.button("🔄 Refresh Stats", use_container_width=True):
            stats = st.session_state.chatbot.get_stats()

            if "error" not in stats:
                st.metric("Total Employees", stats["total_employees"])
                st.metric("Avg Experience", f"{stats['avg_experience']:.1f} years")

                # Department distribution
                st.subheader("Departments")
                dept_df = pd.DataFrame(
                    list(stats["departments"].items()),
                    columns=["Department", "Count"]
                )
                st.bar_chart(dept_df.set_index("Department"))

                # Top skills
                st.subheader("Top Skills")
                skills_df = pd.DataFrame(
                    list(list(stats["top_skills"].items())[:5]),
                    columns=["Skill", "Count"]
                )
                st.bar_chart(skills_df.set_index("Skill"))

        # Information
        st.header("ℹ️ Information")
        st.info("""
        This HR chatbot uses RAG (Retrieval-Augmented Generation) to help you find the right employees for your projects.

        **Features:**
        - Natural language queries
        - Semantic search using embeddings
        - Advanced filtering options
        - Real-time database statistics

        **Tips:**
        - Be specific about skills and requirements
        - Mention project types or domains
        - Ask about experience levels
        """)

        # API Status
        st.header("🔌 API Status")
        try:
            response = requests.get(f"{API_BASE_URL}/", timeout=5)
            if response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.error("❌ API Error")
        except:
            st.error("❌ API Disconnected")
            st.warning("Make sure the FastAPI server is running on http://localhost:8000")

def main():
    """Main application function"""
    initialize_session_state()

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        # display_chat_interface()  # or 
        render_chat()
    with col2:
        # display_sidebar()
        render_sidebar()

# Top-level chat input (must NOT be inside columns/expander/tabs/forms)
    prompt = st.chat_input("Ask about finding employees...")
    if prompt:
        process_user_message(prompt)

    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using FastAPI, Streamlit, and RAG technology | "
        "[View on GitHub](https://github.com/PratikKulkarni93/HRChatbot.git)"
    )

if __name__ == "__main__":
    main()
