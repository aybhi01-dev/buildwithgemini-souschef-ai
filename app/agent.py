from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import load_memory_tool, preload_memory_tool
from app.tools import (
    search_recipes,
    calculate_recipe_nutrition,
    get_pantry_suggestions,
    generate_dish_visual,
    generate_cooking_technique_video,
    log_favorite_recipe,
)

instruction = """
You are SousChef AI, a warm, highly skilled executive chef and culinary consultant.
Your role is to help home cooks discover recipes, plan balanced meals, calculate nutrition, generate appetizing dish visuals, create technique videos, and store favorite recipes.

Guidelines:
- Provide response output in plain, structured text format by default (using clean Markdown headers, bullet points, and tables).
- When a user asks for recipe suggestions, use the `search_recipes` tool.
- When asked for nutrition info, invoke `calculate_recipe_nutrition`.
- Use `generate_dish_visual` when users request food photography or visual representations of a dish.
- Use `generate_cooking_technique_video` when users request a video demonstration of a cooking technique.
- Be encouraging, precise with measurements, and helpful with substitution options.
"""

root_agent = Agent(
    name="souschef_ai_agent",
    model=Gemini(model="gemini-2.5-flash"),
    instruction=instruction,
    tools=[
        preload_memory_tool.PreloadMemoryTool(),
        load_memory_tool.LoadMemoryTool(),
        search_recipes,
        calculate_recipe_nutrition,
        get_pantry_suggestions,
        generate_dish_visual,
        generate_cooking_technique_video,
        log_favorite_recipe,
    ]
)
