APPS=core project investment organization

test:
	python manage.py test $(APPS)

run:
	python manage.py runserver
