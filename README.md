# Desafio SCM Latam

## Diagrama de Arquitectura

![image](/files/diagram.png)

### Supuestos

- Se supuso que el acceso "usando
  autenticación con un proveedor de identidad externo" es manejado fuera del sistema, por lo que no fue considerado dentro del diagrama.

- Al procesar los archivos y guardar el resultado en el bucket, es el mismo sistema el cual los entrega a los clientes (mediante SFTP u otra forma), por lo que el bucket tampoco es accesible desde internet.

## Preguntas

1. **En tu plataforma de monitoreo, te das cuenta que uno de los servidores (máquina virtual) no se está reportando hace varios días, cuando revisas la plataforma de administración, la instancia aparece como encendida, pero los registros no están siendo sincronizados. ¿Cuáles serían los pasos que realizarías para volver a poner en orden los registros?**

Posiblemente el _healthcheck_ no es lo suficientemente exhaustivo como para detectar una anomalía, por lo que no se generan alertas acerca de la instancia. Lo más factible es acceder a la máquina virtual y hacer debugging manual revisando los logs del sistema hasta lograr encontrar lo que está generando la falla. Una vez solucionado el problema, se deben estudiar medidas para que esto no vuelva a ocurrir, aplicando estas en todos los servidores.

2. **Acabas de instalar uno de nuestros software en un servidor con Windows Server, y cuando todo está completo te das cuenta que desde tu computador (fuera de la LAN) no puedes acceder. ¿Cuáles serían las causas posibles? ¿cómo los solucionarías?**

- Revisar que la VM tenga IP Pública, puede ser que no tenga una asignada, en tal caso asignarle una mediante el proveedor de nube.
- Revisar que el firewall de la red donde se encuentra la VM, o el de la misma VM, no estén bloqueando las peticiones de IP's públicas o hacia algún puerto que sea requerido para el acceso. En tal caso, se debe configurar los firewall correctamente.

3. **Uno de tus sistemas debe programarse para eliminar todo el contenido de una carpeta que no haya sido modificado/creado dentro de los últimos 30 días. Esta acción debería ejecutarse al menos una vez al día, por favor generar un script multiplataformas que dé solución a este requerimiento.**

```python
#./script.py

# put some files in ./sample-files
# or modify the FOLDER_PATH

import os
from os import listdir
from os.path import isfile, join
from datetime import datetime

FOLDER_PATH = "./sample-files"
SECONDS_IN_A_MONTH = 2_592_000

def get_last_modification_time(path):
    try:
        return os.path.getmtime(path)
    except:
        return OSError(f"Couldn't find file {path}")

def get_seconds_old(timestamp):
    return (datetime.now()-datetime.fromtimestamp(timestamp)).seconds

def get_file_paths_from_folder_path(folder_path):
    return [f for f in listdir(folder_path) if isfile(join(folder_path, f))]


def main():
    try:
        files = get_file_paths_from_folder_path(FOLDER_PATH)
    except:
        return OSError(f"Couldn't find folder {FOLDER_PATH}")

    for file_path in files:
        last_modification_timestamp = get_last_modification_time(f"{FOLDER_PATH}/{file_path}")
        seconds_old = get_seconds_old(last_modification_timestamp)
        if seconds_old > SECONDS_IN_A_MONTH:
            os.remove(f"{FOLDER_PATH}/{file_path}")

if __name__ == "__main__":
    main()
```

Este script debe ser configurado para ser corrido una vez al día (depende del sistema operativo), pero por ejemplo usando cron en Linux; agregando lo siguiente al crontab:

```
00 12 * * * /usr/bin/python script.py
```

4. **El equipo de desarrollo requiere desplegar una aplicación desarrollada en un nuevo framework escrito en python, para ello te comparten el repositorio y te das cuenta que la mejor opción para desplegar el servidor es mediante un contenedor usando un servidor web ASGI (ej: Uvicorn). Define el manifiesto de construcción del contenedor (Dockerfile) considerando que la vulnerabilidad de “privilege escalation” se puede mitigar cambiando el usuario que ejecuta el servidor web.**

```
FROM python:<version_usada_en_app>

RUN groupadd -g 1234 customgroup && \
    useradd -m -u 1234 -g customgroup customuser

USER customuser

WORKDIR /app
COPY /app /app
COPY ./requirements.txt /app

RUN pip install -r /app/requirements.txt

EXPOSE 5000
CMD ["uwsgi", "--ini", "/app/wsgi.ini"]
```

5. **Estás solo durante tu turno y observas síntomas de lo que podría ser un problema en el servidor Windows disponible en la nube que aloja un servicio interno. En este momento, detectamos un incremento significativo en el consumo de recursos y el uso de CPU está muy por encima de sus niveles normales. Considerando que hay SLAs establecidos y que el servicio debe mantener la máxima disponibilidad posible, ¿qué acciones tomarías antes de reportar el incidente?**

Ver la posibilidad de escalar horizontalmente el servicio utilizando replicas o verticalmente aumentando los recursos de la VM, de manera en que el servicio aumenta su capacidad y posiblemente reducir la intermitencia por la exigencia de recursos.

Posteriormente, se debe analizar cual el origen del problema, ya sea si se trata de un ataque malicioso con fines de denegación de servicio, o si simplemente es un aumento espontáneo de la carga.

Identificado el problema, se deben tomar medidas acorde, como puede ser el configurar un WAF si es que no existe para reducir la posibilidad de DDOS, agregar wail2ban (fail2ban para windows) si es que están utilizando ataques de fuerza bruta, etc. En caso de ser un aumento de la carga "natural", se puede ver la posibilidad por ejemplo de agregar balanceo de carga o alguna otra solución similar que permita distribuir la carga de manera flexible.
