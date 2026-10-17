![screenshot](images/screenshort.png)


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Single-database configuration for Flask.


CareerRadar Backend: PostgreSQL, Admin, Users, Job Search and JWT Authentication
CareerRadar backend will connect three main parts:
- PostgreSQL — stores users, roles, profiles, saved jobs, applications, skills, and other CareerRadar data.
- Flask API — handles registration, login, permissions, job searches, applications, and requests to the public Jobicy API.
- JWT access tokens — authenticate users when they access protected endpoints, including admin-only endpoints.

One important distinction: Jobicy supplies external job listings. Our PostgreSQL database  store CareerRadar users, their roles, saved jobs, applications, and other personal activity. 
1. Understand the backend architecture
Frontend
React — desktop and mobile

HTTP requests + Bearer token

Flask REST API
Authentication, validation, business logic and permissions

PostgreSQL
Users and activity


Jobicy API
External job listings




2. Prepare PostgreSQL in WSL
Open your WSL Ubuntu terminal.
Step 1 — Check PostgreSQL is running
sudo service postgresql status


If it is stopped:
sudo service postgresql start


Open the PostgreSQL shell:
sudo -u postgres psql


Step 2 — Create a database user and CareerRadar database
At the postgres=# prompt, run the following SQL. Replace the example password with a strong, unique password.
CREATE ROLE career_radar_user
WITH LOGIN PASSWORD 'ReplaceWithAStrongPassword';

CREATE DATABASE career_radar
OWNER career_radar_user;

\l
\du
\q


This creates a dedicated database account for your application. Do not use the PostgreSQL postgres superuser as the Flask application's database account.
Step 3 — Test the database connection
psql -h 127.0.0.1 \
  -U career_radar_user \
  -d career_radar


Enter the password you created. If you see a prompt like this, the connection succeeded:
career_radar=>


Exit with:
\q


If PostgreSQL authentication fails, check your PostgreSQL service, credentials, and pg_hba.conf configuration rather than changing permissions indiscriminately.
3. Configure your Flask backend
From WSL, navigate to your project. For example:
cd ~/CareerRadar/backend


If your project is in another folder, use its actual path.
Check your current files:
find app -maxdepth 3 -type f | sort


Your supplied structure is a good modular layout. Keep one copy of each file; your tree contains duplicate entries such as user.py, skill.py, and users.py/uaers.py. Use these canonical filenames:
- app/models/user.py
- app/models/skill.py
- app/routes/users.py
- app/routes/skills.py
Important: a folder structure alone does not implement authentication or admin access. The following setup assumes Flask, SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, and PostgreSQL. If your files currently use different frameworks or route names, adapt the examples to the actual implementation.
Step 1 — Create and activate a Python virtual environment
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip


If venv is unavailable:
sudo apt update
sudo apt install python3-venv python3-pip


Step 2 — Install the backend dependencies
Check your existing requirements.txt first. The following are the main packages for the architecture described here:
pip install Flask Flask-SQLAlchemy Flask-Migrate \
  Flask-JWT-Extended Flask-Cors \
  "psycopg[binary]" python-dotenv \
  requests email-validator


Save the installed versions:
pip freeze > requirements.txt


Step 3 — Configure your .env file
Open the file:
nano .env


Add settings similar to these:

FLASK_APP=run.py
FLASK_DEBUG=1

DATABASE_URL=postgresql+psycopg://career_radar_user:YOUR_DATABASE_PASSWORD@127.0.0.1:5432/career_radar

JWT_SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
JWT_ACCESS_TOKEN_EXPIRES=3600

JOBICY_API_URL=https://jobicy.com/api/v2/remote-jobs



Generate a strong JWT signing secret in a separate terminal command:
python -c "import secrets; print(secrets.token_hex(32))"


Copy its output into JWT_SECRET_KEY in .env.
Replace YOUR_DATABASE_PASSWORD with your actual PostgreSQL password. If the password contains characters such as @, :, / or #, URL-encode those characters in the connection string.
Protect your environment file:
chmod 600 .env


Ensure .env is included in .gitignore:
.env
.venv/
__pycache__/
*.pyc


