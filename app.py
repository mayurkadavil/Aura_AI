import streamlit as st
import pandas as pd
import numpy as np
import lightgbm as lgb
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import warnings
warnings.filterwarnings("ignore")

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Aura AI | Fitness Intelligence", layout="centered")
st.title("⚡️ Aura AI")
st.markdown("### Predictive Recovery & Dynamic Programming Engine")
st.divider()

# --- BRAIN 1: PREDICTIVE ENGINE (LightGBM) ---
@st.cache_resource
def train_forecaster():
    """Trains the predictive model silently in the background."""
    np.random.seed(42)
    data_size = 500
    hours_slept = np.random.normal(7, 1.5, data_size)
    rpe = np.random.uniform(4, 10, data_size)
    workout_duration = np.random.uniform(30, 120, data_size)
    calories_consumed = np.random.normal(2500, 300, data_size)
    
    readiness = (hours_slept * 10) - (rpe * 3) - (workout_duration * 0.1) + (calories_consumed * 0.005)
    readiness = np.clip(readiness, 0, 100)
    
    df = pd.DataFrame({
        'hours_slept': hours_slept, 'rpe': rpe,
        'workout_duration': workout_duration, 'calories_consumed': calories_consumed
    })
    
    model = lgb.LGBMRegressor(objective="regression", learning_rate=0.05, max_depth=5, n_estimators=100)
    model.fit(df, readiness)
    return model

# --- BRAIN 2: RAG AI COACH (Phi-3 + FAISS) 
import os

# Define the network bridge so Docker can talk to your Mac
OLLAMA_URL = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

# --- BRAIN 2: RAG AI COACH (Phi-3 + FAISS) ---
@st.cache_resource
def initialize_knowledge_base():
    """Builds the local vector database from sports science literature."""
    docs = [
        Document(page_content="Protocol for Severe Fatigue (Readiness < 30%): The c..."),
        Document(page_content="Protocol for Moderate Fatigue (Readiness 30% - 70%):..."),
        Document(page_content="Protocol for Peak Performance (Readiness > 70%): The...")
    ]
    # Pointing to your local phi3 model via the Docker network bridge!
    embeddings = OllamaEmbeddings(
        model="phi3", 
        base_url=OLLAMA_URL
    )
    return FAISS.from_documents(docs, embeddings)

# --- INITIALIZATION ---
model = train_forecaster()
vector_db = initialize_knowledge_base()

# --- INITIALIZATION ---
model = train_forecaster()
vector_db = initialize_knowledge_base()

# Pointing to your local phi3 model
llm = Ollama(model="phi3")

# --- USER INTERFACE ---
st.markdown("#### Step 1: Log Morning Metrics")
col1, col2 = st.columns(2)

with col1:
    sleep = st.slider("Hours Slept", 0.0, 12.0, 7.0, 0.5)
    rpe = st.slider("Yesterday's Exertion (RPE 1-10)", 1.0, 10.0, 5.0, 0.5)
with col2:
    duration = st.number_input("Yesterday's Workout Duration (mins)", min_value=0, max_value=180, value=60)
    calories = st.number_input("Calories Consumed", min_value=1000, max_value=5000, value=2500)

if st.button("Generate Daily Protocol", use_container_width=True):
    with st.spinner("Aura AI is analyzing your metrics..."):
        
        # 1. Predict Readiness
        user_data = pd.DataFrame([[sleep, rpe, duration, calories]], 
                                 columns=['hours_slept', 'rpe', 'workout_duration', 'calories_consumed'])
        readiness_score = model.predict(user_data)[0]
        
        st.divider()
        st.markdown("#### Step 2: System Analytics")
        
        # Display Readiness Metric dynamically
        if readiness_score > 70:
            st.metric(label="Predicted Muscle Readiness", value=f"{readiness_score:.1f}%", delta="Peak State")
        elif readiness_score > 30:
            st.metric(label="Predicted Muscle Readiness", value=f"{readiness_score:.1f}%", delta="Moderate State", delta_color="off")
        else:
            st.metric(label="Predicted Muscle Readiness", value=f"{readiness_score:.1f}%", delta="Critical Fatigue", delta_color="inverse")
            
        # 2. RAG Retrieval & LLM Generation
        st.markdown("#### Step 3: AI Coach Protocol")
        user_state = f"Aura AI Predicted Readiness Score: {readiness_score}%. User slept {sleep} hours and had an RPE of {rpe} yesterday."
        
        retrieved_docs = vector_db.similarity_search(user_state, k=1)
        context = retrieved_docs[0].page_content
        
        template = """
        You are Aura AI, an elite strength and conditioning coach.
        Based strictly on the Sports Science Literature provided below, generate a safe, actionable daily workout protocol for the user. Do not suggest anything that violates the literature. Keep it brief, encouraging, and use bullet points.
        
        Literature: {context}
        User State: {user_state}
        """
        prompt = PromptTemplate.from_template(template)
        formatted_prompt = prompt.format(context=context, user_state=user_state)
        
        # Generate the response
        response = llm.invoke(formatted_prompt)
        
        st.info(response)
 
