APPS=core project investment organization maps

test:
	python manage.py test $(APPS)

run:
	python manage.py runserver

alljson:
	python manage.py dumpdata --indent=4 auth contenttypes cms text picture link file maps core opportunity project organization investment > all.json
	@echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
	@echo ""
	@echo "You *MUST* delete contenttype and auth.permissions"
	@echo "from all.json"
