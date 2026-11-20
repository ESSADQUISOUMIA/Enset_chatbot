
import streamlit as st

from modules.conversations import (
    create_conversation, delete_conversation, select_conversation,
    get_current_conversation, list_conversations, models_used,
    get_export_txt, get_export_json, get_export_all_json,
)
from modules.styles import render_brand


AVAILABLE_MODELS = ["llama3.2", "qwen:0.5b"]

MODE_CHAT = "Conversation"
MODE_COMPARE = "Comparaison"


# ------------------------------------------------------------- callbacks
# Les callbacks s'exécutent AVANT le rechargement du script : on peut donc y
# modifier la valeur d'un widget (radio, selectbox) sans erreur Streamlit.
def _sync_model_selector():
    """Remet le sélecteur de modèle sur le dernier modèle utilisé par la conversation active."""
    model = get_current_conversation().get("model")
    if model in AVAILABLE_MODELS:
        st.session_state.selected_model = model


def _on_new():
    create_conversation(st.session_state.get("selected_model"))
    st.session_state.navigation_mode = MODE_CHAT


def _on_select(cid):
    select_conversation(cid)
    st.session_state.navigation_mode = MODE_CHAT
    _sync_model_selector()


def _on_delete(cid):
    delete_conversation(cid)
    _sync_model_selector()


# --------------------------------------------------------------- sidebar
def render_conversation_sidebar():
    """Logo, navigation, liste des conversations et exports. Retourne le mode choisi."""
    render_brand()
    st.sidebar.markdown("### Espace de travail")
    mode = st.sidebar.radio(
        "Espace de travail", [MODE_CHAT, MODE_COMPARE],
        key="navigation_mode", horizontal=True,
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    st.sidebar.markdown("### Conversations")
    st.sidebar.button("Nouvelle conversation", use_container_width=True,
                      type="primary", on_click=_on_new)

    current_id = st.session_state.current_conversation_id
    for conv in list_conversations():
        col_title, col_del = st.sidebar.columns([6, 1])
        col_title.button(
            conv["title"], key=f"select_{conv['id']}", use_container_width=True,
            type="primary" if conv["id"] == current_id else "secondary",
            help=f"Modèle(s) : {', '.join(models_used(conv)) or 'aucun message'}",
            on_click=_on_select, args=(conv["id"],),
        )
        col_del.button("×", key=f"delete_{conv['id']}", help="Supprimer cette conversation",
                       on_click=_on_delete, args=(conv["id"],))

    st.sidebar.divider()
    st.sidebar.markdown("### Export")
    conv = get_current_conversation()
    empty = len(conv["messages"]) == 0
    c1, c2 = st.sidebar.columns(2)
    c1.download_button("TXT", data=get_export_txt(conv), file_name=f"conversation_{conv['id']}.txt",
                       mime="text/plain; charset=utf-8", disabled=empty, use_container_width=True)
    c2.download_button("JSON", data=get_export_json(conv), file_name=f"conversation_{conv['id']}.json",
                       mime="application/json", disabled=empty, use_container_width=True)
    st.sidebar.download_button("Toutes les conversations (JSON)", data=get_export_all_json(),
                               file_name="toutes_les_conversations.json",
                               mime="application/json", use_container_width=True)
    return mode


# ------------------------------------------------------------ page chat
def render_conversation_history(conversation):
    st.markdown('<div class="enset-kicker">Espace conversation</div>', unsafe_allow_html=True)
    st.markdown('<div class="enset-heading">Votre assistant, vos idées.</div>', unsafe_allow_html=True)
  
    if not conversation["messages"]:
        hero_slot = st.empty()  # emplacement effaçable dès que l'utilisateur envoie son 1er message
        hero_slot.markdown('''<div class="enset-empty">
          <div class="enset-empty-title">Que souhaitez-vous découvrir aujourd'hui ?</div>
        </div>''', unsafe_allow_html=True)
        return hero_slot
    for message in conversation["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("model"):
                st.caption(f"Modèle : {message['model']}")
    return None


def stream_with_indicator(placeholder, chunks, model_name=""):
    """Indicateur visuel pendant la génération.

    - avant le 1er token : « <modèle> génère la réponse… »
    - pendant le streaming : texte + curseur
    Retourne le texte complet.
    """
    placeholder.markdown(f"*{model_name or 'Le modèle'} génère la réponse…*")
    full = ""
    for piece in chunks:
        full += piece or ""
        placeholder.markdown(full + "▍")
    placeholder.markdown(full or "*Aucune réponse générée.*")
    return full
