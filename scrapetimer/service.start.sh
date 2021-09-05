#!/bin/sh




sysd="${HOME}/.config/systemd/user"
service="${sysd}/sdgescraper.service"
timer="${sysd}/sdgescraper.timer"

if [ ! -d "${HOME}/.config/systemd/user" ]
then 
    mkdir "${HOME}/.config/systemd/user"
fi

if [ ! -f "${service}" -a ! -h "${service}" ]
then
    if [ ! -f './sdgescraper.service' ]
    then
        echo "ERROR: ${me}: no file './sdgescraper.service'" 1>&2
        exit 1
    fi
    ln -s "$( pwd )/sdgescraper.service" "${service}"
fi

if [ ! -f "${timer}" -a ! -h "${timer}" ]
then
    if [ ! -f './sdgescraper.timer' ]
    then
        echo "ERROR: ${me}: no file './sdgescraper.timer'" 1>&2
        exit 2
    fi
    ln -s "$( pwd )/sdgescraper.timer" "${timer}"
fi

# Test
systemctl --user enable sdgescraper.service
systemctl --user enable sdgescraper.service

# Install
#systemctl --user enable sdgescraper.timer
#systemctl --user enable sdgescraper.timer
