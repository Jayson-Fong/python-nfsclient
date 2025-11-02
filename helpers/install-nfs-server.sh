#!/bin/sh

# This script is meant for execution by a CI flow, not developers
# or end-users. It is specifically made for Ubuntu and installs
# an NFS server with the assumption of root-level privileges.

# Install NFS Server
sudo apt update
sudo apt install -y nfs-kernel-server

# Create Share
sudo mkdir -p /mnt/nfs/secure
sudo mdkr -p /mnt/nfs/insecure

sudo chmod 777 /mnt/nfs/secure
sudo chmod 777 /mnt/nfs/insecure

sudo echo "/mnt/nfs/secure *(rw,sync,no_subtree_check)" >> /etc/exports
sudo echo "/mnt/nfs/insecure *(rw,sync,no_subtree_check,insecure)" >> /etc/exports

sudo exportfs -a
sudo systemctl restart nfs-kernel-server

# Prepare Files
sudo mkdir -p /mnt/nfs/secure/example/nfs/directory
sudo touch /mnt/nfs/secure/example/nfs/directory/file
sudo chmod 777 /mnt/nfs/secure/example/nfs/directory/file
echo "Hello World" > /mnt/nfs/secure/example/nfs/directory/file

sudo mkdir -p /mnt/nfs/insecure/example/nfs/directory
sudo touch /mnt/nfs/insecure/example/nfs/directory/file
sudo chmod 777 /mnt/nfs/insecure/example/nfs/directory/file
echo "Hello World" > /mnt/nfs/insecure/example/nfs/directory/file
