# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  config.vm.box = "generic/ubuntu2004"
  config.vm.synced_folder ".", "/vagrant", type: "nfs", nfs_udp: false

  config.vm.provider :libvirt do |libvirt|
    libvirt.cpus = 2
    libvirt.memory = 4000
  end

  config.vm.provision "shell", inline: <<-SHELL
     #export DEBIAN_FRONTEND=noninteractive
     #apt -y update
     #apt -y upgrade

     GO_URL="https://dl.google.com/go/go1.19.2.linux-amd64.tar.gz"
     GO_TAR=/opt/$(basename $GO_URL)
     if [[ ! -f $GO_TAR ]]; then
         curl -L -o $GO_TAR $GO_URL
     fi

     if [[ -d /opt/go ]]; then
         pushd /opt/
         tar xzvf $GO_TAR
         popd
     fi

     if [[ ! -x /usr/local/bin/go ]]; then
         ln -s /opt/go/bin/go /usr/local/bin/go
     fi

  SHELL

end
