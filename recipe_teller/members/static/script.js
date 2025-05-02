document.addEventListener('DOMContentLoaded', () => {
    const recipesData = document.getElementById('recipesData');
    if (!recipesData) return;
    
    const recipes = JSON.parse(recipesData.textContent);
    let index = 0;

    function showRecipes() {
        const container = document.getElementById('trendingContainer');
        if (!container) return;
        container.innerHTML = '';

        const currentRecipes = recipes.slice(index, index + 3);
        currentRecipes.forEach((recipe, i) => {
            const card = document.createElement('div');
            card.className = 'recipe-card';
            card.style.animationDelay = `${0.2 * (i + 1)}s`;

            const videoUrl = recipe.video_url 
                ? `https://www.youtube.com/watch?v=${recipe.video_url}`
                : null;

            card.innerHTML = `
                <h3>${recipe.name}</h3>
                ${recipe.image ? `<img src="${recipe.image}" alt="${recipe.name}" width="200">` : ''}
                <p><strong>Ingredients:</strong> ${recipe.ingredients}</p>
                <p><strong>Instructions:</strong> ${recipe.instructions}</p>
                ${videoUrl 
                    ? `<a href="${videoUrl}" target="_blank" class="video-link">🎥 Watch Recipe Video</a>`
                    : '<p style="color: orange;">No video available for this recipe</p>'
                }
            `;
            container.appendChild(card);
        });

        index = (index + 3) % recipes.length;
    }

    showRecipes();
    setInterval(showRecipes, 5000);
});



  