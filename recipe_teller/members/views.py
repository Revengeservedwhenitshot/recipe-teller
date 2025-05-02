from django.http import HttpResponse,HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.core.cache import cache
from django.utils.text import slugify
from .forms import RecipeForm
from .models import Recipe, Favourite
from typing import Any
import requests, json, random 
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.core.serializers.json import DjangoJSONEncoder 


# Replace these with your actual API keys
SPOONACULAR_API_KEY = 'd525ce27b29c4e0c82a1ee01027deee0'
YOUTUBE_API_KEY = 'AIzaSyCJwpnHsybfNOUr26HN9dwJqlUZdgIiAiY'


def members(request):
    trending_recipes = fetch_trending_recipes()
    return render(request, 'index.html', {
        'trending_recipes': trending_recipes,
        'trending_recipes_json': json.dumps(trending_recipes, cls=DjangoJSONEncoder)
    })

#Redirection to submit_recipe form page
def submit_recipe(request):
    return render(request, 'submit_recipe.html')

# Function to get recipes from Spoonacular API
def fetch_recipes(ingredients):
    key = f"recipes_{slugify(ingredients)}"
    cached_data = cache.get(key)
    if cached_data:
        return cached_data
    # ... rest of your code ...

    url = f'https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&apiKey={SPOONACULAR_API_KEY}'
    response = requests.get(url)
    try:
        data = response.json()
        if isinstance(data, list):
            cache.set(key, data, timeout=3600) # Cache for 5 minutes
            return data
        else:
            return []
    except ValueError:
        return []  # Return empty list if JSON parsing fails
    

def fetch_instructions(recipe_id):
    key = f"instructions_{recipe_id}"
    cached_data = cache.get(key)
    if cached_data:
        return cached_data
    # ... rest of your code ...

    url = f'https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={SPOONACULAR_API_KEY}'
    response = requests.get(url)
    try:
        data = response.json()
        if isinstance(data, list) and data:
            instructions = " ".join([step["step"] for step in data[0].get("steps", [])])
            cache.set(key, instructions, timeout=3600)
            return instructions
    except ValueError:
        pass
    
    return "No instructions available."


def fetch_video(recipe_name):
    key = f"video_{slugify(recipe_name)}"
    cached_data = cache.get(key)
    if cached_data:
        print(f"Using cached video ID for {recipe_name}: {cached_data}")
        return cached_data

    try:
        # Make the search query more specific and URL encode it
        search_query = f"{recipe_name} recipe cooking"
        encoded_query = requests.utils.quote(search_query)
        youtube_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={encoded_query}&type=video&maxResults=1&key={YOUTUBE_API_KEY}'
        
        print(f"Fetching video for recipe: {recipe_name}")
        print(f"YouTube API URL: {youtube_url}")
        
        response = requests.get(youtube_url)
        print(f"Response status code: {response.status_code}")
        
        data = response.json()
        print(f"Response data: {data}")
        
        if response.status_code != 200:
            error_message = data.get('error', {}).get('message', 'Unknown error')
            print(f"YouTube API Error: {error_message}")
            return None
            
        if 'items' in data and data['items']:
            video_id = data['items'][0]['id'].get('videoId')
            if video_id:
                print(f"Found video ID: {video_id} for recipe: {recipe_name}")
                cache.set(key, video_id, timeout=3600)
                return video_id
            else:
                print(f"No video ID found in response for recipe: {recipe_name}")
        else:
            print(f"No items found in YouTube response for recipe: {recipe_name}")
    except Exception as e:
        print(f"Error fetching video for {recipe_name}: {str(e)}")
        import traceback
        print(traceback.format_exc())
    return None

