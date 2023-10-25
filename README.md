# WSC Earth

This project is in aid of the [Bridgestone World Solar Challenge](https://www.worldsolarchallenge.org/).

This is a demonstration of a [python3 project](https://www.python.org/) which reads from an [Influx v3 database](https://www.influxdata.com/) using the [Influx Python integration](https://docs.influxdata.com/influxdb/cloud-serverless/reference/client-libraries/v3/python/) and [InfluxQL query](https://docs.influxdata.com/influxdb/cloud-serverless/reference/influxql/), and generates a web page using [Flask](https://flask.palletsprojects.com/en/2.1.x/). The web page contains a google map, inserted using the Google Maps API.

This is used to show sample data here: [http://telemetry.worldsolarchallenge.org/wscearth/sample/](http://telemetry.worldsolarchallenge.org/wscearth/sample/)

## Build and Run

To build and run locally, you can use docker and the Makefile. You'll need an InfluxDB token to access the database. We use [Docker Desktop](https://www.docker.com/products/docker-desktop) to make setup easy.

Once you have docker set up, on a Mac, or Linux:

```
INFLUX_TOKEN=your_influx_token_here GOOGLEMAPS_KEY=your_google_api_key_here make run
```

and then navigate to [http://localhost:5000](http://localhost:5000).

The key files are:

* [src/wscearth/views.py](src/wscearth/views.py) -- The main web app code. This is the most relevant bit to modify to suit your needs.
* [src/wscearth/templates/](src/wscearth/templates/) -- Contains HTML templates which are used to render web pages.
* [setup.cfg](setup.cfg) -- Defines how to install the python module.
* [Dockerfile](Dockerfile) -- Definition of how to build a docker image to run this app.
* [Makefile](Makefile) -- A makefile which contains commands and targets to build and run th
e app.
* [README.md](README.md) -- This README file.
* [.github/](.github/) -- Definition of the continuous integration steps.


## Deployment

The resulting docker container can be published to a docker repository, and run in any environment that can host docker containers, for example, Kubernetes.

## Getting in touch

Please reach out to the BWSC Technical Faculty, or the BWSC community members via the on-line forum linked from the [BWSC Web Site](https://www.worldsolarchallenge.org/). Contributions welcome, via pull request on [github.com](https://github.com/worldsolarchallenge/wscearth).
