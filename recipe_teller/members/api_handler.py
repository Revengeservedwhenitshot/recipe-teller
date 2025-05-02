import requests # type: ignore
from django.conf import settings

def get_recipes(ingredients):
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=5&apiKey={settings.SPOONACULAR_API_KEY}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []
