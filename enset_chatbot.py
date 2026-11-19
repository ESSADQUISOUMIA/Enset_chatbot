
import streamlit as st
import ollama
import json
from uuid import uuid4

# ==========================================
# 1. CONFIGURATION DE L'APPLICATION
# ==========================================

st.set_page_config(
    page_title="ENSET Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 ENSET Chatbot")

# ==========================================
# 2. CONFIGURATION DES MODÈLES OLLAMA
# ==========================================

st.sidebar.header("⚙️ Options de configuration")

# Sélection du modèle
available_models = ["llama3.2", "qwen:0.5b"]

selected_model = st.sidebar.selectbox(
    "Modèle",
    available_models,
    index=0
)

# Température
temperature = st.sidebar.slider(
    "Température",
    min_value=0.0,
    max_value=2.0,
    value=0.7,
    step=0.1
)

# Top-k
top_k = st.sidebar.slider(
    "Top-k",
    min_value=1,
    max_value=100,
    value=40,
    step=1
)

# Top-p
top_p = st.sidebar.slider(
    "Top-p",
    min_value=0.0,
    max_value=1.0,
    value=0.9,
    step=0.05
)

# Nombre maximal de tokens
max_tokens = st.sidebar.slider(
    "Nombre maximal de tokens",
    min_value=1,
    max_value=2048,
    value=512,
    step=1
)

# ==========================================
# 3. INITIALISATION DES CONVERSATIONS
# ==========================================

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None


# ==========================================
# 4. FONCTIONS DE GESTION DES CONVERSATIONS
# ==========================================

def create_conversation():
    """Créer une nouvelle conversation vide."""

    conversation_id = str(uuid4())

    st.session_state.conversations[conversation_id] = {
        "title": "Nouvelle conversation",
        "messages": []
    }

    st.session_state.current_conversation_id = conversation_id

    return conversation_id


def delete_conversation(conversation_id):
    """Supprimer une conversation sélectionnée."""

    if conversation_id in st.session_state.conversations:
        del st.session_state.conversations[conversation_id]

    # Si aucune conversation ne reste
    if not st.session_state.conversations:
        create_conversation()
    else:
        # Sélectionner une conversation restante
        st.session_state.current_conversation_id = next(
            iter(st.session_state.conversations)
        )


def change_conversation():
    """Mettre à jour la conversation active."""

    st.session_state.current_conversation_id = (
        st.session_state.conversation_selector
    )


# Initialiser la première conversation
if not st.session_state.conversations:
    create_conversation()

# Vérifier que la conversation active existe
if (
    st.session_state.current_conversation_id
    not in st.session_state.conversations
):
    st.session_state.current_conversation_id = next(
        iter(st.session_state.conversations)
    )


# ==========================================
# 5. SIDEBAR : GESTION DES CONVERSATIONS
# ==========================================

st.sidebar.divider()

st.sidebar.header("💬 Mes conversations")

# Bouton nouvelle conversation
if st.sidebar.button(
    "➕ Nouvelle conversation",
    use_container_width=True
):
    create_conversation()

    # Synchroniser le sélecteur
    st.session_state.conversation_selector = (
        st.session_state.current_conversation_id
    )

    st.rerun()


# Récupérer tous les identifiants
conversation_ids = list(
    st.session_state.conversations.keys()
)

# Synchroniser la sélection avec la conversation active
if (
    st.session_state.get("conversation_selector")
    not in conversation_ids
):
    st.session_state.conversation_selector = (
        st.session_state.current_conversation_id
    )

# Sélecteur des conversations
selected_id = st.sidebar.selectbox(
    "Historique des conversations",
    options=conversation_ids,
    format_func=lambda cid: (
        st.session_state.conversations[cid]["title"]
    ),
    key="conversation_selector",
    on_change=change_conversation
)

# Bouton supprimer
if st.sidebar.button(
    "🗑️ Supprimer la conversation",
    use_container_width=True
):
    delete_conversation(selected_id)

    # Synchroniser après suppression
    st.session_state.conversation_selector = (
        st.session_state.current_conversation_id
    )

    st.rerun()


# ==========================================
# 6. RÉCUPÉRER LA CONVERSATION ACTIVE
# ==========================================

current_id = st.session_state.current_conversation_id

conversation = st.session_state.conversations[current_id]

messages = conversation["messages"]


# ==========================================
# 7. EXPORTATION DES CONVERSATIONS
# ==========================================

st.sidebar.divider()
st.sidebar.subheader("📥 Exporter la conversation")

# Exportation TXT
txt_content = f"Conversation : {conversation['title']}\n"
txt_content += "=" * 40 + "\n\n"

for message in messages:

    role = (
        "Utilisateur"
        if message["role"] == "user"
        else "Assistant"
    )

    txt_content += (
        f"{role} :\n"
        f"{message['content']}\n\n"
    )

# Bouton téléchargement TXT
st.sidebar.download_button(
    label="📄 Télécharger TXT",
    data=txt_content,
    file_name="conversation.txt",
    mime="text/plain",
    use_container_width=True
)

# Exportation JSON
json_content = json.dumps(
    conversation,
    ensure_ascii=False,
    indent=4
)

# Bouton téléchargement JSON
st.sidebar.download_button(
    label="📋 Télécharger JSON",
    data=json_content,
    file_name="conversation.json",
    mime="application/json",
    use_container_width=True
)


# ==========================================
# 8. AFFICHAGE DE LA CONVERSATION
# ==========================================

st.subheader(f"💬 {conversation['title']}")

# Afficher les messages existants
for message in messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==========================================
# 9. SAISIE DU MESSAGE UTILISATEUR
# ==========================================

prompt = st.chat_input(
    "Que voulez-vous me demander ?"
)

if prompt:

    # Afficher le message utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ajouter le message à la conversation active
    messages.append({
        "role": "user",
        "content": prompt
    })

    # Générer automatiquement un titre
    # à partir du premier message
    if len(messages) == 1:
        conversation["title"] = prompt[:30]

    # ======================================
    # 10. GÉNÉRATION DE LA RÉPONSE OLLAMA
    # ======================================

    with st.chat_message("assistant"):

        message_placeholder = st.empty()

        full_response = ""

        try:

            with st.spinner(
                "Génération de la réponse en cours..."
            ):

                # Appel Ollama avec streaming
                for response in ollama.chat(
                    model=selected_model,
                    messages=[
                        {
                            "role": m["role"],
                            "content": m["content"]
                        }
                        for m in messages
                    ],
                    options={
                        "temperature": temperature,
                        "top_k": top_k,
                        "top_p": top_p,
                        "num_predict": max_tokens
                    },
                    stream=True
                ):

                    # Récupérer progressivement
                    # le contenu de la réponse
                    chunk = response["message"]["content"]

                    full_response += chunk

                    # Mise à jour progressive
                    message_placeholder.markdown(
                        full_response + "▌"
                    )

            # Afficher la réponse complète
            message_placeholder.markdown(full_response)

            # Enregistrer la réponse dans
            # la bonne conversation
            messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:

            # Afficher une erreur compréhensible
            st.error(
                "Une erreur est survenue pendant "
                "la génération de la réponse."
            )

            st.warning(
                "Vérifiez qu'Ollama est démarré "
                "et que le modèle est installé."
            )

            st.code(str(e))

    # Actualiser l'interface après génération
    st.rerun()
