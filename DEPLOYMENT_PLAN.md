# Deployment Plan for a $0 Budget

This document outlines the plan to deploy the Camara Insights application with a zero-dollar budget, focusing on free-tier services.

## Backend Deployment

The backend is a Python application using FastAPI and SQLAlchemy. We can use the following services for deployment:

*   **Hosting**: We will use [Render](https://render.com/) to host our backend application. Render offers a free tier that includes a PostgreSQL database, which is perfect for our needs. The free tier has limitations, but it should be sufficient for our initial deployment.
*   **Database**: As mentioned, we will use the free PostgreSQL instance provided by Render. This will require us to migrate our database from SQLite to PostgreSQL.
*   **ETL Automation**: We will use [GitHub Actions](https://github.com/features/actions) to automate the ETL process. We can create a workflow that runs on a schedule (e.g., daily) to fetch data from the Camara API and load it into our database.

### Backend Changes:

1.  **Switch to PostgreSQL**:
    *   Add `psycopg2-binary` to `requirements.txt`.
    *   Update the SQLAlchemy database URL in the settings to connect to the PostgreSQL instance on Render.
    *   Update the code to handle the differences between SQLite and PostgreSQL, if any.
2.  **Create a GitHub Actions Workflow**:
    *   Create a new workflow file in `.github/workflows`.
    *   The workflow will have a scheduled trigger.
    *   The workflow will check out the code, install dependencies, and run the ETL script.
    *   We will need to store the database credentials as secrets in the GitHub repository.

## Frontend Deployment

The frontend is a Next.js application. We can use the following service for deployment:

*   **Hosting**: We will use [Vercel](https://vercel.com/) to host our frontend application. Vercel is the company behind Next.js and offers a generous free tier for personal projects.

### Frontend Changes:

1.  **Configure Environment Variables**:
    *   We will need to configure the `NEXT_PUBLIC_API_BASE_URL` environment variable on Vercel to point to our backend application on Render.

## Domain Name

For a completely free solution, we can use the domains provided by Render and Vercel (e.g., `camara-insights.onrender.com` and `camara-insights.vercel.app`). If a custom domain is desired, we would need to purchase one, which would violate our $0 budget.

## Action Plan

1.  Create a new branch for these changes.
2.  Update the backend to use PostgreSQL.
3.  Deploy the backend to Render.
4.  Create the GitHub Actions workflow for the ETL process.
5.  Deploy the frontend to Vercel.
6.  Configure the frontend to communicate with the backend.
7.  Test the entire application.
