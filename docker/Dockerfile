# sudo docker build --build-arg UID=`id -u` --build-arg GID=`id -g` -t ansible-modules-hashivault .
FROM python:2

LABEL version="0.1"
LABEL name="ansible-modules-hashivault"

ARG UID
ARG GID
ARG USER_NAME=dev

SHELL ["/bin/bash", "-c"]

RUN apt-get update -q && \
    apt-get install \
    curl \
    tmux \
    vim \
    jq \
    sudo \
    -y && \
    apt-get clean && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install virtualenv
RUN pip install virtualenvwrapper

# Download and install vault
ENV VAULT_VERSION 1.0.1
RUN wget "https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip" && \
    unzip "vault_${VAULT_VERSION}_linux_amd64.zip" && \
    cp vault /usr/local/sbin/vault && \
    chmod 0755 /usr/local/sbin/vault && \
    rm -rf /tmp/build/*

RUN echo "%${USER_NAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create non-root user
RUN groupadd -r -g ${GID} ${USER_NAME} &&  \
    useradd -r -m -u ${UID}  -g ${USER_NAME} -G sudo -s /bin/bash ${USER_NAME}

USER ${USER_NAME}

RUN mkdir /home/${USER_NAME}/.Envs
RUN echo "export WORKON_HOME=~/.Envs" >> /home/${USER_NAME}/.bashrc
RUN echo "source /usr/local/bin/virtualenvwrapper.sh" >> /home/${USER_NAME}/.bashrc

ENV WORKON_HOME=/home/${USER_NAME}/.Envs
RUN source /usr/local/bin/virtualenvwrapper.sh && \
    mkvirtualenv ansible-modules-hashivault

CMD ["/bin/bash"]