Never commit your real database password or JWT signing key to GitHub. Use a separate, strong secret in production.
Step 4 — Connect SQLAlchemy and JWT in app/extensions.py
Your extensions file should initialize the shared objects used by your models and routes:
from flask_sqlalchemy import SQLAlchemyfrom flask_migrate import Migratefrom flask_jwt_extended import JWTManagerdb = SQLAlchemy()migrate = Migrate()jwt = JWTManager()



Your app/__init__.py must create the Flask application, load the configuration, initialize these extensions, import the models, and register your blueprints. For example:
import osfrom flask import Flaskfrom dotenv import load_dotenvfrom app.extensions import db, migrate, jwtload_dotenv()def create_app():    app = Flask(__name__)    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False    app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")    )    db.init_app(app)    migrate.init_app(app, db)    jwt.init_app(app)    # Import models so SQLAlchemy and migrations can discover them.    import app.models.user    # Import the other model modules here as they are implemented.    # Register your blueprints here:    # from app.routes.auth import auth_bp    # app.register_blueprint(auth_bp, url_prefix="/api/auth")    return app



This is a configuration example, not a complete implementation of every endpoint in your application. The blueprint names and registration must match your actual files.
Step 5 — Configure run.py
For the application factory above:
from app import create_appapp = create_app()if __name__ == "__main__":    app.run(host="127.0.0.1", port=5000, debug=True)



Start the development server:
python run.py


Keep the terminal open while testing. Debug mode is for local development only.

4. Create users and admin accounts
CareerRadar should distinguish between an ordinary job seeker and an administrator.
Role	What they should be allowed to do
user	Manage their own profile, search jobs, save jobs, manage applications and view their own dashboard
admin	Access authorized administrative functions, inspect users and roles, and view application and job activity according to your access policy
A user should never be able to make themselves an administrator by submitting "role": "admin" during registration.
Step 1 — Add the role field to your user model
In app/models/user.py, your user model needs the equivalent of these fields:
# Add these fields to your existing SQLAlchemy User model.# Keep your existing imports, primary key and relationships.role = db.Column(    db.String(20),    nullable=False,    default="user",    server_default="user",)is_active = db.Column(    db.Boolean,    nullable=False,    default=True,    server_default=db.true(),)



This snippet assumes your model imports db from app.extensions. Do not create a second User model if you already have one.
Your existing model should also store a unique email address and a password hash, not a plaintext password.
For example, your user model should conceptually contain:
- id
- name
- email
- password_hash
- role
- is_active
- created_at
Step 2 — Create the database migration
If Flask-Migrate is configured correctly, run these commands from the backend directory:
flask --app run.py db init
flask --app run.py db migrate -m "Add user roles and active status"
flask --app run.py db upgrade


Only run db init if you do not already have a migrations/ directory initialized for Flask-Migrate. Since your project already has one, you will normally only need the migration and upgrade commands.
Inspect the migration before applying it. If you already have users, ensure the migration assigns existing accounts the user role safely.
Step 3 — Create a normal user using the registration API
Once your /api/auth/register endpoint has been implemented, you can use curl:
curl -i -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Jobseeker",
    "email": "jane@example.com",
    "password": "Use-A-Strong-Password-123!"
  }'


Your registration handler should:
1. Validate the input.
2. Check that the email is not already registered.
3. Hash the password using a password-hashing algorithm.
4. Assign the role user on the server.
5. Save the account in PostgreSQL.
6. Return a safe user response without the password hash.
The exact JSON response depends on your implementation. A successful registration commonly returns HTTP 201 Created.
Step 4 — Create the first administrator securely
The recommended method is a one-time CLI command that creates or promotes an account using your existing Flask application and SQLAlchemy model. This avoids exposing an unrestricted public admin-creation endpoint.
Create app/create_admin.py:
import getpassfrom sqlalchemy import selectfrom werkzeug.security import generate_password_hashfrom app import create_appfrom app.extensions import dbfrom app.models.user import Userapp = create_app()with app.app_context():    email = input("Admin email: ").strip().lower()    name = input("Admin name: ").strip()    password = getpass.getpass("Admin password: ")    if len(password) < 12:        raise SystemExit("Use a password of at least 12 characters.")    existing = db.session.execute(        select(User).where(User.email == email)    ).scalar_one_or_none()    if existing:        existing.role = "admin"        existing.is_active = True        existing.password_hash = generate_password_hash(password)        print("Existing account promoted to admin and password reset.")    else:        admin = User(            name=name,            email=email,            password_hash=generate_password_hash(password),            role="admin",            is_active=True,



This example assumes your User model has the exact field names shown and that it accepts these constructor arguments. Adjust them to your model if necessary.
Run it:
python -m app.create_admin


Enter the admin email, name, and a strong password when prompted. The password is not echoed to the terminal.
If the account already exists, this example promotes it and resets its password. Only run it when you intentionally want that behavior.

5. Log in and obtain a JWT access token
A JWT access token proves that the caller has authenticated. Your backend must still validate the token and enforce the user's permissions on every protected endpoint.
Step 1 — Send a login request from WSL
Once /api/auth/login is implemented, run:
curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "password": "Use-A-Strong-Password-123!"
  }'


