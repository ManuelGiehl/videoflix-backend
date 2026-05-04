## Videoflix Backend (Django + DRF)

Videoflix is a Django REST Framework backend providing:

- **Authentication** with JWT stored in **HttpOnly cookies** (register, activate, login, refresh, logout, password reset)
- **Video API** returning metadata and serving **HLS** manifests and segments
- Background video processing via **RQ** (Redis queue) using **ffmpeg** to create HLS variants and thumbnails

---

## Prerequisites

- **Docker Desktop** (recommended)
- Optional for local (non-Docker) runs:
  - **Python 3.12+**
  - A local or containerized **PostgreSQL** instance
  - A local or containerized **Redis** instance

---

## Step-by-step (recommended): Run everything with Docker

### 1) Clone the repo

```bash
git clone <YOUR_REPO_URL>
cd videoflix_backend
```

### 2) Create `.env` from the template

This project expects a real `.env` file (it is referenced by `docker-compose.yml`).

```bash
copy .env.template .env
```

Now open `.env` and set **at minimum**:

- **DB_NAME**, **DB_USER**, **DB_PASSWORD** (any values are fine for local Docker)
- **SECRET_KEY** (any random string for local use)

Recommended values for local Docker:

- **DB_HOST** must stay `db`
- **REDIS_HOST** must stay `redis`

### 3) Build and start the containers

```bash
docker compose up --build
```

What happens on startup:

- Postgres + Redis containers start
- The `web` container:
  - waits for Postgres (`pg_isready`)
  - runs `collectstatic`, `makemigrations`, `migrate`
  - creates a **Django superuser** from env variables
  - starts an **RQ worker**
  - starts **Gunicorn** on port `8000`

### 4) Verify the backend is running

Open:

- **Backend**: `http://127.0.0.1:8000/`
- **Admin**: `http://127.0.0.1:8000/admin/`

Login with the superuser credentials from `.env`:

- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_PASSWORD`

### 5) (Optional) Configure email sending

If you want real email delivery (activation/password reset), set in `.env`:

- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`
- `FRONTEND_BASE_URL` (used to build activation/reset links)

If you leave email settings empty, the API may still respond successfully, but emails will not be delivered.

---

## Step-by-step (optional): Run backend locally (Python) while DB/Redis run in Docker

This is useful if you want fast iteration without rebuilding the image.

### 1) Start only Postgres + Redis

```bash
docker compose up -d db redis
```

### 2) Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3) Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4) Create your local `.env`

```bash
copy .env.template .env
```

Edit `.env`:

- Set `DB_HOST=127.0.0.1` (or `localhost`) **for local Python runs**
- Keep `DB_PORT=5432`
- Set Redis for local Python runs:
  - `REDIS_LOCATION=redis://127.0.0.1:6379/1`
  - `REDIS_HOST=127.0.0.1`

### 5) Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

### 6) Start an RQ worker (separate terminal)

```bash
python manage.py rqworker default
```

### 7) Ensure ffmpeg is available

Video processing uses `ffmpeg`. If you run locally (not in Docker), ensure `ffmpeg` is installed and on your PATH.

---

## API overview

### Auth (cookie-based JWT)

Base prefix: `/api/`

- `POST /api/register/`
- `GET /api/activate/<uidb64>/<token>/`
- `POST /api/login/`
- `POST /api/token/refresh/`
- `POST /api/logout/`
- `POST /api/password_reset/`
- `POST /api/password_confirm/<uidb64>/<token>/`

Notes:

- JWTs are set as **HttpOnly cookies** (`access_token`, `refresh_token`) on login/refresh.
- For browser-based testing, your frontend must use `credentials: "include"` and be added to CORS/CSRF trusted origins.

### Video API (JWT required)

Base prefix: `/api/video/`

- `GET /api/video/` – list video metadata
- `GET /api/video/<movie_id>/<resolution>/index.m3u8` – HLS manifest
- `GET /api/video/<movie_id>/<resolution>/<segment>` – HLS segment (`.ts`)

---

## Testing locally (quick checklist)

### 1) Login (to receive cookies)

Use a REST client that supports cookies (Postman works).

- Request: `POST http://127.0.0.1:8000/api/login/`
- Body (JSON):

```json
{
  "email": "admin@example.com",
  "password": "adminpassword"
}
```

Expected:

- `200 OK`
- response sets cookies (`access_token`, `refresh_token`)

### 2) List videos

After login (cookies included automatically by Postman):

- Request: `GET http://127.0.0.1:8000/api/video/`

Expected:

- `200 OK`
- JSON array of videos

### 3) Add a video (via Admin)

Open `http://127.0.0.1:8000/admin/` and create:

- a `VideoCategory`
- a `Video` entry with an uploaded `video_file`

After saving:

- RQ should process the video and generate HLS output under `media/hls/<video_id>/...`
- Thumbnails go to `media/thumbnails/`

---

## Troubleshooting

### The backend can’t connect to Postgres (`could not translate host name "db"`)

- When running **Docker**, `DB_HOST=db` is correct.
- When running **locally (Python)**, set `DB_HOST=127.0.0.1` in `.env`.

### CORS/CSRF issues with a local frontend

Add your frontend origin (e.g. `http://127.0.0.1:5501`) to:

- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

Then restart the backend container or the local server.

### Video processing never completes

- Ensure **Redis** is running and the **RQ worker** is running.
  - Docker mode: the container starts `rqworker` automatically.
  - Local mode: start `python manage.py rqworker default` manually.
- Ensure **ffmpeg** is available:
  - Docker image installs `ffmpeg` (see `backend.Dockerfile`)
  - Local mode requires a system installation of `ffmpeg`

