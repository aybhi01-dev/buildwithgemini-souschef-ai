# SousChef AI 🍳

SousChef AI is an intelligent culinary assistant powered by Google Agent Development Kit (ADK), Vertex AI, and Google Cloud Platform. It assists home cooks and food lovers with recipe discovery, nutritional macro calculations, pantry ingredient suggestions, AI dish photography, cooking technique video animations, and recipe bookmarking in Firestore.

![SousChef AI Demo Video](demo.gif)

---

## 🚀 Woven Capabilities & GCP Integrations

* **Vertex AI Agent Engine (Agent Runtime)**: Powered by Google ADK (`google-adk`) and `gemini-2.5-flash`.
* **Vertex AI Memory Bank**: Integrates `PreloadMemoryTool` and `LoadMemoryTool` for persistent long-term culinary memory across chat sessions.
* **Google Cloud Firestore**: Persists favorite recipes and meal logs (`log_favorite_recipe`).
* **Google Cloud Storage (GCS)**: Stores generated food photography and video animation assets in a public bucket (`tricoach-ai-media-qwiklabs-gcp-02-98210aa7ee5c`).
* **Vertex AI Imagen 3**: Generates high-resolution food photography using `imagen-3.0-generate-002` (`generate_dish_visual`).
* **Gemini Omni Flash Video Model**: Generates short cooking technique animations using `gemini-omni-flash-preview` in the `global` region (`generate_cooking_technique_video`).
* **Nutritional Macro Calculator**: Computes calories, protein, carbs, and fats per serving (`calculate_recipe_nutrition`).
* **Recipe Search & Pantry Matcher**: Searches recipes by cuisine, prep time, and available pantry items (`search_recipes`, `get_pantry_suggestions`).
* **FastAPI & Culinary Chat UI**: Responsive web application with recipe quick-chips, light/dark mode, and live Markdown rendering.

---

## 🛠️ Local Development & Setup

### Installation & Configuration

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set up Environment Variables**:
   ```bash
   export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
   export FIRESTORE_PROJECT="<your-firestore-project-id>"
   export AGENT_ENGINE_RESOURCE_NAME="<your-reasoning-engine-resource-name>"
   export AGENT_DIRECTORY="app"
   ```

3. **Run Agent Locally in Playground**:
   ```bash
   agents-cli playground
   ```

4. **Run Web Frontend Locally**:
   ```bash
   cd frontend
   uv run python main.py
   ```
