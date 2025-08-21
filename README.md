# HR Resource Query Chatbot

An intelligent HR assistant chatbot that helps HR teams find employees by answering queries using natural language processing and retrieval-augmented generation (RAG) techniques.

## 🎯 Overview

This project implements a complete RAG-powered chatbot system that can answer queries like:
- "Find Python developers with 3+ years experience"
- "Who has worked on healthcare projects?"
- "Suggest people for a React Native project"
- "Find developers who know both AWS and Docker"

The system combines semantic search using embeddings with natural language generation to provide intelligent, contextual responses about employee capabilities and availability.

## ✨ Features

### Core Features
- **Natural Language Queries**: Ask questions in plain English
- **Semantic Search**: Uses sentence transformers and FAISS for intelligent matching
- **RAG Implementation**: Combines retrieval and generation for contextual responses
- **Real-time Chat Interface**: Interactive Streamlit-based UI
- **Advanced Filtering**: Search by skills, experience, department, and availability
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### AI/ML Features
- **Sentence Transformers**: Uses `all-MiniLM-L6-v2` for embeddings
- **FAISS Vector Search**: Efficient similarity search with cosine similarity
- **OpenAI Integration**: Enhanced responses with GPT-3.5-turbo (optional)
- **Template Fallback**: Works without OpenAI API using smart templates
- **Similarity Scoring**: Relevance scoring for search results

### User Experience
- **Chat Interface**: ChatGPT-like conversation experience
- **Example Queries**: Quick-start buttons with common queries
- **Search Results**: Detailed candidate information with match scores
- **Statistics Dashboard**: Real-time database insights
- **Responsive Design**: Works on desktop and mobile

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐
│                 │                 │                 │
│   Streamlit     │◄───────────────►│   FastAPI       │
│   Frontend      │                 │   Backend       │
│                 │                 │                 │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │                 │
                                    │   RAG System    │
                                    │                 │
                                    └─────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
            ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
            │              │        │              │        │              │
            │ Embeddings   │        │ FAISS Index  │        │ Employee     │
            │ (Sentence    │        │ (Vector DB)  │        │ Data (JSON)  │
            │ Transformers)│        │              │        │              │
            └──────────────┘        └──────────────┘        └──────────────┘
```

### RAG Pipeline

1. **Retrieval**: User query → Embedding → FAISS search → Relevant employees
2. **Augmentation**: Combine query context with employee data
3. **Generation**: Create natural language response using LLM or templates

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (for embeddings)
- Optional: OpenAI API key for enhanced responses

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hr-resource-chatbot.git
   cd hr-resource-chatbot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (Optional)
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key if you have one
   ```

5. **Start the FastAPI backend**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

7. **Access the application**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs
   - API: http://localhost:8000

### Alternative Installation

```bash
# Install as a package
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

## 📚 API Documentation

### Main Endpoints

#### POST /chat
Chat with the HR assistant using natural language.

**Request:**
```json
{
  "message": "Find Python developers with 3+ years experience",
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "response": "Based on your query, I found 3 excellent candidates...",
  "candidates": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "skills": ["Python", "React", "AWS"],
      "experience_years": 5,
      "projects": ["E-commerce Platform", "Healthcare Dashboard"],
      "availability": "available",
      "similarity_score": 0.85
    }
  ],
  "session_id": "session_123"
}
```

#### GET /employees/search
Search employees with specific filters.

**Parameters:**
- `skills`: Comma-separated skills (e.g., "Python,React")
- `experience_min`: Minimum years of experience
- `experience_max`: Maximum years of experience
- `department`: Department name
- `availability`: "available" or "busy"

#### GET /employees/{employee_id}
Get detailed information about a specific employee.

#### GET /stats
Get database statistics including department distribution and top skills.

### Example API Calls

```python
import requests

# Chat query
response = requests.post("http://localhost:8000/chat", json={
    "message": "Find machine learning engineers for healthcare"
})

