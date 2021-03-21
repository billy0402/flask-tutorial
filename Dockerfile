FROM python:3.8-alpine

ENV FLASK_APP main.py
ENV FLASK_CONFIG docker

RUN apk add --no-cache build-base postgresql-dev

RUN adduser -D flasky
#USER flasky

WORKDIR /home/flasky

COPY Pipfile Pipfile.lock ./
RUN pip install pipenv
RUN python -m pipenv install --system --deploy --ignore-pipfile

COPY app app
COPY migrations migrations
COPY main.py config.py boot.sh ./
RUN chmod +x boot.sh

# 執行期組態
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
