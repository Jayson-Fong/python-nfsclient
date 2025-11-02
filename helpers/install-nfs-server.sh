#!/bin/sh

# This script is meant for execution by a CI flow, not developers
# or end-users. It is specifically made for Ubuntu and installs
# an NFS server with the assumption of root-level privileges.

# Install NFS Server
sudo apt update
sudo apt install -y nfs-kernel-server

# Create Share
sudo mkdir -p /mnt/nfs/secure
sudo mkdir -p /mnt/nfs/insecure

sudo chmod 777 /mnt/nfs/secure
sudo chmod 777 /mnt/nfs/insecure

sudo echo "/mnt/nfs/secure *(rw,sync,no_subtree_check)" | sudo tee -a /etc/exports
sudo echo "/mnt/nfs/insecure *(rw,sync,no_subtree_check,insecure)" | sudo tee -a /etc/exports

sudo exportfs -a
sudo systemctl restart nfs-kernel-server

# Prepare Files
sudo mkdir -p /mnt/nfs/secure/example/nfs/directory
echo "Hello World" | sudo tee -a /mnt/nfs/secure/hello
echo "Hello World" | sudo tee -a /mnt/nfs/secure/example/nfs/directory/file

sudo mkdir -p /mnt/nfs/insecure/example/nfs/directory
echo "Hello World" | sudo tee -a /mnt/nfs/insecure/hello
echo "Hello World" | sudo tee -a /mnt/nfs/insecure/example/nfs/directory/file
