from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    name = models.CharField(max_length=255)  
    ingredients = models.TextField()
    instructions = models.TextField()
    video_url = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"
