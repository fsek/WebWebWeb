# Our image starts with Debian
FROM debian:12.7

RUN apt-get update -y

# This adds the PostgreSQL APT repository so postgres can be apt installed
RUN apt-get install -y postgresql-common
RUN /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y

# With the APT repository added we may apt install postgres, sed is for editing text later
RUN apt-get install -y postgresql-16 sed

# Preliminary way to add postgres authentication. Prepend a line in postgres conf using sed  
RUN sed -i '1s;^;host all postgres samenet trust\n;' /etc/postgresql/16/main/pg_hba.conf

# python venv must be installed through apt
RUN apt-get install -y python3.11 python3.11-venv sudo git

ENV ENVIRONMENT=development
ENV DATABASE_URL="postgresql+psycopg://postgres:password@localhost:5432/postgres"
ENV TEST_DATABASE_URL="postgresql+psycopg://postgres:password@localhost:5432/postgres_test"


# In prod we must NOT run our container with root user, security risk. 
# In the future I think we should use non-root user event in dev to make environment similar to prod

# Now create a non root user
# ARG USERNAME=gunnar
# ARG USER_UID=1000
# ARG USER_GID=$USER_UID


# Create the user
# RUN groupadd --gid $USER_GID $USERNAME \
  # && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME 

# \
# [Optional] Add sudo support. Omit if you don't need to install software after connecting.
# && apt-get update \
# && apt-get install -y sudo \
# && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
# && chmod 0440 /etc/sudoers.d/$USERNAME

# set our non-root user as default. running container as user 'root' is not secure
# RUN PATH=$PATH:/home/gunnar/.local/bin
# USER $USERNAME