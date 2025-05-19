FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y libpq-dev

ENV ENVIRONMENT=production

ARG USERNAME=deployuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    apt-get update && \
    apt-get install -y sudo && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

WORKDIR /app

RUN python3 -m venv venv

COPY . .

RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt && pip install psycopg2-binary

EXPOSE 8000

CMD ["bash", "-c", ". venv/bin/activate && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
