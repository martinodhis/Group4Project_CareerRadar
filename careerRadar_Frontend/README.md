# CareerRadar

CareerRadar is a React job-discovery prototype that helps people explore remote job listings from the [Jobicy API](https://jobicy.com/jobs-rss-feed).

## Who CareerRadar is for

CareerRadar is designed for people exploring job opportunities or planning their next career move, including:

- University students and recent graduates looking for internships, graduate programmes, or entry-level roles.
- Early-career professionals searching for opportunities that match their skills and experience.
- Career changers exploring a new field and learning what skills employers request.
- Freelancers and experienced professionals interested in remote work or new roles.

The prototype focuses on remote listings. The opportunities shown depend on the coverage provided by Jobicy.

## Current prototype

The current frontend includes:

- A home page with keyword search and recent listings.
- A jobs page with industry, experience-level, and job-type filters.
- Job cards with the available listing details and save controls.
- An About page describing the project.
- Loading, empty-results, and error states for job searches.

The Job Details screen is currently a **UI mockup** with illustrative sample content. It is not yet connected to individual API listings. Saved jobs are held in frontend state and are not persisted between visits.

## Project team

The following contributors are represented in the repository's commit history:

- Gabriel Cosmas
- Okech Martin
- Teddy Learamo
- Ziza Kariuki

## Run locally

```bash
npm install
npm run dev
```

Open the local URL printed by Vite. To create a production build, run:

```bash
npm run build
```

## Google sign-in configuration

Google sign-in requires a Google OAuth 2.0 Web client ID. Set the same client ID
in `careerRadar_Frontend/.env` and `CareerRadar_Backend/.env`:

```text
# careerRadar_Frontend/.env
VITE_GOOGLE_CLIENT_ID=your-google-oauth-client-id

# CareerRadar_Backend/.env
GOOGLE_CLIENT_ID=your-google-oauth-client-id
```

In Google Cloud Console, add the frontend's local or deployed origin to the
OAuth client's authorized JavaScript origins. Restart Vite after changing its
`.env` file. Google sign-in cannot complete until both values match.

## Deploying the frontend to Netlify

The repository root `netlify.toml` configures Netlify to build the Vite app
from `careerRadar_Frontend`, publish its `dist` directory, and route client-side
paths such as `/login` and `/jobs` back to the app.

The Flask API is deployed separately on Render. The repository's root
`netlify.toml` sets `VITE_API_BASE_URL` to
`https://group4project-careerradar-1.onrender.com` for Netlify builds. If you
change the backend URL, update that value and trigger a new deploy. The backend
must allow requests from your Netlify site origin through CORS. Google login
additionally needs `VITE_GOOGLE_CLIENT_ID` in Netlify and the matching
`GOOGLE_CLIENT_ID` on the backend.

Do not set `VITE_API_BASE_URL` to the Netlify site URL: Netlify serves the
frontend, not this Flask API. Without a backend URL, production requests show
an API configuration error instead of attempting to connect to port `5000` on
the frontend host. Local development still defaults to `http://localhost:5000`.

## Data source

The app requests up to 20 remote jobs from `https://jobicy.com/api/v2/remote-jobs` and passes the search term as a tag. The public endpoint does not require an API key. Listings depend on the API and network being available.

## Technology

- React and JavaScript
- React Router
- CSS
- Vite
- Jobicy Remote Jobs API

## Planned work

These are roadmap items, not features of the current prototype:

- Flask REST API and PostgreSQL database
- User accounts and persistent saved jobs
- Application tracking and a personal dashboard
- Skills profiles and skill-gap recommendations

## Project structure
> A React job-discovery prototype for exploring remote job listings from the [Jobicy API](https://jobicy.com/jobs-rss-feed).
<img width="924" height="406" alt="image" src="https://github.com/user-attachments/assets/6feb22de-8c24-4ed5-b9ee-d7250550bf61" />

## Table of Contents

- [Who It's For](#who-its-for)
- [Current Prototype](#current-prototype)
- [Planned Work](#planned-work)
- [Tech Stack](#tech-stack)
- [Data Source](#data-source)
- [Run Locally](#run-locally)
- [How the Project Was Set Up](#how-the-project-was-set-up)
- [Project Structure](#project-structure)
- [Project Team](#project-team)

## Who It's For

CareerRadar is designed for people exploring job opportunities or planning their next career move:

- **Students and recent graduates:** internships, graduate programmes, and entry-level roles
- **Early-career professionals:** roles that match their skills and experience
- **Career changers:** exploring a new field and the skills employers ask for
- **Freelancers and experienced professionals:** remote work and new roles

The prototype focuses on remote listings, so the opportunities shown depend on Jobicy's coverage.

## Current Prototype

- **Home page:** keyword search and recent listings
- **Jobs page:** filters for industry, experience level, and job type
- **Job cards:** available listing details, plus save controls
- **About page:** describes the project
- **Loading, empty-results, and error states** for job searches

> [!NOTE]
> - The **Job Details** screen is a **UI mockup** with sample content. It is not yet connected to individual API listings.
> - **Saved jobs** are held in frontend state and are not kept between visits.

## Planned Work

These are roadmap items, not features of the current prototype:

- [ ] Flask REST API and PostgreSQL database
- [ ] User accounts and persistent saved jobs
- [ ] Application tracking and a personal dashboard
- [ ] Skills profiles and skill-gap recommendations

## Tech Stack

- React and JavaScript
- React Router
- CSS
- Vite
- Jobicy Remote Jobs API

## Data Source

The app requests up to 20 remote jobs from `https://jobicy.com/api/v2/remote-jobs` and passes the search term as a tag. The public endpoint needs no API key. Listings depend on the API and your network being available.

## Run Locally

```bash
git clone https://github.com/ziza-kariuki/Group4Project_CareerRadar.git
cd Group4Project_CareerRadar
npm install
npm run dev
```

Open the local URL printed by Vite. To create a production build:

```bash
npm run build
```

## How the Project Was Set Up

For reference, the project was created with these commands. **You don't need to run them** if you cloned the repo, since `npm install` above already installs everything.

```bash
# Create the Vite + React project
npm create vite@latest

# Add client-side routing
npm install react-router-dom
```

## Project Structure

```text
src/
  components/  Reusable interface components
  pages/       Home, Jobs, Job Details, and About screens
  services/    Job API requests and data formatting
  hooks/       Job-loading state and search behavior
  styles/      Global and page styles
```
<<<<<<< HEAD
=======

## Project Team

- Gabriel Cosmas: Services folder, skills.py, users.py
- Okech Martin: alerts.py, applications.py, auth.py, career.py, dashboard.py, jobs.py, matches.py, profile.py
- Edwin Lude: application.py, career_goal.py, education.py, experience.py, job.py
- Teddy Learamo: All database schema/relationships
- Ziza Kariuki: job_alert.py, notification.py, profile.py, saved_job.py, skill.py, user.py
>>>>>>> 3574aec9a8fdcb01b4293c7d74ad00f492a82c69
