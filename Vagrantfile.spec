# -*- mode: ruby -*-
# vi: set ft=ruby :

  # TOPOLOGY - this topology is for a Small Non-High Availability MinRole Farm comprised of two servers plus
  # Domain Controller and:
  # a) WFE / Distributed Cache
  # b) Application with Search Server
  # for more details on SharePoint Topologies https://technet.microsoft.com/en-us/library/mt743704(v=office.16).aspx
  # also, be sure to take a look at the HOWTOUSE.md on this repository.

require 'yaml'
require 'json'

error = Vagrant::Errors::VagrantError

machines = YAML.load_file 'spec/ressources.yml'
ANSIBLE_RAW_SSH_ARGS = []

#delete the inventory file if it exists so we can recreate
File.exists? "ansible/inventory/sample/hosts_vagrant.yaml"

File.open("ansible/inventory/sample/hosts_vagrant.yaml" ,'w') do |f|
  # Get Variables 
  machines.each do |machine|
    f.write "#{machine[0]}:\n"
    f.write "   hosts:\n"
    f.write "     #{machine[1]['name']}:\n"
    f.write "       ansible_ssh_host: #{machine[1]['ip_address']}\n"
    f.write "       ansible_user: vagrant\n"
    f.write "       ansible_password: vagrant\n"
    f.write "       ansible_ssh_extra_args: '-o IdentityFile=~/.vagrant.d/insecure_private_key'\n"
    f.write "       hostname: #{machine[1]['hostname']}\n"
  end
end

##########################
## Master nodes
##########################

# Get variables

machines.each do |machine|

    name = machine[1]['name']
    box =  machine[1]['base_img']
    playbook = machine[1]['playbook']
    hostname = machine[1]['hostname']
    memory = machine[1]['memory_nodes'] || '512'
    cpu = machine[1]['cpu_nodes'] || '1'
    ip_address = machine[1]['ip_address']
# Virtual machine
Vagrant.configure(2) do |config|


  config.vm.box_check_update = false

    # insert the private key from the host machine to the guest
    ANSIBLE_RAW_SSH_ARGS << "-o IdentityFile=~/.vagrant.d/insecure_private_key"


    config.vm.hostname = hostname
        # credentials
    config.ssh.username = "vagrant"
    config.ssh.password = "vagrant"
    config.vm.graceful_halt_timeout = 35
    config.vm.boot_timeout = 800

    #configure the network for this machine
    config.vm.network "private_network", ip: ip_address
    # Enable ssh forward agent
     config.ssh.forward_agent = true
    #config.vm.network :forwarded_port, guest: 22, host: 2222, id: "ssh", auto_correct: true
    
        config.vm.box = box

        config.vm.provider :virtualbox do |v|
          v.gui = false
          v.customize ["modifyvm", :id, "--memory", memory]
          v.customize ["modifyvm", :id, "--cpus", cpu]
          v.customize ["modifyvm", :id, "--vram", 128]
          v.customize ["modifyvm", :id, "--clipboard", "bidirectional"]
          v.customize ["modifyvm", :id, "--accelerate3d", "on"]
          v.customize ["modifyvm", :id, "--accelerate2dvideo", "on"]
      end

       # config.vm.provision :ansible do |ansible|
       #     ansible.limit = ""
       #     ansible.playbook = "ansible/plays/" + playbook
       #     ansible.inventory_path = "ansible/hosts_vagrant.yaml"
       #     ansible.verbose = "vvvv"
       #     ansible.raw_ssh_args = ANSIBLE_RAW_SSH_ARGS
       #    end
        # Run ServerSpec Tests for Domain Controller
        #config.vm.provision :serverspec do |spec|
        #  spec.pattern = 'spec/SP2012R2AD.sposcar.local/ad_spec.rb'
        #end

  end

end
