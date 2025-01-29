FROM debian:12.7

ENV ENVIRONMENT=production

ARG USERNAME=deployuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN apt update -y && \
    apt install -y postgresql-common && \
    /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y && \
    apt install -y postgresql-16 sed python3.11 python3.11-venv sudo git && \
    sed -i '1s;^;host all postgres samenet md5\n;' /etc/postgresql/16/main/pg_hba.conf && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid $USER_GID $USERNAME && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
    apt-get update && \
    apt-get install -y sudo && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

WORKDIR /app

RUN python3.11 -m venv venv

COPY . .

RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app" ,"--host", "0.0.0.0", "--port", "8000"]
