
import json
import uuid
from datetime import datetime

import streamlit as st

DEFAULT_TITLE = "Nouvelle conversation"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- état
def init_conversations() -> None:
    """À appeler au début de app.py : garantit qu'une conversation active existe."""
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    convs = st.session_state.conversations
    current = st.session_state.get("current_conversation_id")
    if current not in convs:
        if convs:
            st.session_state.current_conversation_id = list(convs)[-1]
        else:
            create_conversation()


def create_conversation(model: str | None = None) -> str:
    """Crée une conversation vide et la rend active."""
    conv_id = uuid.uuid4().hex[:8]
    st.session_state.conversations[conv_id] = {
        "id": conv_id,
        "title": DEFAULT_TITLE,
        "created_at": _now(),
        "model": model,
        "messages": [],
    }
    st.session_state.current_conversation_id = conv_id
    return conv_id


def select_conversation(conv_id: str) -> None:
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id


def delete_conversation(conv_id: str) -> None:
    """Supprime une conversation ; bascule sur une autre (ou en crée une) si besoin."""
    convs = st.session_state.conversations
    convs.pop(conv_id, None)
    if st.session_state.get("current_conversation_id") == conv_id:
        if convs:
            st.session_state.current_conversation_id = list(convs)[-1]
        else:
            create_conversation()


def get_current_conversation() -> dict:
    return st.session_state.conversations[st.session_state.current_conversation_id]


def list_conversations() -> list[dict]:
    """Conversations de la plus récente à la plus ancienne."""
    return list(reversed(list(st.session_state.conversations.values())))


# ------------------------------------------------------------ messages
def add_message(role: str, content: str, model: str | None = None) -> bool:
    """
    Ajoute un message à la conversation active.
    Retourne True si le titre a été mis à jour (1er message utilisateur),
    pour que l'interface puisse rafraîchir la barre latérale.
    """
    conv = get_current_conversation()
    msg = {"role": role, "content": content}
    if role == "assistant" and model:
        msg["model"] = model  # quel modèle a répondu (llama3.2 ou qwen:0.5b)
    conv["messages"].append(msg)
    if model:
        conv["model"] = model
    if role == "user" and conv["title"] == DEFAULT_TITLE:
        title = " ".join(content.split())
        conv["title"] = title[:30] + ("…" if len(title) > 30 else "")
        return True
    return False


def get_messages_for_model(conv: dict | None = None) -> list[dict]:
    """Messages au format attendu par ollama.chat (role + content uniquement)."""
    conv = conv or get_current_conversation()
    return [{"role": m["role"], "content": m["content"]} for m in conv["messages"]]


def models_used(conv: dict) -> list[str]:
    """Modèles ayant répondu dans la conversation, dans l'ordre d'apparition."""
    seen = []
    for m in conv["messages"]:
        mod = m.get("model")
        if mod and mod not in seen:
            seen.append(mod)
    return seen


# -------------------------------------------------------------- export
def conversation_to_txt(conv: dict) -> str:
    lines = [
        f"Conversation : {conv['title']}",
        f"Créée le     : {conv['created_at']}",
        f"Modèles      : {', '.join(models_used(conv)) or 'N/A'}",
        "=" * 50,
        "",
    ]
    for m in conv["messages"]:
        who = "Utilisateur" if m["role"] == "user" else f"Assistant ({m.get('model', 'N/A')})"
        lines += [f"[{who}]", m["content"], ""]
    return "\n".join(lines)


def conversation_to_json(conv: dict) -> str:
    return json.dumps(conv, ensure_ascii=False, indent=2)


def all_conversations_to_json() -> str:
    return json.dumps(
        list(st.session_state.conversations.values()), ensure_ascii=False, indent=2
    )
