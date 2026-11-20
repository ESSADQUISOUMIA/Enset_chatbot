import json
from datetime import datetime
from uuid import uuid4

import streamlit as st

DEFAULT_TITLE = "Nouvelle conversation"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------------ état
def create_conversation(model=None):
    """Crée une conversation vide et la rend active."""
    cid = uuid4().hex[:8]
    st.session_state.conversations[cid] = {
        "id": cid,
        "title": DEFAULT_TITLE,
        "created_at": _now(),
        "model": model,
        "messages": [],
    }
    st.session_state.current_conversation_id = cid
    return cid


def init_conversations():
    """À appeler au début de app.py : garantit qu'une conversation active existe."""
    st.session_state.setdefault("conversations", {})
    convs = st.session_state.conversations
    if st.session_state.get("current_conversation_id") not in convs:
        if convs:
            st.session_state.current_conversation_id = list(convs)[-1]
        else:
            create_conversation()


initialize_conversations = init_conversations  # alias de compatibilité


def select_conversation(cid):
    if cid in st.session_state.conversations:
        st.session_state.current_conversation_id = cid


def delete_conversation(cid):
    """Supprime une conversation ; bascule sur une autre (ou en crée une) si besoin."""
    convs = st.session_state.conversations
    convs.pop(cid, None)
    if st.session_state.get("current_conversation_id") == cid or not convs:
        if convs:
            st.session_state.current_conversation_id = list(convs)[-1]
        else:
            create_conversation()


def get_current_conversation():
    return st.session_state.conversations[st.session_state.current_conversation_id]


def list_conversations():
    """Conversations de la plus récente à la plus ancienne."""
    return list(reversed(list(st.session_state.conversations.values())))


# -------------------------------------------------------------- messages
def add_message(role, content, model=None):
    """Ajoute un message à la conversation active.

    Retourne True si le titre vient d'être défini (1er message utilisateur).
    """
    conv = get_current_conversation()
    msg = {"role": role, "content": content}
    if role == "assistant" and model:
        msg["model"] = model
    conv["messages"].append(msg)
    if model:
        conv["model"] = model
    if role == "user" and conv["title"] == DEFAULT_TITLE:
        title = " ".join(content.split())
        conv["title"] = title[:42] + ("…" if len(title) > 42 else "")
        return True
    return False


def get_messages_for_model(conv=None):
    """Messages au format attendu par ollama.chat (role + content uniquement)."""
    conv = conv or get_current_conversation()
    return [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]


def models_used(conv):
    """Modèles ayant répondu dans la conversation, dans l'ordre d'apparition."""
    seen = []
    for m in conv["messages"]:
        if m.get("model") and m["model"] not in seen:
            seen.append(m["model"])
    return seen


# ---------------------------------------------------------------- export
def get_export_txt(conversation):
    lines = [
        f"Conversation : {conversation['title']}",
        f"Créée le     : {conversation.get('created_at', 'N/A')}",
        f"Modèles      : {', '.join(models_used(conversation)) or 'N/A'}",
        "=" * 50,
        "",
    ]
    for msg in conversation["messages"]:
        who = "Utilisateur" if msg["role"] == "user" else f"Assistant ({msg.get('model', 'N/A')})"
        lines.extend([f"[{who}]", msg["content"], ""])
    return "\n".join(lines)


def get_export_json(conversation):
    return json.dumps(conversation, ensure_ascii=False, indent=2)


def get_export_all_json():
    return json.dumps(list(st.session_state.conversations.values()), ensure_ascii=False, indent=2)
