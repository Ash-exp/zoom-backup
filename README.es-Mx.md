# Scripts para respaldo de archivos Zoom en Local y Vimeo

Estos scripts han sido creados para descargar archivos de un conjunto de cuentas de Zoom en una computadora local, subirlos a Vimeo desde zoom y finalmente eliminarlos de Zoom. Los archivos incluídos en el repositorio son:

* **config.json**: Archivo de configuración
* **utils.py**: Archivo de utilería
* **vimeo_uploader.py**: Sube archivos a Vimeo desde Zoom
* **zoom_files_downloader.py**: Descarga archivos desde Zoom
* **zoom_files_delete.py**: Elimina archivos en Zoom

Todos estos Scripts en python se ejecutan de forma individual, excepto utils.py, y la sintaxis de ejecución es similar para todos.

## Pre-requisitos
* python 3.x
* wget (se puede instalar con: `pip wget`)
* Cuenta Pro de Zoom
* Cuenta Pro de Vimeo
* Aplicación Zoom
* Aplicación Vimeo
* Los videos en Zoom deben poder descargarse.

### config.json
Es necesario especificar la siguiente información en este archivo:
* **Zoom access token**
* **Vimeo access token**
* **Vimeo User Id**
* **Vimeo Preset Id**

### Obteniendo el Token JWT de Zoom
Para obtener el Access Token de Zoom, es necesario crear una aplicación JWT en Zoom market place (https://marketplace.zoom.us/). En este link se encuentran los pasos  para crear una aplicación Jwt (https://marketplace.zoom.us/docs/guides/build/jwt-app).
Una vez que se ha creado la aplicación, es necesario copiar el Token JWT en el archivo config.json.

### Obteniendo el Token de Vimeo
Para obtener el Token de Vimeo, es necesario crear una aplicación en Vimeo (https://developer.vimeo.com/apps), después de esto, es necesario generar el Access token desde la misma página. En este link se encuentra información más detallada para hacer esto: https://developer.vimeo.com/api/guides/start.
Una vez que se ha obtenido el Access Token de Vimeo, es necesario copiarlo en el archivo config.json.

### Obteniendo el User Id de Vimeo
Es posible obtener el User Id de Vimeo desde el perfil de la cuenta y copiando la última parte de Url, después de **user**. Por ejemplo, en el perfil con link https://vimeo.com/user123456789, el userId es 123456789.
Una vez obtenido el User Id, es necesario copiarlo en el archivos config.json

### Obteniendo el Vimeo
Es necesario crear un Preset en Vimeo, ya que el script vimeo_uploader, después de subir los videos a Vimeo, les asigna una configuración predefinida.
Para esto, después de crear el preset, es necesario copiarlo desde la url y pegarlo en el archivo config.json. Por ejemplo, si la url del preset es https://vimeo.com/settings/videos/embed_presets/987654321, el preset id es 987654321.

## Descargando archivos de Zoom: zoom_files_downloader
Este script obtiene el Id de todas las cuentas Zoom, posteriormente, utiliza estos Ids para obtener todas las grabaciones de cada una de las cuentas y descargarlos en la computadora local de forma desatendida.
Al igual que todos los demás, este script, puede ejecutarse en dos modos: utilizando un archivo de entrada y utilizando un rango de fechas.
Es necesario instalar el paquete wget de python para ejecutar correctamente este script:

`pip wget`

### Utilizando un archivo de entrada
![Download files using an input file](diagrams/download_files.jpg?raw=true "Download files using an input file")

`python zoom_files_downloader.py --inputfile inputfile.csv  --outputfile outputfile.csv`

Con este modo, es necesario un archivo CSV de entrada. Los registros para este archivo están definidos en utils.CSV_HEADER. Es muy difícil generar este archivo, así que es recomendable utilizar este modo únicamente después de haberlo obtenido por haber ejecutado algun script con modalidad de un rango de fechas.

Es decir, es posible subir los videos a Vimeo utilizando un rango de fechas, y, con el reporte generado por este script, es posible descargarlos a la computadora local, utilizando este reporte como archivo de entrada.

### Utilizando un rango de fechas
![Download files using an input file](diagrams/download_zoom.jpg?raw=true "Download files using an input file")

`python zoom_files_downloader.py --daterange YYYY-mm-dd YYYY-mm-dd  --outputfile outputfile.csv`

Con esta modalidad, es posible descargar los archivos de un conjunto de cuentas Zoom utilizando fechas de inicio y fin. Por ejemplo:

`python zoom_files_downloader.py --daterange 2020-01-01 2020-05-03  --outputfile outputfile.csv`

## Subir archivos a Vimeo desde Zoom: vimeo_uploader
Este script sube los videos de Zoom a Vimeo, además los organiza en carpetas (nombradas igual que la reunión) y les asigna una configuración (preset) predefinida en Vimeo, previamente configurada.

### Utilizando un archivo de entrada
![Upload files using an input file](diagrams/upload_files.jpg?raw=true "Upload videos using an input file")

`python vimeo_uploader.py --inputfile inputfile.csv  --outputfile outputfile.csv`

En esta modalidad, es necesario un archivo de entrada; antes de subir los archivos, el script revisa que estos videos no existan ya en vimeo, entonces, se suben todos los archivos que no se han subido. Una vez que los videos se han subido a Vimeo, y que la transcripción de cada uno de estos ha comenzado, cada uno se mueve a su carpeta correspondiente (si esta no existe, se crea), y se le asigna el preset previamente configurado.
Finalmente, se genera un reporte con el estado del script, que puede usarse para volver a ejecutar el mismo script y, en caso de que algún video no se haya subido, o no se haya terminado de mover su carpeta o no se haya asignado un preset definido, se intenta terminar el proceso.

### Utilizando un rango de fechas
![Upload files using date range](diagrams/upload_zoom.jpg?raw=true "Upload videos using an input file")

`python zoom_files_downloader.py --daterange YYYY-mm-dd YYYY-mm-dd  --outputfile outputfile.csv`

Es posible subir los videos en un rango de fechas desde Zoom a Vimeo. Por ejemplo:

`python vimeo_uploader.py --daterange 2020-01-01 2020-05-03  --outputfile outputfile.csv`

## Delete files from Zoom: zoom_files_delete
Este script permite mover los archivos de Zoom hacia la papelera de reciclaje implementada por Zoom.
Este archivo puede ser generado con los scripts vimeo_uploader.py o zoom_files_downloader.py, así una vez que estos scripts se han ejecutado satisfactoriamente, es posible eliminarlos de la cuenta de Zoom.

### Using file input mode
![Delete files using an input file](diagrams/delete_files.jpg?raw=true "Delete files using an input file")

`python zoom_files_delete.py --inputfile inputfile.csv  --outputfile outputfile.csv`

Con esta modalidad, este script recibe un archivo de entrada, mueve cada uno de los archivos especificados en este, a la papelera de reciclaje de Zoom.

### Using date range mode
![Delete files using date range](diagrams/delete_zoom.jpg?raw=true "Delete files using an input file")

`python zoom_files_delete.py --daterange YYYY-mm-dd YYYY-mm-dd  --outputfile outputfile.csv`

En esta modalidad, los archivos de reuniones en un rango de fechas son movidos a la papelera de reciclaje de Zoom.

`python vimeo_uploader.py --daterange 2020-01-01 2020-05-03  --outputfile outputfile.csv`

##Links de documentación oficial
* https://marketplace.zoom.us/docs/guides
* https://marketplace.zoom.us/docs/api-reference/introduction
* https://marketplace.zoom.us/docs/api-reference/zoom-api/users/users
* https://marketplace.zoom.us/docs/api-reference/zoom-api/meetings/meetings
* https://marketplace.zoom.us/docs/api-reference/zoom-api/cloud-recording/recordingdelete
* https://developer.vimeo.com/api/guides/start
* https://developer.vimeo.com/api/reference/folders
* https://developer.vimeo.com/api/reference/videos#uploads
* https://developer.vimeo.com/api/reference/embed-presets
