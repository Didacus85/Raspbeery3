#!/bin/bash


#Debug enable next 3 lines
exec 5> install.txt
BASH_XTRACEFD="5"
set -x
# ------ end debug


function killpython()
{

sudo killall python3

}


function system_update_light()
{

# ---- system_update

sudo apt-get -y update

}

function system_update()
{

# ---- remove unnecessary packages

sudo apt-get remove --purge libreoffice-*
sudo apt-get remove --purge wolfram-engine


# ---- system_update

sudo apt-get -y update
sudo apt-get -y upgrade

}

function system_update_UI()
{

while true; do
    read -p "Do you wish to update the Raspbian system (y/n)?" yn
    case $yn in
        [Yy]* ) system_update; break;;
        [Nn]* ) break;;
        * ) echo "Please answer y or n.";;
    esac
done

}

function install_dependencies()
{


#--- start installing dependencies

sudo apt-get -y install python3-dev || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo apt -y install python3-pip || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo pip3 install flask || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
#sudo pip3 install pyserial || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo apt-get install python3-future
sudo pip install future
sudo pip install requests

#(GPIO)
sudo pip3 install RPi.GPIO
}

function enable_I2C()
{

# --- Enable I2C and Spi :
# /boot/config.txt

sed -i 's/\(^.*#dtparam=i2c_arm=on.*$\)/dtparam=i2c_arm=on/' /boot/config.txt
sed -i 's/\(^.*#dtparam=spi=on.*$\)/dtparam=spi=on/' /boot/config.txt
sed -i 's/\(^.*#dtparam=i2s=on.*$\)/dtparam=i2s=on/' /boot/config.txt

# --- install I2C tools
#sudo apt-get install python-smbus
#sudo apt-get install python3-smbus

sudo apt-get -y install git build-essential python3-dev python3-smbus || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}
sudo apt-get -y install -y i2c-tools  || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}

}




ask_reboot ()
{


read -p "Do you want to reboot the system? (y,n): " -e -i y doreboot
echo "Confirmed Answer: "$doreboot

if [ "$doreboot" == "y" ]; then
	sudo reboot
fi

}




install_Raspbeery ()
{
# --- INSTALL Raspbeery software
sudo apt-get -y install git || { echo "ERROR --------------------------Installation failed ----------------" && exit ;}


# check if file exist in local folder
aconf="/home/pi/env/Raspbeery3"
if [ -d $aconf ]; then  # if the directory exist
	cd /home/pi
else
	cd /home/pi
	sudo rm -r env
	mkdir env
	cd env
	#sudo rm -r raspbeery
    git clone https://github.com/Didacus85/Raspbeery3.git
	sudo killall python3
	mv Master Raspbeery3
    sudo chmod -R 777 /home/pi/env/
    #sudo chmod -R 777 /etc/nginx/sites-enabled/
	cd ..

fi

}


install_nginx ()
{
# this function is used
cd /home/pi

sudo apt-get -y install nginx

# create default file
aconf="/etc/nginx/sites-enabled/default"
if [ -f $aconf ]; then
   cp $aconf /home/pi/$aconf.1
   sudo rm $aconf
   echo "remove file"
fi


sudo bash -c "cat >> $aconf" << EOF
server {
    # for a public HTTP server:
    listen 124;
    server_name localhost;

    access_log off;
    error_log off;
    
    root /home/pi/env/Raspbeery3/templates;

    location / {
        proxy_pass http://127.0.0.1:5000;
    }

}
EOF

sudo service nginx start

cd ..
cd ..

}



copy_services()
{
sudo cp /home/pi/env/Raspbeery3/app.service /lib/systemd/system

sudo chmod 644 /lib/systemd/system/app.service
sudo chmod +x /home/pi/env/Raspbeery3/app.py
sudo systemctl daemon-reload
sudo systemctl enable app.service
sudo systemctl start app.service

sudo cp /home/pi/env/Raspbeery3/raspbeery.service /lib/systemd/system

sudo chmod 644 /lib/systemd/system/raspbeery.service
sudo chmod +x /home/pi/env/Raspbeery3/raspbeery.py
sudo systemctl daemon-reload
sudo systemctl enable app.service
sudo systemctl start app.service

}



# --- RUN the functions
killpython
system_update_light

install_dependencies
enable_I2C

install_nginx
install_Raspbeery

copy_services
echo "installation is finished!!! "
ask_reboot
