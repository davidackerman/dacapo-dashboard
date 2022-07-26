# Dacapo

## Installation:
1) `pip install -r requirements.txt`
2) `pip install .`

## Usage:
### Local dev server:
You can start a dev server via the command line interface.
The only requirement is that `DaCapo` can find its config file
in either `~/dacapo.yaml` or `~/.config/dacapo/dacapo.yaml`
`dacapo-dashboard dashboard`


### Docker server:
Using the `DockerFile` you can create an image capable of running the dashboard in a more production ready environment. This uses uwsgi and nginx to serve the necessary files. To use:
1. `docker build -t dacapo-dashboard .`
2. `docker run -p {desired_port}:80 -v ~/Code/Projects/DaCapo/dacapo/dacapo.yaml:/app/dacapo.yaml dacapo-dashboard`
You should then be able to access the dashboard at "http://{server_domain}:{desired_port}"