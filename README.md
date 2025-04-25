# PEEPS
"Peeps es un sistema de gestión de tareas diseñado para mejorar la organización y eficiencia en tiendas de retail. Permite asignar tareas en tiempo real, enviar notificaciones, registrar tiempos de ejecución, calificar tareas y generar informes de rendimiento. 

---

## Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)  
- [Instalación](#instalación)  
- [Ejecución de la Aplicación](#ejecución-de-la-aplicación)

---

## Requisitos Previos

Antes de comenzar, asegúrate de tener lo siguiente instalado:

- **Python 3.8 o superior**: PEEPS está desarrollado con Django, que requiere Python. Puedes descargarlo desde [python.org](https://www.python.org/downloads/).
- **Git**: Para clonar el repositorio. Descárgalo desde [git-scm.com](https://git-scm.com/).
- (Opcional) **Virtualenv** para la gestión de entornos virtuales.

---

## Instalación

Sigue estos pasos para configurar el proyecto en tu máquina local:

### 1. Clona el repositorio

Abre tu terminal y ejecuta:

```
git clone https://github.com/usuario/PEEPS.git
```
### 2. Navega al directorio del proyecto

```
cd PEEPS

```
### 3. Crea un entorno virtual (opcional pero recomendado)

**En Windows:**

```
python -m venv venv
venv\Scripts\activate
```
**En Linux/MacOS:**

```
python3 -m venv venv
source venv/bin/activate
```

### 4. Instala Django

Como el proyecto no cuenta aún con un archivo requirements.txt, puedes instalar Django manualmente:
```
pip install django
```
## Ejecución de la Aplicación

### 1. Aplica migraciones

```
python manage.py migrate
```

### 2. Ejecuta el servidor de desarrollo

**En Windows:**
```
py manage.py runserver
```
**En Linux/MacOS:**
```
python3 manage.py runserver
```

### 3. Accede a la aplicación
Abre tu navegador web y dirígete a:
```
http://127.0.0.1:8000/
```
¡Ya deberías poder ver la página de inicio de PEEPS!

### Cerrar el Entorno Virtual

Cuando termines de trabajar en el proyecto, puedes cerrar el entorno virtual con:
```
deactivate
```
Esto funciona tanto en Windows como en Linux/MacOS.
