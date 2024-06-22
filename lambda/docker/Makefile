DOCKER_ARGS	= --rm --platform $(PLATFORM) -p 9000:8080
DOCKER_IMAGE	= lambda
PLATFORM	= linux/amd64

build:
	docker build --platform $(PLATFORM) -t $(DOCKER_IMAGE) .

run:
	docker run --rm --platform $(PLATFORM) -p 9000:8080 $(DOCKER_IMAGE)

shell:
	docker run --rm -i -t --platform $(PLATFORM) -p 9000:8080 --entrypoint bash $(DOCKER_IMAGE)
