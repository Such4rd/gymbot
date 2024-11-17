#!/bin/bash

# Función para mostrar el menú
mostrar_menu() {
    echo "----------------------"
    echo "   Menú de Opciones"
    echo "----------------------"
    echo "1) Construir volumen"
    echo "2) Restablecer servicio"
    echo "3) Ver logs"
    echo "4) Ver estado del servicio"
    echo "5) Salir"
    echo "----------------------"
    echo -n "Seleccione una opción: "
}

# Función para construir el volumen
construir_volumen() {
    echo "[+] Construyendo el volumen..."
    docker-compose -f /home/smmulas/gymbot/docker-compose.yml build
    echo "Volumen construido."
}

# Función para restablecer el servicio
restablecer_servicio() {
    echo "[+] Restableciendo el servicio..."
    sudo systemctl restart gymbot.service
    echo "Servicio restablecido."
}

# Función para ver los logs del servicio, ultimas 5 lineas
ver_logs() {
    echo "Mostrando las últimas 5 líneas de los logs:"
    sudo journalctl -u gymbot.service -n 5 --no-pager
    echo "----------------------"
    echo "Presiona cualquier tecla para volver al menú..."
    read -n 1 -s # Espera a que el usuario presione una tecla
}

# Función para ver el estado del servicio
ver_estado_servicio() {
    echo "[+] Estado del servicio:"
    sudo systemctl status gymbot.service | grep "Active:"
}

#comando para entrar en la terminal del contenedor docker exec -it 68c5d90b357f bash

# Bucle para mostrar el menú y esperar una selección
while true; do
    mostrar_menu
    read opcion

    case $opcion in
        1)
            construir_volumen
            ;;
        2)
            restablecer_servicio
            ;;
        3)
            ver_logs
            ;;
        4)
            ver_estado_servicio
            ;;
        5)
            echo "[+] Saliendo del script..."
            exit 0
            ;;
        *)
            echo "[!] Opción no válida. Por favor, elija una opción del 1 al 5."
            ;;
    esac

    echo # Espacio en blanco para mejor legibilidad
done

#build del volumen
#docker-compose -f /home/smmulas/gymbot/docker-compose.yml build
#restablecer el servicio
#sudo systemctl restart gymbot.service

