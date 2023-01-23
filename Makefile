.PHONY: client

start:
	docker swarm init
	docker compose build
	docker stack deploy -c swarm-compose.yml stack

stop:
	docker stack rm stack
	docker swarm leave --force

legacy-mode:
	docker compose build && docker compose up --remove-orphans

restart:
	docker compose restart

build:
	docker compose build

status:
	docker compose ps  # compose
	docker service ls  # swarm

purge:
	docker compose down -v --rmi all --remove-orphans

test:
	cd client && make test
	cd directory_node && make test
