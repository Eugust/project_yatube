# Project Yatube
Project from Yandex.Practicum courses

The project is a small social network where users can post their posts on different topics and attach images to them. Posts are divided into different topics (music, movies, etc.), the user himself creates a tag for his post. Also, the social network has the ability to subscribe to the author and track his latest updates and unsubscribe from the author. The author can track how many subscribers he has. Each author has his own page with summary information and all his posts.
## Tools
Django, HTML, CSS, Bootstrap
## Instruction
Create a virtual environment in the project
```
python -m venv venv
```
Activate virtual environment
```
. venv/bin/activate
```
Install all from file requirements.txt
```
pip install -r requirements.txt
```
Make migration
```
python manage.py makemigrations
python manage.py migrate
```
Create folder with static
```
python manage.py collectstatic
```
Run server
```
python manage.py runserver
```
