import json 
from difflib import get_close_matches
import streamlit as st
import os

# Page Configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        data: dict = json.load(file)
    return data


def save_knowledge_base(file_path: str, data:dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    # Lowercase Conversion For Better Matching Results
    user_question = user_question.lower().strip()
    questions_lower = [q.lower().strip() for q in questions]
    
    # Higher The Cutoff, Higher The Accuracy
    matches = get_close_matches(user_question, questions_lower, n=1, cutoff=0.8)
    
    if matches:
        # To Find The Original Question or Matching Question
        for q in questions:
            if q.lower().strip() == matches[0]:
                return q
    return None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    question = question.lower().strip()
    for q in knowledge_base["questions"]:
        if q["question"].lower().strip() == question:
            return q["answer"]
# SideBar Start        
with st.sidebar:
    st.title("🤖 About the AskMate")
    st.markdown("### Developer")
    st.write("Created by: Rahim Ali")
    
    st.markdown("### Technologies Used")
    st.write("""
    - Python
    - Streamlit
    - JSON for data storage
    - Difflib for pattern matching
    """)
    
    st.markdown("### How to Use")
    st.write("""
    1. Type your question in the text input box
    2. The chatbot will try to find the best matching answer
    3. If no answer is found, you can teach the chatbot by providing an answer
    4. The chatbot will learn and store your new Q&A pair
    5. You can view the chat history below
    """)
# SideBar End        

# Main Content Start
st.title("🤖 AskMate")
st.markdown("---")

# Initialize session state for chat history and knowledge base
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = load_knowledge_base('knowledge_base.json')
if 'teaching_mode' not in st.session_state:
    st.session_state.teaching_mode = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'last_prompt' not in st.session_state:
    st.session_state.last_prompt = None

# This Condition Displays Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat Box
prompt = st.chat_input("Teach Me...")
if prompt and prompt != st.session_state.last_prompt:
    st.session_state.last_prompt = prompt
    
    # This Line Adds User Message To Temporary Chat History
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Bot Response on Saved Question
    best_match = find_best_match(prompt, [q["question"] for q in st.session_state.knowledge_base["questions"]])
    
    if best_match:
        answer = get_answer_for_question(best_match, st.session_state.knowledge_base)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        answer = "I don't know the answer. Would you like to teach me?"
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.teaching_mode = True
        st.session_state.current_question = prompt
    
    st.rerun()

# This Condition Manages The Bot Teaching Function
if st.session_state.teaching_mode:
    new_answer = st.text_input("Type the answer or press Enter to skip:", key="new_answer")
    if new_answer:
        # This Condition Checks If The Question Exists
        question_exists = any(q["question"].lower().strip() == st.session_state.current_question.lower().strip() 
                            for q in st.session_state.knowledge_base["questions"])
        
        if not question_exists:
            st.session_state.knowledge_base["questions"].append({
                "question": st.session_state.current_question,
                "answer": new_answer
            })
            save_knowledge_base('knowledge_base.json', st.session_state.knowledge_base)
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Thank you! I've learned that '{st.session_state.current_question}' should be answered with '{new_answer}'"
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I already know this question. Please ask me something else!"
            })
        
        st.session_state.teaching_mode = False
        st.session_state.current_question = None
        st.rerun()

# Chat History Clear
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.knowledge_base = load_knowledge_base('knowledge_base.json')
    st.session_state.teaching_mode = False
    st.session_state.current_question = None
    st.session_state.last_prompt = None
    st.rerun()

# Main Content End
