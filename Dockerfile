FROM python:3.10

WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./bewise_test_task ./bewise_test_task

STOPSIGNAL SIGTERM

ENV DATABASE_URL=""
ENV FLASK_APP=bewise_test_task
ENV FLASK_RUN_HOST=0.0.0.0

ENTRYPOINT ["sh", "-c", "python -c \"from bewise_test_task.models import db; db.create_all()\" && \
    python -m flask run"]
