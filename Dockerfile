FROM python:3.10.8

WORKDIR /usr/src/app

COPY . ./
RUN python setup.py install

CMD [ "python", "-m", "santa" ]