# Filtered search
response = requests.get("http://localhost:8000/employees/search", params={
    "skills": "Python,TensorFlow",
    "experience_min": 3,
    "availability": "available"
})
```

## 🤖 AI Development Process

### AI Tools and Assistance Used

This project was developed with extensive use of modern AI development tools:

#### AI Coding Assistants Used:
- **Primary Tool**: Claude AI for architecture planning and code generation
- **Secondary Tools**: GitHub Copilot for code completion and debugging
- **ChatGPT**: Used for API documentation and README generation

#### AI Assistance Breakdown by Development Phase:

1. **Architecture & Planning (40% AI-assisted)**
   - AI helped design the RAG pipeline architecture
   - Suggested optimal tech stack (FastAPI + Streamlit + FAISS)
   - Provided best practices for embedding-based search

2. **Backend Development (60% AI-assisted)**
   - Generated boilerplate FastAPI code structure
   - AI provided FAISS integration patterns
   - Helped implement proper error handling and logging
   - Generated Pydantic models and API schemas

3. **Frontend Development (50% AI-assisted)**
   - Streamlit chat interface design patterns
   - CSS styling and layout suggestions
   - Session state management implementation

4. **Data Processing (70% AI-assisted)**
   - Employee dataset generation and structure
   - Embedding pipeline implementation
   - Text preprocessing for semantic search

5. **Testing & Debugging (30% AI-assisted)**
   - AI helped identify edge cases
   - Provided testing strategies and example queries
   - Debugging assistance for API integration issues

#### Code Generation Statistics:
- **Estimated AI-generated code**: ~65%
- **Hand-written/modified code**: ~35%
- **AI-suggested optimizations**: 15+ performance improvements
- **Manual debugging and customization**: Significant customization of AI suggestions

#### Notable AI-Generated Solutions:
1. **RAG Pipeline Architecture**: AI suggested the optimal separation of retrieval, augmentation, and generation components
2. **FAISS Integration**: Complete implementation pattern for semantic search
3. **Error Handling**: Comprehensive exception handling across the API
4. **Template Response System**: Fallback system when OpenAI API is unavailable

#### Challenges Where AI Couldn't Help:
1. **Domain-Specific Requirements**: Understanding HR-specific needs required manual research
2. **Performance Optimization**: Fine-tuning FAISS parameters required manual testing
3. **UI/UX Design Decisions**: User experience choices required human judgment
4. **Business Logic**: Complex filtering and ranking logic needed manual implementation

### Technical Decision Justifications

#### Embedding Model Choice: `all-MiniLM-L6-v2`
- **Pros**: Fast inference, good general-purpose performance, lightweight
- **Cons**: Less specialized than domain-specific models
- **AI Recommendation**: Claude suggested this model for balanced performance

#### Vector Database: FAISS vs. Alternatives
- **FAISS Chosen**: Free, fast, runs locally
- **Alternatives Considered**: Pinecone (cloud), Chroma (local)
- **Decision Factor**: Local deployment and cost considerations

#### LLM Strategy: OpenAI + Template Fallback
- **Primary**: OpenAI GPT-3.5-turbo for best responses
- **Fallback**: Template-based responses for reliability
- **Reasoning**: Ensures system works without API dependencies

## 📊 Sample Data Structure

The employee dataset includes 20+ employees with the following structure:

```json
{
  "employees": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "skills": ["Python", "React", "AWS", "Docker", "PostgreSQL"],
      "experience_years": 5,
      "projects": ["E-commerce Platform", "Healthcare Dashboard"],
      "availability": "available",
      "department": "Engineering",
      "specialization": "Full-stack Development",
      "certifications": ["AWS Solutions Architect", "React Developer"]
    }
  ]
}
```

## 🧪 Testing the Application

### Sample Queries to Try:

1. **Skill-based searches:**
   - "Find Python developers"
   - "Who knows React and Node.js?"
   - "Show me DevOps engineers"

2. **Experience-based searches:**
   - "Find senior developers with 5+ years experience"
   - "Who are the junior developers?"

3. **Project-based searches:**
   - "Who has worked on healthcare projects?"
   - "Find people with e-commerce experience"

4. **Complex queries:**
   - "I need a machine learning engineer for a healthcare AI project"
   - "Find someone who can work on both frontend and DevOps"

### API Testing:

```bash
# Test the API directly
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Find Python developers with machine learning experience"}'

# Test employee search
curl "http://localhost:8000/employees/search?skills=Python&experience_min=3"
```

## 🔮 Future Improvements

### Technical Enhancements
- **Advanced RAG**: Implement query expansion and result reranking
- **Multi-modal Search**: Add support for searching by project images/documents
- **Real-time Updates**: WebSocket integration for live chat updates
- **Caching Layer**: Redis for improved response times
- **A/B Testing**: Compare different embedding models and LLMs

### Feature Additions
- **Employee Profiles**: Detailed profile pages with recommendations
- **Team Building**: Suggest optimal team compositions
- **Skill Gap Analysis**: Identify missing skills in the organization
- **Integration**: Connect with HR systems (ATS, HRIS)
- **Mobile App**: React Native mobile application

### Deployment Options
- **Docker Containerization**: Multi-stage builds for production
- **Cloud Deployment**: AWS/GCP deployment with auto-scaling
- **Database Integration**: PostgreSQL with vector extensions
- **Monitoring**: Prometheus + Grafana for system monitoring

## 🐳 Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 8501

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have questions or need help:

1. Check the [API documentation](http://localhost:8000/docs) when running
2. Create an issue on GitHub
3. Contact: your.email@example.com

## 🏆 Acknowledgments

- **OpenAI** for the GPT models and embeddings API
- **Hugging Face** for the sentence-transformers library
- **Facebook AI Research** for FAISS
- **FastAPI** and **Streamlit** teams for excellent frameworks
- **AI Development Tools** that accelerated development

---

**Built with ❤️ using FastAPI, Streamlit, and RAG technology**