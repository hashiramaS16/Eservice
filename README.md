# 🚀 E-Service - Plataforma de Servicios

Una plataforma web moderna desarrollada en Django para conectar empresas con colaboradores profesionales para la prestación de servicios.

## ✨ Características Principales

### 🔐 Sistema de Autenticación
- Registro e inicio de sesión para empresas y colaboradores
- Autenticación con Google OAuth
- Perfiles personalizados con fotos y documentos

### 🏢 Dashboard Empresarial
- Publicación de servicios con categorías y requisitos
- Gestión de postulaciones y asignación de colaboradores
- Sistema de calificación y reseñas
- Historial completo de servicios

### 👥 Dashboard Colaborador
- Búsqueda y postulación a servicios
- Gestión de perfil profesional
- Subida de certificados y hojas de vida
- Historial de trabajos realizados

### 💬 Comunicación en Tiempo Real
- Chat integrado entre empresas y colaboradores
- Notificaciones instantáneas
- Sistema de mensajería avanzado

### 📊 Gestión de Servicios
- Categorización por tipos de servicio
- Sistema de pagos integrado
- Confirmación y finalización de servicios
- Exportación de historiales a PDF

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 4.2+** - Framework web principal
- **Django Channels** - WebSockets para chat en tiempo real
- **Django Allauth** - Autenticación social
- **SQLite** - Base de datos (desarrollo)
- **PostgreSQL** - Base de datos (producción)

### Frontend
- **HTML5** - Estructura semántica
- **CSS3** - Estilos modernos y responsivos
- **JavaScript** - Interactividad y AJAX
- **Bootstrap** - Framework CSS (opcional)

### Herramientas
- **Pillow** - Procesamiento de imágenes
- **ReportLab** - Generación de PDFs
- **Gunicorn** - Servidor WSGI para producción

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/hashiramaS16/Eservice.git
   cd Eservice
   ```

2. **Crea un entorno virtual**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En macOS/Linux:
   source venv/bin/activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   ```bash
   # Crea un archivo .env en la raíz del proyecto
   cp .env.example .env
   # Edita .env con tus configuraciones
   ```

5. **Ejecuta las migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Crea un superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Ejecuta el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

8. **Accede a la aplicación**
   - URL: http://localhost:8000
   - Admin: http://localhost:8000/admin

## ⚙️ Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Django Settings
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True

# Google OAuth (opcional)
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret

# Database (para producción)
DATABASE_URL=tu-url-de-base-de-datos
```

## 📁 Estructura del Proyecto

```
Eservice/
├── eservice/                 # Configuración principal de Django
│   ├── settings.py          # Configuraciones del proyecto
│   ├── urls.py              # URLs principales
│   ├── asgi.py              # Configuración ASGI
│   └── wsgi.py              # Configuración WSGI
├── landing/                 # Aplicación principal
│   ├── models.py            # Modelos de datos
│   ├── views.py             # Vistas y lógica de negocio
│   ├── urls.py              # URLs de la aplicación
│   ├── forms.py             # Formularios personalizados
│   ├── consumers.py         # WebSocket consumers
│   ├── templates/           # Plantillas HTML
│   │   ├── landing/         # Templates de la aplicación
│   │   └── account/         # Templates de autenticación
│   └── static/              # Archivos estáticos
│       └── landing/         # CSS, JS, imágenes
├── media/                   # Archivos subidos por usuarios
├── manage.py                # Script de gestión de Django
├── requirements.txt         # Dependencias del proyecto
├── .gitignore              # Archivos ignorados por Git
└── README.md               # Este archivo
```

## 🔧 Comandos Útiles

### Desarrollo
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Shell de Django
python manage.py shell
```

### Producción
```bash
# Recolectar archivos estáticos
python manage.py collectstatic

# Verificar configuración
python manage.py check --deploy
```

## 🌐 Despliegue

### Opciones Recomendadas

1. **Render.com** (Gratis)
   - Fácil configuración
   - Base de datos PostgreSQL incluida
   - Despliegue automático desde GitHub

2. **Railway.app** (Gratis)
   - Muy sencillo de usar
   - Integración directa con GitHub
   - Base de datos incluida

3. **Heroku** (Pago)
   - Muy estable y confiable
   - Excelente para aplicaciones en producción

### Variables de Entorno para Producción
```env
DEBUG=False
SECRET_KEY=clave-secreta-muy-segura
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/db
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Desarrollado por

**SSDev-code** - Equipo de desarrollo

### Contacto
- 📧 Email: contactos@eservices.com
- 🌐 Sitio web: [E-Services](https://eservices.com)
- 📱 Teléfono: 30000000-000-0

## 🙏 Agradecimientos

- Django Software Foundation
- Comunidad de desarrolladores de Python
- Todos los contribuidores del proyecto

---

**¡Gracias por usar E-Service! 🎉** 