"""Composants d'interface Streamlit destinés à la personne 1."""
import streamlit as st
from modules.conversations import (
    create_conversation, delete_conversation, get_current_conversation,
    get_export_txt, get_export_json
)


def on_conversation_change():
    st.session_state.current_conversation_id = st.session_state.conversation_selector


def render_conversation_sidebar():
    st.sidebar.divider()
    st.sidebar.header("💬 Mes conversations")

    if st.sidebar.button("➕ Nouvelle conversation", use_container_width=True):
        create_conversation()
        # Le widget selectbox sera mis à jour au prochain rerun.
        st.session_state.conversation_selector = st.session_state.current_conversation_id
        st.rerun()

    conversation_ids = list(st.session_state.conversations.keys())
    if st.session_state.get("conversation_selector") not in conversation_ids:
        st.session_state.conversation_selector = st.session_state.current_conversation_id

    selected_id = st.sidebar.selectbox(
        "Historique des conversations",
        conversation_ids,
        format_func=lambda cid: st.session_state.conversations[cid]["title"],
        key="conversation_selector",
        on_change=on_conversation_change,
    )

    if st.sidebar.button("🗑️ Supprimer la conversation", use_container_width=True):
        delete_conversation(selected_id)
        st.session_state.conversation_selector = st.session_state.current_conversation_id
        st.rerun()

    conversation = get_current_conversation()
    st.sidebar.divider()
    st.sidebar.subheader("📥 Exporter la conversation")
    st.sidebar.download_button(
        "📄 Télécharger TXT",
        data=get_export_txt(conversation),
        file_name="conversation.txt",
        mime="text/plain; charset=utf-8",
        use_container_width=True,
    )
    st.sidebar.download_button(
        "📋 Télécharger JSON",
        data=get_export_json(conversation),
        file_name="conversation.json",
        mime="application/json",
        use_container_width=True,
    )


def render_conversation_history(conversation):
    st.subheader(f"💬 {conversation['title']}")
    for message in conversation["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
