# ENSET Chatbot 

Chatbot local Streamlit + Ollama. Gestion de plusieurs conversations pendant une même session, sélection/suppression de discussions, export TXT/JSON, titre automatique et réponses en streaming.

## Prérequis
- Python 3.10 ou plus récent
- Ollama installé et démarré

## Installation sous Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull llama3.2
ollama pull qwen:0.5b
streamlit run app.py
```

Si Ollama ne fonctionne pas en tâche de fond, démarrez le service avec `ollama serve` dans un second terminal.

## Organisation
- `app.py` : paramètres de génération et boucle de chat Ollama.
- `modules/conversations.py` : stockage en session et exportations.
- `modules/interface.py` : sidebar et affichage des messages.
- `modules/__init__.py` : marque le dossier comme package Python.

## Tests manuels
1. Envoyer une question et vérifier la réponse.
2. Créer une autre conversation, envoyer une question, puis revenir à la précédente.
3. Vérifier que les historiques restent distincts.
4. Télécharger les exports TXT/JSON.
5. Supprimer une conversation, notamment la dernière.
6. Vérifier le spinner et le streaming.

Les discussions sont conservées pendant la session Streamlit seulement, sans persistance après réinitialisation de la session.

## Intégration
La personne 2 ajoutera le mode comparaison et l'accès aux modèles. La personne 3 ajoutera les métriques et le suivi matériel. Préserver les interfaces `get_current_conversation()` et `render_conversation_sidebar()` lors de l'intégration.

## Nouvelle interface
L'interface utilise un thème clair, une typographie moderne, des cartes de messages et aucune décoration emoji. Le menu latéral contient l'historique, les exports et les paramètres. La navigation « Comparaison » est préparée : l'implémentation de la comparaison appartient à la personne 2. Le style est isolé dans `modules/styles.py`.
