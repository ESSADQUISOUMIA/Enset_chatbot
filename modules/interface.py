"""Navigation, historique et export des conversations (Personne 1)."""
import streamlit as st
from modules.conversations import (
    create_conversation, delete_conversation, get_current_conversation,
    get_export_txt, get_export_json,
)


def on_conversation_change():
    st.session_state.current_conversation_id = st.session_state.conversation_selector


def render_conversation_sidebar():
    st.sidebar.markdown('<div class="enset-brand">ENSET <span>Chatbot</span></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="enset-meta">Assistant IA local · Ollama</div>', unsafe_allow_html=True)

    mode = st.sidebar.radio(
        "Espace de travail", ["Conversation", "Comparaison"],
        key="navigation_mode", horizontal=True,
    )
    st.sidebar.divider()
    st.sidebar.markdown("### Conversations")

    if st.sidebar.button("Nouvelle conversation", use_container_width=True, type="primary"):
        create_conversation()
        st.session_state.conversation_selector = st.session_state.current_conversation_id
        st.session_state.navigation_mode = "Conversation"
        st.rerun()

    ids = list(st.session_state.conversations)
    if st.session_state.get("conversation_selector") not in ids:
        st.session_state.conversation_selector = st.session_state.current_conversation_id

    selected_id = st.sidebar.selectbox(
        "Historique", ids,
        format_func=lambda cid: st.session_state.conversations[cid]["title"],
        key="conversation_selector", on_change=on_conversation_change,
    )

    if st.sidebar.button("Supprimer cette conversation", use_container_width=True):
        delete_conversation(selected_id)
        st.session_state.conversation_selector = st.session_state.current_conversation_id
        st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown("### Export")
    conversation = get_current_conversation()
    cols = st.sidebar.columns(2)
    with cols[0]:
        st.download_button("TXT", data=get_export_txt(conversation), file_name="conversation.txt",
                           mime="text/plain; charset=utf-8", use_container_width=True)
    with cols[1]:
        st.download_button("JSON", data=get_export_json(conversation), file_name="conversation.json",
                           mime="application/json", use_container_width=True)
    return mode


def render_conversation_history(conversation):
    st.markdown('<div class="enset-kicker">Espace conversation</div>', unsafe_allow_html=True)
    st.markdown('<div class="enset-heading">Votre assistant, vos idées.</div>', unsafe_allow_html=True)
    st.markdown('<div class="enset-subtitle">Posez une question et échangez avec un modèle exécuté localement.</div>', unsafe_allow_html=True)
    if not conversation["messages"]:
        st.markdown('''<div class="enset-empty">
          <div class="enset-empty-title">Une nouvelle conversation commence ici.</div>
          <div class="enset-empty-desc">Demandez une explication, rédigez un texte ou explorez une idée. Votre historique reste accessible dans le menu latéral.</div>
        </div>''', unsafe_allow_html=True)
    else:
        for message in conversation["messages"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