A successful login should return a response similar to this:

{
  "access_token": "eyJ...example-token...",
  "user": {
    "id": 2,
    "name": "Jane Jobseeker",
    "email": "jane@example.com",
    "role": "user"
  }
}



The token above is illustrative, not a real credential. Your backend must issue the actual token.
Step 2 — Save the token in your terminal
If you have jq installed, you can extract the token from the login response and store it in a shell variable:
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"Use-A-Strong-Password-123!"}' \
  | jq -r '.access_token')


Check that a token was returned:
test -n "$TOKEN" && echo "Token received" || echo "Login failed"


If jq is missing:
sudo apt install jq


The shell variable is temporary. It normally disappears when you close the terminal.
Step 3 — Make an authenticated request
For example, if you have implemented GET /api/auth/me:
curl -i http://127.0.0.1:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"


Your Flask route must be protected with @jwt_required(). Without that protection, sending a token does not automatically secure the endpoint.

6. Automatically save the JWT token in Postman
Your JavaScript approach is correct, provided your login endpoint returns an access_token field.

Step 1 — Create a Postman environment
Open Postman, select Environments, and create an environment named CareerRadar Local.
Add these variables:
Variable	Initial value
base_url	http://127.0.0.1:5000
token	Leave empty




Step 2 — Create the Login request
Set the method to POST and the URL to:
{{base_url}}/api/auth/login
Under Body → raw → JSON, enter:
{
  "email": "jane@example.com",
  "password": "Use-A-Strong-Password-123!"
}






Step 3 — Add the automatic token-saving script
Open the Login request's Scripts → Post-response tab (called Tests in some Postman versions).
Paste:

const json = pm.response.json();

if (pm.response.code === 200 && json.access_token) {
    pm.environment.set("token", json.access_token);
    console.log("CareerRadar access token saved.");
} else {
    console.error("Login failed or access_token was not returned.");
}



This saves the token only when the request succeeds with HTTP 200 and the response contains access_token.




Step 4 — Use the saved token
Create a new request to:
{{base_url}}/api/auth/me
Select Authorization → Bearer Token and enter:
{{token}}


Send the request. If the token is valid and the endpoint is implemented, you should receive the authenticated user's details.



Why this works: each time you successfully log in, Postman runs the post-response script and updates the selected environment's token variable. Your other requests can reuse that variable without manually copying the JWT.
If your API returns 201 on login rather than 200, adjust the status check accordingly. Keep tokens out of screenshots, shared collections, and source control.
7. Build an API request collection for CareerRadar
Here is a recommended endpoint structure based on your models and routes. These are proposed endpoint contracts; they will work only after the corresponding Flask routes have been implemented and registered.
Method	Endpoint	Purpose	Access
POST	/api/auth/register	Register a job seeker	Public
POST	/api/auth/login	Authenticate and issue token	Public
GET	/api/auth/me	Return current user details	Authenticated
GET	/api/users	List registered users	Admin
GET	/api/users/2	View user ID 2	Admin or authorized owner
GET	/api/jobs	Search imported/external jobs	Public or authenticated
GET	/api/jobs/123	View a job	According to your policy
GET	/api/jobs/external	Fetch live Jobicy listings	Public or authenticated
POST	/api/jobs/123/save	Save a job	Authenticated
GET	/api/applications	View your own applications	Authenticated
POST	/api/applications	Record an application	Authenticated
GET	/api/users/2/applications	View a user's applications	Admin or authorized owner
GET	/api/dashboard	User dashboard	Authenticated
GET	/api/admin/dashboard	Administrative dashboard	Admin
Use one consistent naming convention in your project. For example, if your existing jobs.py exposes /api/jobs/search, use that instead of creating a duplicate endpoint.
Example: use the token to list users
Once you implement the admin-only GET /api/users route, log in as an administrator and capture that administrator's token:
ADMIN_TOKEN="paste-your-admin-token-here"


