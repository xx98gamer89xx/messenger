## Descripción 
Messenger es un proyecto educativo con la ambición de algún día ser lanzado al público como servicio auto alojado para grupos de personas pequeños-medianos.
## Componentes 
Este proyecto esta completamente escrito en python, utilizando Flask (para la gestión de las solicitudes http al servidor), pyNaCl (para cifrado asimétrico de extremo a extremo) y sqlite3 (para guardado de mensajes no entregados en servidor y de chats en usuarios).
## Contenido 
Actualmente el proyecto cuenta con 4 scripts de python (cliente y servidor), que cuentan con versión a través de Tor (para máxima privacidad) y con versión de red común, para aumentar la velocidad.
## Características
- Cifrado **end-to-end** con `nacl.public.Box`
- Envío y recepción de mensajes entre usuarios con claves públicas.
- Almacenamiento local con **SQLite3**.
- Conexión anónima mediante **Tor (SOCKS5)**.
- Interfaz de texto simple e intuitiva.
## Requerimientos
- Python3.
- Tor (Solo para la versión que lo usa).
- Sistema operativo Linux (No ha sido probado en otros de momento).
## Uso
1. Clona el repositorio ("git clone https://github.com/xx98gamer89xx/messenger").
2. Cambia la dirección del servidor del script de cliente y configura correctamente los puertos en el servidor (Está planeado añadir un script para que esto sea más sencillo).
3. Crea un entorno virtual ("python -m venv venv", "source venv/bin/activate ") y haz "pip install -r client(_tor)_requeriments.txt" en cliente y "pip install -r server(_tor)_requeriments.txt".
4. Instala tor e inícialo como servicio del sistema si quieres usar esa versión del script (Debian: "sudo apt install tor", Arch:"sudo pacman -S tor").
5. Inicia el script en servidor ("python3 server(_mytor).py") y en cliente ("python3 client(_mytor).py").
7. Utiliza la interfaz.
