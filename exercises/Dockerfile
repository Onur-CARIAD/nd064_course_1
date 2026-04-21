FROM registry.opensuse.org/opensuse/leap:15.6

# Install SSH and prerequisites
RUN zypper refresh \
 && zypper install -y openssh sudo \
 && ssh-keygen -A \
 && useradd -m -s /bin/bash vagrant \
 && echo "vagrant ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
 && mkdir -p /home/vagrant/.ssh

# Add the Vagrant public key (Solution B – static key)
COPY authorized_keys /home/vagrant/.ssh/authorized_keys

# ✅ THIS IS WHERE YOUR PERMISSIONS GO
RUN chown -R vagrant:vagrant /home/vagrant/.ssh \
 && chmod 700 /home/vagrant/.ssh \
 && chmod 600 /home/vagrant/.ssh/authorized_keys

# Expose SSH port
EXPOSE 22

# ✅ THIS MUST BE THE FINAL START COMMAND
CMD ["/usr/sbin/sshd", "-D"]