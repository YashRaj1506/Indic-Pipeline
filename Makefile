build:
	docker-compose build 

ready:
	python batching/data_categorizer.py
	python batching/batch_creator.py

up:
	docker-compose up

start:
	python publishers.py