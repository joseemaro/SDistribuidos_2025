.PHONY: build up down logs clean

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

node1_log:
	docker logs -f logs_node1

node2_log:
	docker logs -f logs_node2

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f