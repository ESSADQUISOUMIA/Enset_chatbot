"""Application Streamlit : interface et conversations ENSET Chatbot."""
import streamlit as st
import ollama
from modules.conversations import initialize_conversations, get_current_conversation
from modules.interface import render_conversation_sidebar, render_conversation_history
from modules.styles import apply_styles

st.set_page_config(page_title="ENSET Chatbot", layout="wide", initial_sidebar_state="expanded")
apply_styles()
initialize_conversations()
mode = render_conversation_sidebar()

with st.sidebar.expander("Paramètres du modèle", expanded=False):
    selected_model = st.selectbox("Modèle", ["llama3.2", "qwen:0.5b"])
    temperature = st.slider("Température", 0.0, 2.0, 0.7, 0.1)
    top_k = st.slider("Top-k", 1, 100, 40)
    top_p = st.slider("Top-p", 0.0, 1.0, 0.9, 0.05)
    max_tokens = st.slider("Tokens maximum", 1, 2048, 512)

if mode == "Comparaison":
    st.markdown('<div class="enset-kicker">Espace comparaison</div>', unsafe_allow_html=True)
    st.markdown('<div class="enset-heading">Comparer les modèles.</div>', unsafe_allow_html=True)
    st.markdown('<div class="enset-subtitle">Une navigation prête pour le module de comparaison.</div>', unsafe_allow_html=True)
    st.info("Ce mode sera activé après l'intégration du module de la personne 2.")
    st.stop()

conversation = get_current_conversation()
render_conversation_history(conversation)
messages = conversation["messages"]
prompt = st.chat_input("Écrivez votre message...")

if prompt and prompt.strip():
    prompt = prompt.strip()
    messages.append({"role": "user", "content": prompt})
    if len(messages) == 1:
        conversation["title"] = prompt[:42] + ("…" if len(prompt) > 42 else "")
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        answer = ""
        try:
            with st.spinner("Génération de la réponse..."):
                stream = ollama.chat(
                    model=selected_model,
                    messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                    options={"temperature": temperature, "top_k": top_k,
                             "top_p": top_p, "num_predict": max_tokens},
                    stream=True,
                )
                for chunk in stream:
                    # Ollama Python renvoie un objet avec attributs (et parfois un dict).
                    part = (chunk["message"]["content"] if isinstance(chunk, dict)
                            else chunk.message.content)
                    answer += part or ""
                    placeholder.markdown(answer + "▍")
            placeholder.markdown(answer or "*Aucune réponse générée.*")
            if answer:
                messages.append({"role": "assistant", "content": answer})
        except Exception as exc:
            st.error("Impossible de contacter Ollama ou le modèle sélectionné. Vérifiez le service et les modèles installés.")
            st.caption(str(exc))
    st.rerun()
