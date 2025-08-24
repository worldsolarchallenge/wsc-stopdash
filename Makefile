DOCKER_NAME=wsc-stopdash
DOCKER_TAG=latest
DOCKER_REPO=dcasnowdon

INFLUX_URL ?= "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_ORG ?= "Bridgestone World Solar Challenge"
INFLUX_BUCKET ?= test

GOOGLEMAPS_KEY ?= AIzaSyD4cxmf6zr3SMovEYgZZe9eoEQCglqz3L8

#ENV_VARS=INFLUX_URL INFLUX_ORG INFLUX_TOKEN INFLUX_BUCKET QUERY_TIME
ENV_VARS=INFLUX_TOKEN GOOGLEMAPS_KEY INFLUX_BUCKET EXTERNAL_ONLY INFLUX_MEASUREMENT

export $(ENV_VARS)

.PHONY: build run

all: run

build:
	docker build -t $(DOCKER_NAME):$(DOCKER_TAG) .

run: build
	docker run -p 5000:5000 $(foreach e,$(ENV_VARS),-e $(e)) $(DOCKER_NAME)

publish: build
	docker image tag $(DOCKER_NAME):$(DOCKER_TAG) $(DOCKER_REPO)/$(DOCKER_NAME):$(DOCKER_TAG)

build/testenv: setup.cfg
		mkdir -p build
		python3 -m venv build/testenv
		build/testenv/bin/pip install --upgrade pip setuptools wheel legacy-cgi
		source build/testenv/bin/activate && pip install -e .
		touch $@

localtest: build/testenv
		source $</bin/activate && \
			WSC_CONFIG_FILE_PATH=../config-prod.yaml \
			INFLUX_MEASUREMENT=telemetry4 \
			INFLUX_TOKEN=$$(cat ../wsc_bucket_token.key) \
		flask --debug --app wsc_stopdash run
lint: build/testenv
		source $</bin/activate && \
		        pip install --upgrade pip setuptools wheel legacy-cgi && \
				pip install pylint && \
				pylint $$(git ls-files '*.py')

clean:
	rm -rf build