# View for handling user input and returning recipes
def recipe_teller(request):
    if request.method == 'GET':
        ingredients = request.GET.get('ingredients', '')
        recipe_list = []

        if ingredients:
            cache_key = f"db_recipes_{slugify(ingredients)}"
            cached_recipes = cache.get(cache_key)
            if cached_recipes:
                print(f"Using cached recipes for ingredients: {ingredients}")
                return render(request, 'index.html', {
                    'recipes': cached_recipes,
                    'searched_ingredients': ingredients
                })

            # Step 1: Check if recipes exist in DB for given ingredients
            db_recipes = Recipe.objects.filter(ingredients__icontains=ingredients)
            if db_recipes.exists():
                print(f"Found {db_recipes.count()} recipes in database for ingredients: {ingredients}")
                recipe_list = list(db_recipes)
            else:
                # No recipes found locally, call API
                print(f"Fetching recipes from API for ingredients: {ingredients}")
                recipes = fetch_recipes(ingredients)
                
                for recipe in recipes:
                    recipe_name = recipe.get('title', 'Unknown Recipe')
                    recipe_id = recipe.get('id', 0)
                    recipe_ingredients = ", ".join([
                        ingredient.get('name', '') 
                        for ingredient in recipe.get('usedIngredients', []) + recipe.get('missedIngredients', [])
                    ])
                    recipe_instructions = fetch_instructions(recipe_id)
                    
                    # Fetch video and ensure we have a response
                    video_url = fetch_video(recipe_name)
                    print(f"Video URL for {recipe_name}: {video_url}")

                    # Save recipe to DB with video URL
                    recipe_obj, created = Recipe.objects.update_or_create(
                        name=recipe_name,
                        defaults={
                            'ingredients': recipe_ingredients,
                            'instructions': recipe_instructions,
                            'video_url': video_url if video_url else None
                        }
                    )
                    print(f"{'Created' if created else 'Updated'} recipe: {recipe_name} with video URL: {video_url}")
                    recipe_list.append(recipe_obj)

                # Cache the results
                cache.set(cache_key, recipe_list, timeout=3600)
                print(f"Cached {len(recipe_list)} recipes for ingredients: {ingredients}")

        return render(request, 'index.html', {
            'recipes': recipe_list,
            'searched_ingredients': ingredients,
            'trending': not ingredients
        })

# submit_recipe page form
def submit_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            form.save()  # Save form data to database
            return redirect('success')  # Redirect after successful form submission
    else:
        form = RecipeForm()
    
    return render(request, 'submit_recipe.html', {'form': form})

# myapp/views.py
def success(request):
    return render(request, 'success.html')

#trending recipes
def fetch_trending_recipes():
    key = "trending_recipes"
    cached_data = cache.get(key)
    if cached_data:
        return random.sample(cached_data, min(len(cached_data), 3))

    url = f"https://api.spoonacular.com/recipes/random?number=10&apiKey={SPOONACULAR_API_KEY}"
    response = requests.get(url)
    try:
        data = response.json()
        recipes = data.get("recipes", [])
        trending_list = []
        for recipe in recipes:
            recipe_title = recipe.get('title', '')
            video_url = fetch_video(recipe_title)  # Get video ID
            
            trending_list.append({
                'name': recipe_title,
                'ingredients': ", ".join([ing.get('name', '') for ing in recipe.get('extendedIngredients', [])]),
                'instructions': recipe.get('instructions', 'No instructions available'),
                'image': recipe.get('image'),
                'video_url': video_url  # This will be the video ID
            })
            
        cache.set(key, trending_list, timeout=1800)  # Cache for 30 minutes
        return random.sample(trending_list, min(len(trending_list), 3))
    except Exception as e:
        print(f"Error in fetch_trending_recipes: {str(e)}")
        return []
    
def members(request):
    trending_recipes = fetch_trending_recipes()

    return render(request, 'index.html', {
        'trending_recipes': trending_recipes,
        'trending_recipes_json': json.dumps(trending_recipes, cls=DjangoJSONEncoder)
    })

#save favourites recipes
@csrf_protect
@login_required
def save_favourite(request: Any, recipe_id: Any) -> HttpResponseRedirect:
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, id=recipe_id)
        Favourite.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect('recipe_teller')



@login_required
def view_favourites(request):
    favourites = Favourite.objects.filter(user=request.user)
    return render(request, 'favourites.html', {'favourites': favourites})




