"""Gestion des conversations dans la session Streamlit."""
import json
from uuid import uuid4
import streamlit as st


def create_conversation():
    cid = str(uuid4())
    st.session_state.conversations[cid] = {"title": "Nouvelle conversation", "messages": []}
    st.session_state.current_conversation_id = cid
    return cid


def initialize_conversations():
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    if not st.session_state.conversations:
        create_conversation()
    elif st.session_state.current_conversation_id not in st.session_state.conversations:
        st.session_state.current_conversation_id = next(iter(st.session_state.conversations))


def delete_conversation(cid):
    st.session_state.conversations.pop(cid, None)
    if not st.session_state.conversations:
        create_conversation()
    elif cid == st.session_state.current_conversation_id:
        st.session_state.current_conversation_id = next(iter(st.session_state.conversations))


def get_current_conversation():
    return st.session_state.conversations[st.session_state.current_conversation_id]


def get_export_txt(conversation):
    lines = [f"Conversation : {conversation['title']}", "=" * 40, ""]
    for msg in conversation["messages"]:
        role = "Utilisateur" if msg["role"] == "user" else "Assistant"
        lines.extend([f"{role} :", msg["content"], ""])
    return "\n".join(lines)


def get_export_json(conversation):
    return json.dumps(conversation, ensure_ascii=False, indent=2)
