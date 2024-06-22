.PHONY: all build clean run shell

DOCKER_ARGS	= --rm --platform $(PLATFORM) -p 9000:8080
DOCKER_IMAGE	= lambda
PLATFORM	= linux/amd64

build:
	docker build --platform $(PLATFORM) -t $(DOCKER_IMAGE) .

run:
	docker run $(DOCKER_ARGS) $(DOCKER_IMAGE)

shell:
	docker run -it --entrypoint bash $(DOCKER_ARGS) $(DOCKER_IMAGE)

clean:
