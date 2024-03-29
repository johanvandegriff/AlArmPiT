echo "Installing git..."
sudo apt install git python-flask -y

echo "Cloning repo to home dir..."
cd ~
git clone https://codeberg.org/johanvandegriff/AlArmPiT.git

echo "Adding connection script to local crontab..."
CRON_JOB="@reboot /home/pi/AlArmPiT/start.sh
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

if [[ "$1" == "--auto" ]]; then
  sudo timedatectl set-timezone "$2"
  sudo reboot
fi

echo "You need to set the timezone. Press ENTER, then select your region."
read a
sudo dpkg-reconfigure tzdata

echo "Reboot now to complete setup? (yes/no)"
read a
test "$a" == "yes" && sudo reboot || echo "Reboot cancelled. Reboot later to complete the installation."
