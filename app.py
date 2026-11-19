
import ollama
import streamlit as st

from modules import conversations as conv_mgr
from modules import interface as ui

st.set_page_config(page_title="ENSET Chatbot", page_icon="🤖", layout="wide")
st.title("ENSET Chatbot")

conv_mgr.init_conversations()

# ------------------------------------------------------------ navigation
mode = ui.render_mode_selector()

# --------------------------------------------- options de configuration
st.sidebar.header("Options de configuration")

available_models = ui.AVAILABLE_MODELS  # ["llama3.2", "qwen:0.5b"]
if st.session_state.get("selected_model") not in available_models:
    st.session_state.selected_model = available_models[0]
selected_model = st.sidebar.selectbox("Modèle", available_models, key="selected_model")
temperature = st.sidebar.slider("Température", 0.0, 2.0, 0.7, 0.1)
top_k = st.sidebar.slider("Top-k", 1, 100, 40, 1)
top_p = st.sidebar.slider("Top-p", 0.0, 1.0, 0.9, 0.05)
max_tokens = st.sidebar.slider("Nombre maximal de tokens", 1, 2048, 512, 1)

options = {
    "temperature": temperature,
    "top_k": top_k,
    "top_p": top_p,
    "num_predict": max_tokens,
}

# ------------------------------------------------------------ mode chat
if mode == ui.MODE_CHAT:
    ui.render_conversation_sidebar(default_model=selected_model)
    ui.render_export_buttons()

    conv = conv_mgr.get_current_conversation()
    st.caption(f"{conv['title']}  •  créée le {conv['created_at']}")
    ui.render_history(conv["messages"])

    prompt = st.chat_input("Que voulez-vous me demander ?")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        title_changed = conv_mgr.add_message("user", prompt, model=selected_model)

        def token_stream():

            for chunk in ollama.chat(
                model=selected_model,
                messages=conv_mgr.get_messages_for_model(),
                options=options,
                stream=True,
            ):
                yield chunk["message"]["content"]

        with st.chat_message("assistant"):
            placeholder = st.empty()
            try:
                answer = ui.stream_with_indicator(placeholder, token_stream(), selected_model)
                conv_mgr.add_message("assistant", answer, model=selected_model)
                st.caption(f" {selected_model}")
            except Exception as e:
                placeholder.empty()
                st.error(f"Erreur lors de l'appel à Ollama : {e}")
                title_changed = False  # ne pas effacer le message d'erreur

        if title_changed:
            st.rerun()  # rafraîchit le titre dans la barre latérale

# ------------------------------------------------------ mode comparaison
else:
    try:
        from modules.model_comparison import render_comparison_page  # P2

        render_comparison_page(available_models, options)
    except ImportError:
        st.info("Le module de comparaison (Personne 2) n'est pas encore intégré.")