Then run:
curl -i http://127.0.0.1:5000/api/users \
  -H "Authorization: Bearer $ADMIN_TOKEN"


The intended result is a JSON list of user records. If you send a normal user's token, the endpoint should return 403 Forbidden.
Do not return password hashes, reset tokens, or other secrets in the user list.
Example: list all users directly from PostgreSQL
You can inspect the database independently of the Flask API.
psql -h 127.0.0.1 -U career_radar_user -d career_radar


At the PostgreSQL prompt:
\dt
\d users

SELECT id, name, email, role, is_active
FROM users
ORDER BY id;


The table might be called user, users, or something else depending on your SQLAlchemy model and naming convention. Use \dt to see its actual name and adjust the query accordingly.
To list administrators:
SELECT id, name, email, role
FROM users
WHERE role = 'admin';


To count accounts by role:
SELECT role, COUNT(*)
FROM users
GROUP BY role
ORDER BY role;


Exit with:
\q


These database queries are useful for verification, but your admin dashboard should access records through authorized API routes rather than connecting directly to PostgreSQL from React.

8. Search Jobicy jobs from the WSL terminal
Your app/services/jobicy_service.py should be responsible for communicating with the external Jobicy API. Your app/routes/jobs.py should expose a CareerRadar endpoint that calls the service.
Jobicy's public API has historically used this endpoint:
https://jobicy.com/api/v2/remote-jobs
You can test the external API directly before integrating it with Flask.
Step 1 — Test Jobicy using curl
curl -sG "https://jobicy.com/api/v2/remote-jobs" \
  --data-urlencode "count=10" \
  -H "Accept: application/json" | jq .


To filter for a particular job category or geographic location, consult the Jobicy API documentation for supported query parameters.
This direct request tests Jobicy, not your own backend. If it succeeds, implement the same request inside jobicy_service.py.
Step 2 — Request jobs through CareerRadar
Once you have registered the relevant route, test your backend:
curl -i "http://127.0.0.1:5000/api/jobs/external"


For authenticated job searches, add the token:
curl -G "http://127.0.0.1:5000/api/jobs/external" \
  --data-urlencode "search=Python" \
  -H "Authorization: Bearer $TOKEN"


The second command assumes your endpoint accepts a search parameter. If it does not, implement that parameter in your Flask route and service.
Step 3 — Decide what to save in PostgreSQL
Your job.py model should distinguish between an external listing and a user's personal activity.
A recommended job record contains:
- id — CareerRadar's internal identifier.
- external_id — Jobicy's listing identifier.
- title — job title.
- company — employer offering the job.
- location — listed location.
- job_url — link to the original job advertisement.
- description — job description, if stored.
- source — for example, Jobicy.
- created_at and updated_at.
Use a unique constraint on the source and external ID combination to prevent duplicate imports.
There are two ways to manage listings:
- Live search: fetch listings from Jobicy whenever a user searches. You may not have a complete local history of those listings.
- Stored job catalogue: synchronize Jobicy listings into PostgreSQL and serve them through CareerRadar. This makes it easier to associate saved jobs, matching scores and application records with stable internal job IDs.
For your planned dashboard, a stored catalogue is usually more useful.

