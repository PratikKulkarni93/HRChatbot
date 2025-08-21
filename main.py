
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import openai
import os
from dotenv import load_dotenv
import re
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="HR Resource Query Chatbot API",
    description="An intelligent HR assistant chatbot using RAG system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models and data
class HRChatbot:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.employees_data = self.load_employee_data()
        self.employee_embeddings = None
        self.faiss_index = None
        self.openai_client = None
        self.setup_openai()
        self.setup_embeddings()

    def load_employee_data(self):
        """Load employee data from JSON file"""
        try:
            with open('employees_data.json', 'r') as f:
                data = json.load(f)
            return data['employees']
        except FileNotFoundError:
            logger.error("Employee data file not found")
            return []

    def setup_openai(self):
        """Setup OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.openai_client = openai
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not found. RAG responses will be template-based.")

    def create_employee_text(self, employee):
        """Create searchable text representation of employee"""
        skills_text = ", ".join(employee['skills'])
        projects_text = ", ".join(employee['projects'])
        certs_text = ", ".join(employee['certifications'])

        text = f"""
        Name: {employee['name']}
        Skills: {skills_text}
        Experience: {employee['experience_years']} years
        Projects: {projects_text}
        Department: {employee['department']}
        Specialization: {employee['specialization']}
        Certifications: {certs_text}
        Availability: {employee['availability']}
        """
        return text.strip()

    def setup_embeddings(self):
        """Create embeddings for all employees and setup FAISS index"""
        if not self.employees_data:
            logger.error("No employee data available for embedding")
            return

        # Create text representations
        employee_texts = [self.create_employee_text(emp) for emp in self.employees_data]

        # Generate embeddings
        logger.info("Generating embeddings for employees...")
        embeddings = self.model.encode(employee_texts)
        self.employee_embeddings = embeddings

        # Setup FAISS index
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product similarity

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.faiss_index.add(embeddings.astype('float32'))

        logger.info(f"FAISS index created with {len(employee_texts)} employees")

    def search_employees(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant employees using semantic similarity"""
        if not self.faiss_index:
            return []

        # Generate query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Search in FAISS index
        scores, indices = self.faiss_index.search(query_embedding.astype('float32'), top_k)

        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.employees_data):
                employee = self.employees_data[idx].copy()
                employee['similarity_score'] = float(score)
                results.append(employee)

        # Filter by minimum similarity threshold
        results = [emp for emp in results if emp['similarity_score'] > 0.3]

        return results

    def generate_response(self, query: str, relevant_employees: List[Dict]) -> str:
        """Generate natural language response using retrieved employee data"""
        if not relevant_employees:
            return "I couldn't find any employees matching your criteria. Please try a different search query."

        if self.openai_client and os.getenv('OPENAI_API_KEY'):
            return self.generate_openai_response(query, relevant_employees)
        else:
            return self.generate_template_response(query, relevant_employees)

    def generate_openai_response(self, query: str, employees: List[Dict]) -> str:
        """Generate response using OpenAI GPT"""
        try:
            # Prepare context
            context = "Based on your query, here are the relevant employees:\n\n"
            for emp in employees:
                skills_text = ", ".join(emp['skills'])
                projects_text = ", ".join(emp['projects'])
                context += f"""
                **{emp['name']}** ({emp['experience_years']} years experience)
                - Skills: {skills_text}
                - Projects: {projects_text}
                - Department: {emp['department']}
                - Specialization: {emp['specialization']}
                - Availability: {emp['availability']}

                """

            prompt = f"""
            You are an HR assistant helping to find the right employees for projects. 
            A user asked: "{query}"

            {context}

            Please provide a helpful, natural response recommending the most suitable candidates 
            and explaining why they would be a good fit. Be conversational and highlight their 
            relevant experience and skills.
            """

            response = self.openai_client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful HR assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self.generate_template_response(query, employees)

    def generate_template_response(self, query: str, employees: List[Dict]) -> str:
        """Generate template-based response when OpenAI is not available"""
        if len(employees) == 1:
            emp = employees[0]
            skills_text = ", ".join(emp['skills'][:5])  # Show top 5 skills
            projects_text = ", ".join(emp['projects'])

            response = f"""Based on your query "{query}", I found an excellent candidate:

**{emp['name']}** would be perfect for this role. They have {emp['experience_years']} years of experience and their skills include {skills_text}. 

They have worked on projects like: {projects_text}

Department: {emp['department']}
Specialization: {emp['specialization']}
Current availability: {emp['availability']}

Would you like more details about their background or see other candidates?"""

        else:
            response = f"""Based on your query "{query}", I found {len(employees)} excellent candidates:\n\n"""

            for i, emp in enumerate(employees[:3], 1):  # Show top 3
                skills_text = ", ".join(emp['skills'][:3])
                response += f"""**{i}. {emp['name']}** ({emp['experience_years']} years experience)
- Key skills: {skills_text}
- Specialization: {emp['specialization']}
- Availability: {emp['availability']}

"""

            if len(employees) > 3:
                response += f"\nI found {len(employees) - 3} more candidates. Would you like to see them?"

        return response

