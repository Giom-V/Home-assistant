alias hastart='sudo systemctl start home-assistant@homeassistant.service'
alias hastatus='sudo systemctl status home-assistant@homeassistant.service'
alias hastop='sudo systemctl stop home-assistant@homeassistant.service'
alias haupgrade='sudo apt-get update;sudo apt-get upgrade; sudo apt autoremove; sudo su -s /bin/bash homeassistant -c "source /srv/homeassistant/bin/activate;pip3.7 install --upgrade homeassistant"'
alias hacheck='sudo su -s /bin/bash homeassistant -c "source /srv/homeassistant/bin/activate;hass --script check_config"'
alias upgradeall='sudo apt-get update;sudo apt-get upgrade; sudo apt autoremove; sudo su -s /bin/bash homeassistant -c "source /srv/homeassistant/bin/activate;pip-review --local --interactive"'
alias habash='sudo -u homeassistant -H /bin/bash'
#alias savePictures='sudo su -s /bin/bash homeassistant -c "rsync /home/homeassistant/.homeassistant/Share/* giom@192.168.86.123:/volume1/Photos/Timelapse/."'
sudo su -s /bin/bash homeassistant -c "sudo cp -f /home/homeassistant/.homeassistant/home-assistant.log /home/homeassistant/.homeassistant/home-assistant.previous.log"