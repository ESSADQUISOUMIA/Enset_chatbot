
import ollama
import streamlit as st

from modules import conversations as conv_mgr
from modules import interface as ui
from modules.styles import apply_styles

st.set_page_config(page_title="ENSET Chatbot", layout="wide", initial_sidebar_state="expanded")
apply_styles()
conv_mgr.init_conversations()

# Le modèle sélectionné doit toujours être valide avant l'affichage du sélecteur
if st.session_state.get("selected_model") not in ui.AVAILABLE_MODELS:
    st.session_state.selected_model = ui.AVAILABLE_MODELS[0]

mode = ui.render_conversation_sidebar()

# ------------------------------------------------ options de configuration
with st.sidebar.expander("Paramètres du modèle", expanded=False):
    # TODO (P2) : remplacer par la détection des modèles Ollama installés
    selected_model = st.selectbox("Modèle", ui.AVAILABLE_MODELS, key="selected_model")
    temperature = st.slider("Température", 0.0, 2.0, 0.7, 0.1)
    top_k = st.slider("Top-k", 1, 100, 40, 1)
    top_p = st.slider("Top-p", 0.0, 1.0, 0.9, 0.05)
    max_tokens = st.slider("Nombre maximal de tokens", 1, 2048, 512, 1)

options = {"temperature": temperature, "top_k": top_k, "top_p": top_p, "num_predict": max_tokens}

# ------------------------------------------------------ mode comparaison
if mode == ui.MODE_COMPARE:
    try:
        from modules.model_comparison import render_comparison_page  
    except ImportError:
        render_comparison_page = None

    if render_comparison_page:
        render_comparison_page(ui.AVAILABLE_MODELS, options)
    else:
        st.markdown('<div class="enset-kicker">Espace comparaison</div>', unsafe_allow_html=True)
        st.markdown('<div class="enset-heading">Comparer les modèles</div>', unsafe_allow_html=True)
        
    st.stop()


# ------------------------------------------------------------ mode chat
def token_stream(model, messages, opts):
    
    for chunk in ollama.chat(model=model, messages=messages, options=opts, stream=True):
        yield (chunk["message"]["content"] if isinstance(chunk, dict)
               else chunk.message.content)


conversation = conv_mgr.get_current_conversation()
hero_slot = ui.render_conversation_history(conversation)  # None si des messages existent déjà

if hero_slot is not None:
    # Conversation vide : barre de saisie centrée dans la page
    input_slot = st.empty()
    with input_slot.container():
        _, center, _ = st.columns([1, 20, 1])
        with center:
            prompt = st.chat_input("Écrivez votre message...", key="chat_input_center")
else:
    # Discussion commencée : barre de saisie classique, fixée en bas
    input_slot = None
    prompt = st.chat_input("Écrivez votre message...", key="chat_input_bottom")

if prompt and prompt.strip():
    prompt = prompt.strip()
    if hero_slot is not None:  # 
        hero_slot.empty()
        input_slot.empty()
    with st.chat_message("user"):
        st.markdown(prompt)
    conv_mgr.add_message("user", prompt, model=selected_model)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            answer = ui.stream_with_indicator(
                placeholder,
                token_stream(selected_model, conv_mgr.get_messages_for_model(), options),
                selected_model,
            )
            if answer:
                conv_mgr.add_message("assistant", answer, model=selected_model)
                st.caption(f"Modèle : {selected_model}")
        except Exception as exc:
            placeholder.empty()
            st.error("Impossible de contacter Ollama ou le modèle sélectionné. "
                     "Vérifiez que le service est démarré et que le modèle est installé.")
            st.caption(str(exc))
        else:
            st.rerun()  
