FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /project
WORKDIR /project
ADD . /project
RUN pip install -r requirements.txt