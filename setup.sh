echo "Installing git..."
sudo apt install git

echo "Cloning repo to home dir..."
cd ~
git clone https://gitlab.com/johanvandegriff/AlArmPiT.git

echo "Adding connection script to local crontab..."
CRON_JOB="@reboot /usr/bin/python2 /home/pi/AlArmPiT/web-servo.py
* * * * * curl localhost:5000/cron"
cron_temp_file=$(mktemp)
crontab -l > "$cron_temp_file"
if grep -Fx "$CRON_JOB" "$cron_temp_file"; then
  echo "Cron job already installed."
else
  echo "$CRON_JOB" >> "$cron_temp_file"
  crontab "$cron_temp_file"
fi
rm "$cron_temp_file"

echo "You need to set the timezone. Press ENTER, then select your region."
read a
sudo dpkg-reconfigure tzdata

echo "Reboot now to complete setup? (yes/no)"
read a
test "$a" == "yes" && sudo reboot || echo "Reboot cancelled. Reboot later to complete the installation."
