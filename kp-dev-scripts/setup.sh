#!/bin/bash

GITHUB_DIR="/mnt/Github"
# Setup tmux consoles
SESSION=dev

source /usr/local/bin/virtualenvwrapper.sh && /
workon ansible-modules-hashivault && /

# Setup ansible
pip install -r "$GITHUB_DIR/ansible/requirements.txt" && /

# Install local hvac
pip install -e "$GITHUB_DIR/hvac/" && /

# Install local ansible-modules-hashivault
pip install -e "$GITHUB_DIR/ansible-modules-hashivault/"


tmux ls | grep $SESSION 2>/dev/null
if [ "$?" != 0 ]; then
# New session
    tmux -2 new-session -d -s $SESSION

    # Rename default window
    tmux rename-window -t $SESSION:0 'dev'

    # Setup vault-server windows
    tmux new-window -t $SESSION:1 -n 'vault-server'
    tmux send-keys "cd $GITHUB_DIR/vault/kp-dev-storage" C-m
    tmux send-keys "/usr/local/sbin/vault server -config config.hcl" C-m

    # Setup vault-client window
    tmux new-window -t $SESSION:2 -n 'vault-client'
    tmux send-keys "export VAULT_ADDR=http://127.0.0.1:8200" C-m

    # Set default windows
    tmux select-window -t $SESSION:0
fi

# Attach
tmux -2 attach-session -t $SESSION
