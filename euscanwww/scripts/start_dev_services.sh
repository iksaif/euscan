python manage.py celeryd -E -l INFO &
python manage.py celerybeat -l INFO &
python manage.py celerycam &
python manage.py runserver
