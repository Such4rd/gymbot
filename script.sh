#build del volumen
docker-compose -f /home/smmulas/gymbot/docker-compose.yml build
#restablecer el servicio
sudo systemctl restart gymbot.service