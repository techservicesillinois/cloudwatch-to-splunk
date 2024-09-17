.PHONY: all build clean run shell

DOCKER_ARGS	= --rm --platform $(PLATFORM)
DOCKER_IMAGE	= lambda
DOCKER_PORTS	= -p 9000:8080
PLATFORM	= linux/amd64

build:
	docker build --platform $(PLATFORM) -t $(DOCKER_IMAGE) .

run:
	docker run $(DOCKER_PORTS) $(DOCKER_ARGS) $(DOCKER_IMAGE)

shell:
	docker run -it --entrypoint bash $(DOCKER_ARGS) $(DOCKER_IMAGE)

clean:
