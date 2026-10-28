# CareerRadar Backend

> Flask REST API and PostgreSQL database for [CareerRadar](https://github.com/ziza-kariuki/Group4Project_CareerRadar), a job discovery platform.

## Overview

CareerRadar's Phase 1 was a React job explorer that called the Jobicy API directly. This repository holds the Phase 2 backend: a Flask API that lets the frontend search jobs, register and log in users, and save jobs that persist between visits.

## Core Features

- **User authentication:** registration, password sign-in, direct Google sign-in, and logout
- **Job search:** search and filter jobs through our own API, backed by Jobicy
- **Saved jobs:** logged-in users can save, list, and remove jobs
- **Application tracking:** logged-in users can track applications and update their pipeline status
- **Admin reporting:** administrators can review users, applications, and authenticated user activity
- **Validation and errors:** invalid requests are rejected and errors return consistent JSON

## Tech Stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| Language and framework | Python and Flask | REST API |
| Database | PostgreSQL | Stores users, jobs, and saved jobs |
| ORM | SQLAlchemy | Maps Python classes to tables |
| Migrations | Flask-Migrate | Tracks schema changes |
| Serialization | Marshmallow | Validates input and formats output |
| Security | Flask-Bcrypt | Hashes passwords |
| Cross-origin access | Flask-CORS | Lets the React app call the API |

## API Endpoints

| Method | Route | Login required | Purpose |
| --- | --- | --- | --- |
| `GET` | `/` | No | Return API status and registered endpoints as JSON |
| `GET` | `/health` | No | Return API server status as JSON |
| `POST` | `/register` | No | Create an account |
| `POST` | `/login` | No | Sign in using email and password |
| `POST` | `/google-login` | No | Verify a Google identity and sign in |
| `POST` | `/logout` | Yes | End the session |
| `GET` | `/me` | Yes | Return the current user |
| `GET` | `/dashboard` | Yes | Return personal dashboard statistics |
| `GET` | `/dashboard/admin` | Admin | Return platform statistics |
| `GET` | `/dashboard/admin/activity` | Admin | Paginate user activity and application history |
| `GET`, `PUT` | `/profile` | Yes | View or update your career profile |
| `GET`, `POST` | `/alerts` | Yes | List or create job alerts |
| `PUT`, `DELETE` | `/alerts/<id>` | Yes | Update or delete a job alert |
| `GET` | `/notifications` | Yes | List job and account notifications |
| `PATCH` | `/notifications/<id>/read` | Yes | Mark a notification as read |
| `PATCH` | `/notifications/read-all` | Yes | Mark all notifications as read |
| `GET` | `/applications` | Yes | List the current user's applications |
| `POST` | `/applications` | Yes | Track an application for a local job |
| `PUT`, `PATCH` | `/applications/<id>` | Yes | Update an application |
| `DELETE` | `/applications/<id>` | Yes | Remove an application |
| `GET` | `/jobs` | Yes | Search and filter jobs |
| `GET` | `/jobs/search` | Yes | Search jobs by keyword |
| `GET` | `/jobs/<id>` | Yes | Get one job in full |
| `POST` | `/jobs` | Admin | Create a job |
| `PUT`, `PATCH` | `/jobs/<id>` | Admin | Update a job |
| `DELETE` | `/jobs/<id>` | Admin | Delete a job |
| `GET` | `/skills` | No | List the skills catalogue |
| `GET` | `/skills/<id>` | No | Get one skill |
| `POST` | `/skills` | Admin | Add a skill |
| `PUT`, `PATCH` | `/skills/<id>` | Admin | Update a skill |
| `DELETE` | `/skills/<id>` | Admin | Delete a skill |
| `GET` | `/users` | Admin | List users |
| `GET` | `/users/<id>` | Admin | Get one user |
| `POST` | `/users` | Admin | Create a user |
| `PUT`, `PATCH` | `/users/<id>` | Admin | Update a user |
| `DELETE` | `/users/<id>` | Admin | Delete a user |
| `GET`, `PATCH`, `DELETE` | `/users/me` | Yes | Read, update, or delete your own account |
| `GET` | `/saved-jobs` | Yes | List the user's saved jobs |
| `POST` | `/saved-jobs` | Yes | Save a job |
| `DELETE` | `/saved-jobs/<id>` | Yes | Remove a saved job |

Errors are returned as JSON. For example:

```json
{
  "success": false,
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "The requested job could not be found."
  }
}
```

Use `http://127.0.0.1:5000` as the Postman base URL (there is no `/api`
prefix). `GET /skills` requests need no token. Browse and view jobs only after
registering and logging in, then use the issued access token for protected routes.
Mutating jobs, skills, and the `/users` collection requires an administrator
account. Register and sign in to the account that should administer the system,
then use the `promote-admin` command below to grant that account administrator
access.

Register and log in using JSON bodies:

```json
{
  "email": "you@example.com",
  "first_name": "Your",
  "last_name": "Name",
  "password": "a-password-at-least-8-characters"
}
```

Send that body to `POST /register`, then sign in using `email` and `password` at
`POST /login`. The response contains the access token for authenticated requests.
Google sign-in uses the Google Identity Services button in the frontend. Set
the same Google OAuth Web client ID in the backend and frontend environments:

```text
SECRET_KEY=generate-a-long-random-value
JWT_SECRET_KEY=generate-a-different-long-random-value
GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

Set `VITE_GOOGLE_CLIENT_ID` to the same Google OAuth client ID in the frontend
`.env` to display the Google sign-in button. Google validates the user directly;
CareerRadar does not send any additional email or SMS code. Keep backend secrets
unique and random in deployment; do not use development defaults.

Request `/` to get the API status and a JSON list of registered methods and
paths. For example:

```bash
curl "http://127.0.0.1:5000/"
```

The response contains a `message` and an `endpoints` array. Each endpoint
includes its HTTP `method` and URL `path`.

Example authenticated job search:

```bash
curl -H "Authorization: Bearer <access-token>" \
  "http://127.0.0.1:5000/jobs?limit=5"
```

Example authenticated dashboard request:

```bash
curl -H "Authorization: Bearer <access-token>" \
  "http://127.0.0.1:5000/dashboard"
```

## Database Tables

| Table | Purpose |
| --- | --- |
| `users` | User account details |
| `jobs` | Job listings |
| `saved_jobs` | Links users to the jobs they save |
| `applications` | User application pipeline records |
| `user_activity` | Timestamped history of authenticated user actions |

A user can save many jobs, and a job can be saved by many users, so `saved_jobs` connects the two.

## Connect the React frontend

The React app reads and saves jobs through this API and uses it for login,
accounts, and application tracking. Run the backend at `http://127.0.0.1:5000`
and apply the migrations before starting the frontend from
`careerRadar_Frontend`:

```bash
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in the frontend `.env` file if the backend uses another
address. The admin dashboard is available at `/admin` after signing in with an
account whose database role is `ADMIN`; it can also synchronize listings from
Jobicy. Public registration only creates regular accounts.

Authenticated logins, job searches and views, saved-job changes, and application
actions are recorded from the point the activity migration is applied. Records
contain an action, endpoint, timestamp, and limited action details; passwords
and complete request bodies are not stored.

Users can edit account and career details at `/profile`, review saved listings at
`/saved-jobs`, and create keyword/location/job-type alerts at `/alerts`.
Notifications are created for matching new listings when a job synchronization
adds them; they are shown on the alerts page after refresh.

## Project Structure

```text
backend/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   │   ├── user.py
│   │   ├── job.py
│   │   └── saved_job.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── jobs.py
│   │   └── saved_jobs.py
│   ├── services/
│   │   └── jobicy_service.py
│   ├── schemas/
│   └── utils/
├── migrations/
├── tests/
├── config.py
├── requirements.txt
├── run.py
└── .env          (not committed)
```

| Folder or file | Purpose |
| --- | --- |
| `app/__init__.py` | Creates and configures the Flask app |
| `app/extensions.py` | Shared tools such as the database and migration objects |
| `app/models/` | Database models |
| `app/routes/` | API endpoints, grouped by feature |
| `app/services/` | Logic that talks to external services, such as Jobicy |
| `app/schemas/` | Marshmallow validation and serialization |
| `app/utils/` | Small helper functions |
| `migrations/` | Database migration files |
| `tests/` | Tests |
| `config.py` | App and database configuration |
| `run.py` | Starts the development server |

## Getting Started

> Update these commands once the setup is finalised.

```bash
# Clone the repository
git clone https://github.com/<your-username>/<backend-repo>.git
cd <backend-repo>

# Create the project virtual environment
python3 -m venv .venv

# Install dependencies using that environment's interpreter
.venv/bin/python -m pip install -r requirements.txt

# Create the .env file (see below), then apply the migrations
.venv/bin/flask --app migration_app db upgrade

# Start the server
.venv/bin/python run.py
```

The local development server keeps Flask's interactive debugger disabled by
default. Set `FLASK_DEBUG=true` only when debugging locally; do not enable it
for a publicly reachable server.

This repository already includes the `migrations/` directory, so do not run
`flask db init` again. Use `flask --app migration_app db upgrade` to apply the
checked-in migrations to your database. Run this upgrade after every code
update that includes a new migration and before starting or restarting the API.
The API model and database schema must be updated together; for example, an
`UndefinedColumn` error naming `users.phone_number` means the authentication
migration has not yet been applied to the database configured in `.env`.
For Render, set `DATABASE_URL` to the PostgreSQL connection URL attached to the
service. The application also supports `DATABASE_URI`, which takes precedence
when both variables are set.

### Deploying the backend to Render

Configure the Render web service with these values:

| Setting | Value |
| --- | --- |
| Root Directory | `CareerRadar_Backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `sh start.sh` |

Add `DATABASE_URL` using the **Internal Database URL** from the PostgreSQL
database attached to this Render service (the database and web service should
be in the same region). Also set unique, randomly generated `SECRET_KEY` and
`JWT_SECRET_KEY` environment variables; do not use the development defaults.
Remove any stale `DATABASE_URI` setting: when both database variables are set,
the application uses `DATABASE_URI` instead of `DATABASE_URL`.
Keep Render's automatic deploy on push enabled for the branch connected to the
GitHub repository.

`start.sh` runs `python -m flask --app migration_app db upgrade` before launching
Gunicorn. This applies checked-in migrations during each deploy or restart, so
the account tables and columns are present before `/register` or `/login`
receives requests. If the migration fails, Render will show the migration
error in the deploy logs and will not start the API against an out-of-date
schema. Do not use this startup migration against an existing database whose
schema was created manually and is not tracked by Alembic; first verify its
schema and migration version to avoid applying an incompatible migration.

After saving these settings, trigger a manual deploy once. Subsequent pushes
to the connected GitHub branch will deploy automatically. Confirm the deploy
logs show the migration command completing before Gunicorn
starts, then check `https://<your-render-service>.onrender.com/health`.

Use the `.venv/bin/` executables shown above so dependency installation and
server startup use the same Python interpreter. This is especially important
when `python3` is managed by pyenv or another system-level Python selector.

Open `http://127.0.0.1:5000/` in a browser on the same computer. To open it
from another device on the same network, use the server computer's local IP
address instead, for example `http://192.168.1.10:5000/`. Allow inbound
connections to port `5000` in the server computer's firewall if needed. This
development server is intended for local development, not public production
hosting.

## Environment Variables

Create a `.env` file in the project root. It holds secrets, so it must never be committed.

```text
SECRET_KEY=<your-secret-key>
DATABASE_URI=postgresql://<user>:<password>@localhost:5432/<database-name>
```

After registering the account that should administer the system, run the command
from this backend directory and enter the exact email used for that account:

```bash
./.venv/bin/flask --app run.py promote-admin "martin12@gmail.com"
```

Confirm the promotion when prompted, then sign out and sign back in so the
frontend loads the updated role. Only trusted operators with access to the
backend environment should run this command. Public account registration
continues to create regular users.

Migrations use the dedicated migration app so loading the CLI does not require
importing the API route modules:

```bash
flask --app migration_app db upgrade
```

## Data Source

Job listings are stored in the backend database. Public `GET /jobs` requests
automatically fill or refresh the local cache from the
[Jobicy Remote Jobs API](https://jobicy.com/jobs-rss-feed) when it is empty or
older than 15 minutes. A keyword search with no local matches is also sent to
Jobicy and the returned results are saved for application tracking.
Administrators can manually synchronize listings using the admin dashboard or
`POST /jobs/sync`.

## Project Team

- **Gabriel Cosmas**: Services folder, skills.py, users.py
- **Okech Martin**: alerts.py, applications.py, auth.py, career.py, dashboard.py, jobs.py, matches.py, profile.py
- **Edwin Lude**: application.py, career_goal.py, education.py, experience.py, job.py
- **Teddy Learamo**: All database schema/relationships
- **Ziza Kariuki**: job_alert.py, notification.py, profile.py, saved_job.py, skill.py, user.py



./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python run.py
.venv/bin/python -m flask --app migration_app db upgrade
