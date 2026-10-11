# FitTrack 🏋️

Aplicación móvil para la gestión de entrenadores personales y sus clientes. Permite al entrenador administrar a sus usuarios, programar sesiones, registrar entrenamientos y hacer seguimiento de asistencia y métricas, todo respaldado por una base de datos relacional y una API REST propia.


## Problema

Los entrenadores personales suelen coordinar horarios, rutinas y asistencia por chat y hojas de cálculo. Eso genera cruces de horarios, clientes que no confirman y poca visibilidad del progreso de cada persona.

## Funcionalidades

**Entrenador**
- Aprobación o rechazo de nuevos usuarios.
- Gestión de clientes, horarios y sesiones.
- Registro de entrenamientos con autocompletado de ejercicios y validación de ventana de tiempo.
- Seguimiento de asistencia y métricas de cada cliente.
- Carga de videos de ejercicios.

**Usuario (cliente)**
- Consulta de horarios y detalle de cada sesión.
- Confirmación de asistencia desde la notificación.
- Foto de perfil y seguimiento de su progreso.

**General**
- Notificaciones push (Expo Push API) para recordatorios y confirmación de asistencia.
- Selector de hora personalizado tipo rueda (`TimePickerModal`).
- Eliminación de cuenta desde la app.
- Roles diferenciados con autenticación segura.

## Modelo de datos

- Tabla `schedules` con los campos `notified`, `user_response` y `attended`, que permiten medir la tasa de confirmación y asistencia por cliente.
- Relación entrenador → usuarios, con estado de aprobación.
- Registro de entrenamientos y métricas asociado a cada usuario.
- Archivos multimedia (fotos y videos) en Cloudinary, con la URL guardada en PostgreSQL.
- 

## Arquitectura

El backend sigue **Clean Architecture**, separando rutas, servicios y acceso a datos:

```
App móvil (React Native + Expo)
        │  HTTPS / JSON
        ▼
API REST (Flask)  →  Servicios  →  Repositorios
        │                              │
        ▼                              ▼
Cloudinary (media)              PostgreSQL (Railway)
```

## Stack

| Capa | Tecnología |
|---|---|
| App móvil | React Native, Expo |
| Backend | Flask, SQLAlchemy |
| Base de datos | PostgreSQL |
| Multimedia | Cloudinary |
| Notificaciones | Expo Push API |
| Despliegue | Railway (API), EAS Build (app) |

## Estructura del proyecto

```
fittrack/
├── backend/        # API REST en Flask
│   ├── app/
│   │   ├── models/
│   │   ├── services/
│   │   └── routes/
│   └── migrations/
├── mobile/         # App React Native + Expo
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   └── services/
│   └── app.json
└── docs/           # Capturas y diagrama ER
```

## Instalación local

**Requisitos:** Python 3.10+, Node 18+, PostgreSQL y la app Expo Go (o un emulador).

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
flask run
```

### App móvil
```bash
cd mobile
npm install
cp .env.example .env
npx expo start
```

## Autor

**Jorge Alejandro Mora**
