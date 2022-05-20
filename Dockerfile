FROM tiangolo/uwsgi-nginx-flask:python3.9
ENV STATIC_URL /static
ENV STATIC_PATH /app/dashboard/static
COPY ./requirements.txt /data/dacapo-dashboard/requirements.txt
RUN pip install -r /data/dacapo-dashboard/requirements.txt
COPY . /app