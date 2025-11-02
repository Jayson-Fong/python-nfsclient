#!/bin/sh

# This script is meant for execution by a CI flow, not developers
# or end-users. It is specifically made for Ubuntu and installs
# an NFS server with the assumption of root-level privileges.

# Install NFS Server
apt update
apt install -y nfs-kernel-server

# Create Share
mkdir -p /mnt/nfs/secure
mdkr -p /mnt/nfs/insecure

chmod 777 /mnt/nfs/secure
chmod 777 /mnt/nfs/insecure

echo "/mnt/nfs/secure *(rw,sync,no_subtree_check)" >> /etc/exports
echo "/mnt/nfs/insecure *(rw,sync,no_subtree_check,insecure)" >> /etc/exports

exportfs -a
systemctl restart nfs-kernel-server

# Prepare Files
mkdir -p /mnt/nfs/secure/example/nfs/directory
echo "Hello World" > /mnt/nfs/secure/example/nfs/directory/file

mkdir -p /mnt/nfs/insecure/example/nfs/directory
echo "Hello World" > /mnt/nfs/insecure/example/nfs/directory/file
