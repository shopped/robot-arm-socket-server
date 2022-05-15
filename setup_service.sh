cp ./roboremote.service /lib/systemd/system/roboremote.service
sudo chmod 644 /lib/systemd/system/roboremote.service
sudo systemctl daemon-reload
sudo systemctl enable sample.service
chmod +x ./start.sh
echo "sudo reboot now"
