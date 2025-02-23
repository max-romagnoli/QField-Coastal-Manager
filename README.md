# QField Coastal Manager

1. **Environment Setup**  
   - Install Docker and Docker Compose.
   - Ensure the `.env` file is in the repository root containing values for:
     ```
     DB_PASSWORD=
     DJANGO_SECRET_KEY=
     DJANGO_DEBUG=False
     DJANGO_SUPERUSER_USERNAME=
     DJANGO_SUPERUSER_EMAIL=
     DJANGO_SUPERUSER_PASSWORD=
     ```

2. **Build and Run**  
   - In the project directory:
     ```
     docker-compose up --build -d
     ```
   - This starts the PostGIS database, Django (Gunicorn), and Nginx containers.  
   - The app will auto-run migrations, create a superuser, and collect static files on startup.

3. **Usage**  
   - The application will by default accessible at `http://localhost` or the server’s IP/domain on port 80.
   - A default superuser is created if it does not exist. Use the credentials defined in `.env`.

4. **Logs and Maintenance**  
   - View logs:
     ```
     docker-compose logs -f
     ```
   - Stop or remove containers:
     ```
     docker-compose down
     ```
   - For data persistence, PostGIS volumes are stored in `postgres_data`; static and media files in `static_data` and `media_data`.

5. **Updating**  
   - Pull changes or modify code, then rebuild and restart:
     ```
     docker-compose up --build -d
     ```