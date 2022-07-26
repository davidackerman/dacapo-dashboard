FROM python:3

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install .
RUN pip install gevent gevent-websocket


# tell the port number the container should expose
EXPOSE 5000

# run the command
CMD dacapo-dashboard dashboard