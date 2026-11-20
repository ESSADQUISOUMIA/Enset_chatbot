# ENSET Chatbot — Personne 1 (Conversations et interface)

Chatbot local Streamlit + Ollama avec les modèles `llama3.2` et `qwen:0.5b`.

## Fonctionnalités (Amélioration 1 + éléments de l'Amélioration 5)
- Plusieurs conversations dans la même session (`st.session_state`), bouton « Nouvelle conversation ».
- Liste des conversations : sélection, consultation, suppression (y compris la conversation active ou la dernière).
- Titre automatique à partir du premier message.
- Modèle enregistré **par réponse** : on peut passer de Llama 3.2 à Qwen 0.5B dans une même conversation.
- Export TXT / JSON de la conversation active, et JSON de toutes les conversations (boutons désactivés si vide).
- Navigation Conversation / Comparaison (le mode Comparaison appelle le module de la Personne 2 dès qu'il existe).
- Indicateur pendant la génération (nom du modèle, puis curseur de streaming) et message d'erreur clair si Ollama est indisponible.
- Logo et thème sobre sans emojis.

## Installation (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3.2
ollama pull qwen:0.5b
streamlit run app.py
```
Lancer la commande depuis le dossier qui contient `app.py`. Si Ollama ne tourne pas en tâche de fond : `ollama serve`.

## Organisation
```
app.py                    assemblage, paramètres de génération, boucle de chat
modules/conversations.py  données (créer, supprimer, ajouter, exporter) — aucun rendu
modules/interface.py      sidebar, historique, export, indicateur de génération
modules/styles.py         thème CSS et logo
assets/logo.svg           logo 
.streamlit/config.toml    couleurs des composants natifs
```

## Interfaces à préserver pour P2 et P3
| Interface | Utilisée par |
|---|---|
| `conversations.add_message(role, content, model=None)` | app.py |
| `conversations.get_messages_for_model()` | app.py, P2 |
| `interface.stream_with_indicator(placeholder, chunks, model_name)` | app.py |
| `interface.AVAILABLE_MODELS` | P2 (détection dynamique) |
| `model_comparison.render_comparison_page(available_models, options)` | fournie par P2 |
| `token_stream(model, messages, opts)` dans app.py | P3 (mesures TTFT, tokens/s) |

## Tests manuels
1. Envoyer une question : réponse en streaming, titre mis à jour, légende « Modèle : … ».
2. Nouvelle conversation, nouvelle question, retour à la précédente : historiques distincts.
3. Changer de modèle en cours de conversation : chaque réponse garde son modèle ; export TXT : `[Assistant (qwen:0.5b)]`.
4. Ouvrir une conversation : le sélecteur de modèle se remet sur son dernier modèle.
5. Exports TXT / JSON / tout (accents corrects), désactivés si la conversation est vide.
6. Supprimer la conversation active, puis toutes : une conversation vide est recréée.
7. Mode Comparaison : message d'attente tant que le module P2 est absent.
8. Arrêter Ollama puis envoyer un message : message d'erreur visible, pas de plantage.

Les discussions sont conservées pendant la session seulement (un rechargement F5 les efface : utiliser l'export).
