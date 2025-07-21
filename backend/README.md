# Backend

This is the backend of the Camara Insights project.

## Environment Configuration

The backend now supports both development and production environments. The environment is determined by the `CI_ENV` environment variable.

- **Development**: Set `CI_ENV=development`. The application will use the `.env.development` file, which is configured to use a local SQLite database.
- **Production**: Set `CI_ENV=production`. The application will use the `.env.production` file. You will need to provide the appropriate credentials for your production PostgreSQL database in this file.

If `CI_ENV` is not set, the application will default to the development environment.

To run the application, you can use the following command:

```bash
CI_ENV=development uvicorn app.main:app --reload
```

