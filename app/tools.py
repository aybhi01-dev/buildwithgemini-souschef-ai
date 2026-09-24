import base64
import uuid
import datetime
from typing import Any, Dict, List
from google import genai
from google.genai import types
from google.cloud import storage
from google.cloud import firestore

GCP_PROJECT = "qwiklabs-gcp-02-98210aa7ee5c"
GCS_BUCKET_NAME = "tricoach-ai-media-qwiklabs-gcp-02-98210aa7ee5c"

def search_recipes(query: str, max_prep_time_mins: int = 30) -> Dict[str, Any]:
    """Searches for recipes matching a cuisine, ingredient, or meal type.

    Args:
        query: Recipe keyword or cuisine type (e.g. 'Tuscan Garlic Pasta', 'High Protein Salad').
        max_prep_time_mins: Maximum preparation time in minutes.

    Returns:
        Dictionary containing matching recipe suggestions with preparation steps.
    """
    recipes_db = [
        {
            "name": "Tuscan Garlic Cream Pasta",
            "cuisine": "Italian",
            "prep_time_mins": 20,
            "ingredients": ["Penne pasta", "Heavy cream", "Garlic", "Sun-dried tomatoes", "Spinach", "Parmesan"],
            "difficulty": "Easy",
            "calories": 580
        },
        {
            "name": "Pan-Seared Salmon with Lemon Dill Asparagus",
            "cuisine": "Mediterranean",
            "prep_time_mins": 25,
            "ingredients": ["Salmon fillet", "Asparagus", "Fresh dill", "Lemon", "Olive oil", "Butter"],
            "difficulty": "Medium",
            "calories": 490
        },
        {
            "name": "Avocado & Quinoa Power Bowl",
            "cuisine": "Healthy / Vegetarian",
            "prep_time_mins": 15,
            "ingredients": ["Cooked quinoa", "Ripe avocado", "Cherry tomatoes", "Chickpeas", "Tahini dressing"],
            "difficulty": "Easy",
            "calories": 420
        },
        {
            "name": "Matcha Green Tea Soufflé Pancake",
            "cuisine": "Japanese Dessert",
            "prep_time_mins": 25,
            "ingredients": ["Culinary matcha", "Eggs", "Flour", "Milk", "Maple syrup", "Berries"],
            "difficulty": "Hard",
            "calories": 360
        }
    ]

    query_lower = query.lower()
    matches = [
        r for r in recipes_db
        if (query_lower in r["name"].lower() or query_lower in r["cuisine"].lower())
        and r["prep_time_mins"] <= max_prep_time_mins
    ]

    if not matches:
        matches = [recipes_db[0]]

    return {
        "query": query,
        "max_prep_time_mins": max_prep_time_mins,
        "results_count": len(matches),
        "recipes": matches
    }


def calculate_recipe_nutrition(recipe_name: str, servings: int = 2) -> Dict[str, Any]:
    """Calculates nutritional breakdown per serving for a recipe.

    Args:
        recipe_name: Name of the dish.
        servings: Number of servings prepared.

    Returns:
        Dictionary containing calories, protein, carbs, fats, and fiber per serving.
    """
    # Sample calculation logic
    base_cal = 480
    return {
        "recipe_name": recipe_name,
        "servings": servings,
        "per_serving": {
            "calories_kcal": base_cal,
            "protein_g": 32.5,
            "carbohydrates_g": 45.0,
            "dietary_fiber_g": 6.8,
            "total_fat_g": 18.2,
            "sodium_mg": 480
        },
        "total_batch_calories": base_cal * servings
    }


def get_pantry_suggestions(ingredients: str) -> Dict[str, Any]:
    """Provides recipe suggestions based on available pantry ingredients.

    Args:
        ingredients: Comma-separated list of available ingredients in pantry.

    Returns:
        Dictionary of suggested recipes utilizing the provided ingredients.
    """
    item_list = [i.strip() for i in ingredients.split(",")]
    return {
        "provided_ingredients": item_list,
        "suggested_dishes": [
            {
                "dish": f"Custom {item_list[0].title()} Stir-Fry",
                "matching_ingredients": item_list[:3],
                "additional_pantry_staples_needed": ["Soy sauce", "Garlic", "Cooking oil"]
            }
        ]
    }


