#!/bin/bash

if  [ $(sudo su -s /bin/bash homeassistant -c "source /srv/homeassistant/bin/activate;hass --script check_config" | wc -l) -eq 1 ]
then
    sudo su -s /bin/bash homeassistant -c "sudo cp -f /home/homeassistant/.homeassistant/home-assistant.log /home/homeassistant/.homeassistant/home-assistant.previous.log"
    harestart
else
    echo "Some errors detected, impossible to restart!"
fi