all: build deploy  ## Build and deploy the stack

.PHONY: build
build:
	docker-compose build

.PHONY: deploy
deploy:
	docker-compose up -d
