
import streamlit as st

from modules import conversations as conv_mgr


AVAILABLE_MODELS = ["llama3.2", "qwen:0.5b"]

MODE_CHAT = " Conversation"
MODE_COMPARE = " Comparaison"


def render_mode_selector() -> str:
    """Navigation entre les modes conversation et comparaison."""
    return st.sidebar.radio("Mode", [MODE_CHAT, MODE_COMPARE], key="app_mode")


def _sync_model_selector() -> None:
    """Remet le sélecteur de modèle sur le dernier modèle utilisé par la conversation active."""
    model = conv_mgr.get_current_conversation().get("model")
    if model in AVAILABLE_MODELS:
        st.session_state.selected_model = model


def _select(conv_id: str) -> None:
    conv_mgr.select_conversation(conv_id)
    _sync_model_selector()


def _delete(conv_id: str) -> None:
    conv_mgr.delete_conversation(conv_id)
    _sync_model_selector()


def render_conversation_sidebar(default_model: str | None = None) -> None:
    """Bouton « Nouvelle conversation » + liste sélectionnable / supprimable."""
    st.sidebar.header("Conversations")
    st.sidebar.button(
        "+ Nouvelle conversation",
        use_container_width=True,
        on_click=conv_mgr.create_conversation,
        args=(default_model,),
    )

    current_id = st.session_state.current_conversation_id
    for conv in conv_mgr.list_conversations():
        col_title, col_del = st.sidebar.columns([5, 1])
        is_current = conv["id"] == current_id
        col_title.button(
            conv["title"],
            key=f"select_{conv['id']}",
            use_container_width=True,
            type="primary" if is_current else "secondary",
            help=f"Modèle(s) : {', '.join(conv_mgr.models_used(conv)) or 'aucun message'}",
            on_click=_select,
            args=(conv["id"],),
        )
        col_del.button(
            "🗑️",
            key=f"delete_{conv['id']}",
            help="Supprimer cette conversation",
            on_click=_delete,
            args=(conv["id"],),
        )


def render_export_buttons() -> None:
    """Export de l'historique en TXT ou JSON (conversation active / toutes)."""
    st.sidebar.header("Exporter")
    conv = conv_mgr.get_current_conversation()
    disabled = len(conv["messages"]) == 0
    c1, c2 = st.sidebar.columns(2)
    c1.download_button(
        "⬇TXT",
        data=conv_mgr.conversation_to_txt(conv),
        file_name=f"conversation_{conv['id']}.txt",
        mime="text/plain",
        disabled=disabled,
        use_container_width=True,
    )
    c2.download_button(
        "⬇ JSON",
        data=conv_mgr.conversation_to_json(conv),
        file_name=f"conversation_{conv['id']}.json",
        mime="application/json",
        disabled=disabled,
        use_container_width=True,
    )
    st.sidebar.download_button(
        "⬇ Toutes les conversations (JSON)",
        data=conv_mgr.all_conversations_to_json(),
        file_name="toutes_les_conversations.json",
        mime="application/json",
        use_container_width=True,
    )


def render_history(messages: list[dict]) -> None:
    for m in messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("model"):
                st.caption(f" {m['model']}")


def stream_with_indicator(placeholder, chunks, model_name: str = "") -> str:
    """
    Indicateur visuel pendant la génération :
      - «  Génération en cours… » tant que le 1er token n'est pas arrivé,
      - curseur ▌ pendant le streaming.
    `chunks` est un itérable de morceaux de texte. Retourne le texte complet.
    """
    placeholder.markdown(f" *{model_name or 'Le modèle'} génère la réponse…*")
    full = ""
    for piece in chunks:
        full += piece
        placeholder.markdown(full + "▌")
    placeholder.markdown(full)
    return full