# Initialize chatbot
chatbot = HRChatbot()

# Pydantic models
class ChatQuery(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    candidates: List[Dict[str, Any]]
    session_id: str

class EmployeeSearchQuery(BaseModel):
    skills: Optional[List[str]] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    department: Optional[str] = None
    availability: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "HR Resource Query Chatbot API is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(query: ChatQuery):
    """Main chat endpoint for natural language queries"""
    try:
        # Search for relevant employees
        relevant_employees = chatbot.search_employees(query.message, top_k=5)

        # Generate natural language response
        response_text = chatbot.generate_response(query.message, relevant_employees)

        session_id = query.session_id or "default_session"

        return ChatResponse(
            response=response_text,
            candidates=relevant_employees,
            session_id=session_id
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/search")
async def search_employees(
    skills: Optional[str] = None,
    experience_min: Optional[int] = None,
    experience_max: Optional[int] = None,
    department: Optional[str] = None,
    availability: Optional[str] = None
):
    """Search employees with specific criteria"""
    try:
        filtered_employees = chatbot.employees_data.copy()

        # Apply filters
        if skills:
            skill_list = [s.strip().lower() for s in skills.split(',')]
            filtered_employees = [
                emp for emp in filtered_employees
                if any(skill.lower() in [s.lower() for s in emp['skills']] for skill in skill_list)
            ]

        if experience_min:
            filtered_employees = [
                emp for emp in filtered_employees
                if emp['experience_years'] >= experience_min
            ]

        if experience_max:
            filtered_employees = [
                emp for emp in filtered_employees
                if emp['experience_years'] <= experience_max
            ]

        if department:
            filtered_employees = [
                emp for emp in filtered_employees
                if department.lower() in emp['department'].lower()
            ]

        if availability:
            filtered_employees = [
                emp for emp in filtered_employees
                if emp['availability'].lower() == availability.lower()
            ]

        return {"employees": filtered_employees, "count": len(filtered_employees)}

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/employees/{employee_id}")
async def get_employee(employee_id: int):
    """Get specific employee details"""
    try:
        employee = next((emp for emp in chatbot.employees_data if emp['id'] == employee_id), None)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    except Exception as e:
        logger.error(f"Get employee error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get database statistics"""
    try:
        employees = chatbot.employees_data
        departments = {}
        skills_count = {}

        for emp in employees:
            # Count departments
            dept = emp['department']
            departments[dept] = departments.get(dept, 0) + 1

            # Count skills
            for skill in emp['skills']:
                skills_count[skill] = skills_count.get(skill, 0) + 1

        return {
            "total_employees": len(employees),
            "departments": departments,
            "top_skills": dict(sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            "avg_experience": sum(emp['experience_years'] for emp in employees) / len(employees)
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

#End of main