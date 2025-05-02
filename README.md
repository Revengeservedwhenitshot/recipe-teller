# Recipe Teller

A Django web application that helps users find recipes based on available ingredients and provides video tutorials.

## Features

- Search recipes by ingredients
- View recipe details and instructions
- Watch video tutorials
- Save favorite recipes
- User authentication

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/Revengeservedwhenitshot/recipe-teller.git
cd recipe-teller
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
SECRET_KEY=your_secret_key
YOUTUBE_API_KEY=your_youtube_api_key
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

- `members/` - Main application directory
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)
  - `views.py` - View functions
  - `models.py` - Database models
  - `urls.py` - URL routing
- `recipe_teller/` - Project configuration
  - `settings.py` - Django settings
  - `urls.py` - Main URL configuration

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License. 