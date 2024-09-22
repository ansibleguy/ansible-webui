# Name of container
NAME?=ansible-webui

# Add username/ prefix for pushing images
TAG?=ansibleguy/$(NAME)

#WEBUI_ENVIRONMENT?=dev
WEBUI_ENVIRONMENT?=production
#WEBUI_ENVIRONMENT?=production_aws
#WEBUI_ENVIRONMENT?=unstable
#...

# Local server parameters
HOST?=127.0.0.1
PORT?=8000

# Bound storage, or Git volume?
# If STORAGE_TYPE is bind, then use ./var; else just use a volume called 'ansible'
STORAGE_TYPE?=volume
#STORAGE_TYPE?=bind
#STORAGE_DATA_PATH?=./var/data
#STORAGE_PLAY_PATH?=./var/play

# List of architectures for which to build release image (buildx)
RELEASE_ARCHS?=linux/arm/v7,linux/arm64/v8,linux/amd64

# Simple docker suite
run: run.$(WEBUI_ENVIRONMENT)
stop: stop.$(WEBUI_ENVIRONMENT)
test: test.$(WEBUI_ENVIRONMENT)
logs: logs.$(WEBUI_ENVIRONMENT)
tail: tail.$(WEBUI_ENVIRONMENT)
purge: purge.$(WEBUI_ENVIRONMENT)

clean: clean.$(WEBUI_ENVIRONMENT)
	-docker rmi $(TAG):$(VERSION)

build: build.$(WEBUI_ENVIRONMENT)
	docker tag $(NAME).$(WEBUI_ENVIRONMENT) $(TAG):$(VERSION)

.PHONY: build run stop test logs tail clean purge

# Get version for image tagging; if current git ref is tagged, use that.
# If it's HEAD, use 'latest'. Else, use the commit ref.
VERSION?=$(shell \
	if git describe --exact-match --tags HEAD > /dev/null 2>&1; then \
		echo "$(git describe --tags)"; \
	else \
		echo "latest"; \
	fi)

# We generate a file containing a secret for credential encryption (see AW_SECRET in docs)
AW_SECRET_FILE=aw_secret

# If STORAGE_TYPE is bind, then use ./var; else just use Git volumes
STORAGE_DATA_PATH?=$(if $(filter bind,$(STORAGE_TYPE)),$(PWD)/var/data,$(NAME)-data)
STORAGE_PLAY_PATH?=$(if $(filter bind,$(STORAGE_TYPE)),$(PWD)/var/play,$(NAME)-play)

# Options for "docker run"
DOCKER_RUN_OPTS?=
DOCKER_RUN_OPTS+= \
	--publish $(HOST):$(PORT):8000 \
	--volume $(STORAGE_DATA_PATH):/data \
	--volume $(STORAGE_PLAY_PATH):/play \
	-e AW_SECRET=$(shell cat $(AW_SECRET_FILE))

# Options for "docker build"
DOCKER_BUILD_OPTS?=
DOCKER_BUILD_OPTS+= \
	--build-arg AW_VERSION=$(VERSION)
# DOCKER_BUILD_OPTS += --no-cache   # Uncomment for a clean build, if you want

# Environment-based rule templates

build.%: Dockerfile_%
	docker build -f $^ $(DOCKER_BUILD_OPTS) -t $(NAME).$*  .

test.%: build.%
	docker run -it --rm --name $(NAME).$* $(DOCKER_RUN_OPTS) $(NAME):$(VERSION)

run.%: build.% $(AW_SECRET_FILE)
	docker run -d --name $(NAME).$* $(DOCKER_RUN_OPTS) $(NAME):$(VERSION)

logs.%:
	docker logs $(NAME).$*

tail.%:
	docker logs -f $(NAME).$*

# Stop and destroy containers
stop.%:
	-docker stop $(NAME).$*
	-docker kill $(NAME).$*

# Clean images and containers
clean.%: stop.%
	-docker rm $(NAME).$*
	-docker rmi $(NAME).$*

# Clean volumes (persistent app state)
purge.%: clean.%
	if [ "$(STORAGE_TYPE)" == "bind" ]; then \
		rm -rf $(STORAGE_DATA_PATH) $(STORAGE_PLAY_PATH); \
	else \
		docker volume rm $(NAME)-data $(NAME)-play; \
	fi

$(AW_SECRET_FILE):
	openssl rand -hex 30 > $@

release:
	docker buildx build \
		-f Dockerfile_$(WEBUI_ENVIRONMENT) \
		$(DOCKER_BUILD_OPTS) \
		--platform $(RELEASE_ARCHS) \
		-t $(TAG):$(VERSION) \
		. \