def generate_dish_visual(dish_description: str, tool_context: Any = None) -> Dict[str, Any]:
    """Generates food photography for a dish using Vertex AI Imagen 3 and uploads to GCS.

    Args:
        dish_description: Detailed description of the prepared dish.

    Returns:
        Dictionary containing the public GCS HTTPS URL of the generated dish photo.
    """
    try:
        client = genai.Client(vertexai=True, project=GCP_PROJECT, location="us-central1")
        prompt = f"Professional gourmet studio food photography of {dish_description}, elegant plating, warm lighting, 4k resolution"
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                output_mime_type="image/png"
            )
        )

        image_bytes = response.generated_images[0].image.image_bytes
        filename = f"dish_{uuid.uuid4().hex[:8]}.png"

        # Save artifact for Playground
        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception as e:
                print(f"Warning: save_artifact failed: {e}")

        # Upload to GCS
        storage_client = storage.Client(project=GCP_PROJECT)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
        return {
            "public_url": public_url,
            "filename": filename,
            "description": dish_description
        }
    except Exception as e:
        return {"error": f"Dish visual generation failed: {str(e)}"}


def generate_cooking_technique_video(prompt: str, tool_context: Any = None) -> Dict[str, Any]:
    """Generates a short video demonstration of a cooking technique using gemini-omni-flash-preview in global region.

    Args:
        prompt: Description of the cooking technique animation.

    Returns:
        Dictionary containing public GCS HTTPS URL of the video.
    """
    try:
        client = genai.Client(vertexai=True, project=GCP_PROJECT, location="global")
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=f"Short 2-second cooking technique video animation of: {prompt}"
        )

        video_bytes = None
        mime_type = "video/mp4"

        if hasattr(interaction, "output_video") and interaction.output_video:
            data = getattr(interaction.output_video, "data", None)
            if data:
                video_bytes = base64.b64decode(data) if isinstance(data, str) else data

        if not video_bytes:
            for out in getattr(interaction, "outputs", []) or []:
                content = getattr(out, "content", []) or []
                if isinstance(content, list):
                    for part in content:
                        inline_data = getattr(part, "inline_data", None)
                        if inline_data and getattr(inline_data, "data", None):
                            raw = inline_data.data
                            video_bytes = base64.b64decode(raw) if isinstance(raw, str) else raw
                            if getattr(inline_data, "mime_type", None):
                                mime_type = inline_data.mime_type
                            break

        if not video_bytes:
            return {"error": "Failed to extract video bytes from gemini-omni-flash-preview."}

        filename = f"recipe_video_{uuid.uuid4().hex[:8]}.mp4"

        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
                tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception as e:
                print(f"Warning: save_artifact failed: {e}")

        storage_client = storage.Client(project=GCP_PROJECT)
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{filename}"
        return {
            "public_url": public_url,
            "filename": filename,
            "description": prompt
        }
    except Exception as e:
        return {"error": f"Cooking video generation failed: {str(e)}"}


def log_favorite_recipe(recipe_name: str, cuisine: str, prep_time_mins: int) -> Dict[str, Any]:
    """Logs a favorite recipe to Google Cloud Firestore.

    Args:
        recipe_name: Name of the dish.
        cuisine: Cuisine style.
        prep_time_mins: Preparation time in minutes.

    Returns:
        Confirmation dictionary with Firestore document ID.
    """
    try:
        db = firestore.Client(project=GCP_PROJECT)
        doc_ref = db.collection("favorite_recipes").document()
        data = {
            "recipe_name": recipe_name,
            "cuisine": cuisine,
            "prep_time_mins": prep_time_mins,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        doc_ref.set(data)
        return {
            "status": "success",
            "doc_id": doc_ref.id,
            "message": f"Logged {recipe_name} to favorite recipes database."
        }
    except Exception as e:
        return {"error": f"Failed to log favorite recipe to Firestore: {str(e)}"}
