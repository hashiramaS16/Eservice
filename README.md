# Eservice
E-Services Django
Este proyecto es una plataforma web desarrollada con Django para la gestión de servicios entre empresas y colaboradores. Permite publicar, buscar, asignar y calificar servicios, así como la comunicación en tiempo real mediante chat.

Características principales
Registro y autenticación de usuarios (empresa y colaborador)
Publicación y búsqueda de servicios
Asignación y postulación a servicios
Calificación de servicios
Chat en tiempo real (Django Channels)
Exportación de historial en PDF y Excel
Instalación
Clona el repositorio:
git clone <URL-del-repositorio>
Accede al directorio del proyecto:
cd E-service0.2/E-service/eservice
Instala las dependencias:
pip install -r requirements.txt
Realiza las migraciones:
python manage.py migrate
Ejecuta el servidor de desarrollo:
python manage.py runserver
Dependencias principales
Django
django-allauth
channels
openpyxl
xhtml2pdf
asgiref
Licencia
Este proyecto es solo para fines educativos.
