# the python image is based on Debian
FROM python:3.12

RUN apt update
RUN apt install -y sudo sed
#sed is for editing text

# This adds the PostgreSQL APT repository
RUN apt install -y postgresql-common
RUN /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh -y

# With the APT repository added we may apt install postgres 
RUN apt install -y postgresql-16

# Preliminary way to add postgres authentication. Prepend a line in postgres conf using sed  
RUN sed -i '1s;^;host all postgres samenet trust\n;' /etc/postgresql/16/main/pg_hba.conf

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