#!/bin/sh
# One-time setup for Option 2 on a Linux machine. Run as root: sudo sh setup_isolation.sh
# Creates the unprivileged account the agent runs as. It has no password, no login
# shell and no home folder, and belongs to no group the evaluator uses.
set -eu
if ! getent passwd dch-agent >/dev/null; then
  useradd --system --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin --user-group dch-agent
fi
# Evaluator storage: owned by root, closed to everyone else.
mkdir -p /var/lib/dch01_v11
chown root:root /var/lib/dch01_v11
chmod 0700 /var/lib/dch01_v11
id dch-agent