9. View saved jobs, applications, and job-search activity
Your model structure already identifies most of the entities needed for these features. The important part is implementing the relationships and ensuring records belong to the correct user.
Model	Information it should store
user.py	Email, password hash, role and account status
profile.py	Name, contact details, location and professional summary
skill.py	Skill names and descriptions
education.py	Qualifications and institutions
experience.py	Previous employers, positions and dates
career_goal.py	Target roles and career objectives
job.py	Job listing and employer information
saved_job.py	User ID, job ID and saved date
application.py	User ID, job ID, status and application date
match.py	User/job match score and matching information
job_alert.py	User's search criteria and alert preferences
notification.py	Notification type, message and read status
Example: inspect applications
After implementing the models and API routes, an administrator should be able to inspect application activity through an endpoint such as:
curl -i http://127.0.0.1:5000/api/admin/applications \
  -H "Authorization: Bearer $ADMIN_TOKEN"


A normal user should only be able to access their own applications:
curl -i http://127.0.0.1:5000/api/applications \
  -H "Authorization: Bearer $TOKEN"


For a PostgreSQL query, if your application table is named applications and contains the specified columns:
SELECT
    a.id,
    a.user_id,
    u.email,
    a.job_id,
    a.status,
    a.applied_at
FROM applications AS a
JOIN users AS u ON u.id = a.user_id
ORDER BY a.applied_at DESC;


This query assumes that your models use these exact table and column names. Check them with \dt and \d applications before executing it.
Application statuses could include saved, applied, interviewing, offered, rejected, and withdrawn, depending on your application's workflow. Only mark an application as genuinely submitted when you have evidence that submission occurred. Recording that a user clicked an external application link is a separate event.

10. Protect your admin routes
A valid token is not sufficient to grant administrator access. Your Flask backend must verify the authenticated user's role.
For example, add a reusable decorator in app/utils/permissions.py:
from functools import wrapsfrom flask import jsonifyfrom flask_jwt_extended import get_jwt, jwt_requireddef admin_required():    def decorator(view_function):        @wraps(view_function)        @jwt_required()        def wrapper(*args, **kwargs):            claims = get_jwt()            if claims.get("role") != "admin":                return jsonify({                    "error": "Administrator access required"                }), 403            return view_function(*args, **kwargs)        return wrapper    return decorator



This example assumes the login process puts the user's role into the JWT claims. Your token creation and authorization logic must be implemented consistently.
For example, the login handler can include the role in the token:
from flask_jwt_extended import create_access_tokenaccess_token = create_access_token(    identity=str(user.id),    additional_claims={"role": user.role},)



Your login handler must also validate the password hash, reject inactive accounts, and return the token in its JSON response.
Security consideration: a role embedded in a JWT remains there until that token expires. If you promote or demote a user, consider short-lived access tokens plus a current-role check, token revocation or another mechanism to prevent stale privileges from being used.
Your admin endpoints should never rely on a role supplied by a query parameter or request body.

11. Test everything in Postman
After registering the appropriate routes, create a collection named CareerRadar API.
Backend testing checklist
0 of 7

[ ] PostgreSQL connection succeeds.
[ ] A normal user can register and log in.
[ ] Postman saves the JWT token after login.
[ ] GET /api/auth/me returns the authenticated user.
[ ] An admin can list users without seeing password hashes.
[ ] A normal user receives 403 when accessing admin-only endpoints.
[ ] Jobicy listings, saved jobs and application records return expected results.

For each request, verify the HTTP status code and the response body. Also test invalid passwords, expired or missing tokens, duplicate registration, and attempts to access another user's private data.
12. Recommended order for implementing your actual files
Do not try to implement every model and route simultaneously. Build the foundation in this order:
1. Database and extensions
   Configure .env, config.py, app/extensions.py, app/__init__.py and run.py. Confirm that Flask connects to PostgreSQL.
2. Users and authentication
   Implement app/models/user.py, app/routes/auth.py and registration/login schemas. Create a normal user, log in and test JWT authentication.
3. Admin permissions
   Implement app/routes/users.py, the permission decorator and the one-time admin CLI command. Test both admin and normal-user access.
4. Jobicy integration
   Implement app/services/jobicy_service.py, app/models/job.py and app/routes/jobs.py. Test the external API and then your internal endpoint.
5. Job seeker features
   Implement profiles, skills, education, experience, saved jobs, applications, career goals and matching.
6. Dashboard, alerts and notifications
   Add the remaining endpoints, tests and administrative reporting. Verify that users only see data they are authorized to access.
13. What I recommend doing next








