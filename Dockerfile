FROM python:3.8

WORKDIR /bot

COPY . .

RUN apt-get update
RUN apt-get install libgl1-mesa-glx fonts-nanum -qq -y
RUN rm /root/.cache/matplotlib/*
RUN pip install -r requirements.txt

CMD [ "python", "run.py" ]