# MST Email Automation

A secure Flask-based email automation dashboard with OTP login. Easily manage recipients, reuse email templates, personalize messages using {name} & [text]{link}, and send formatted HTML emails with branded signatures. Built for speed, clarity, and marketing teams.

## Features

- Secure OTP-based login system
- Client management (add, edit, delete)
- Email template management
- Personalized email sending with variable substitution
- HTML email support with signatures
- Support for multiple email accounts (HomeSchool Asia and Kung Fu Quiz)

## Deployment to Railway

This application is configured for easy deployment to Railway with SQLite database support.

### Prerequisites

1. A [Railway](https://railway.app/) account
2. A GitHub repository with your code

### Deployment Steps

1. **Push your code to GitHub**
   - Create a new repository on GitHub
   - Push your code to the repository

2. **Create a new project on Railway**
   - Log in to Railway
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if prompted
   - Select your repository

3. **Set up environment variables**
   - In your Railway project dashboard, go to the "Variables" tab
   - Add the following variables:
     - `SECRET_KEY`: A secure random string
     - `HSA_EMAIL`: Email address for HomeSchool Asia
     - `HSA_PASSWORD`: Password for HomeSchool Asia email
     - `HSA_DISPLAY_NAME`: Display name for HomeSchool Asia
     - `KFQ_EMAIL`: Email address for Kung Fu Quiz
     - `KFQ_PASSWORD`: Password for Kung Fu Quiz email
     - `KFQ_DISPLAY_NAME`: Display name for Kung Fu Quiz

4. **Set up persistent storage for SQLite**
   - In your project dashboard, go to the "Volumes" tab
   - Click "Add Volume"
   - Set the mount path to `/data`
   - Give it a name like "sqlite-data"
   - Set an appropriate size (1GB should be plenty)

5. **Deploy your application**
   - Railway will automatically build and deploy your application
   - You can view the deployment logs in the "Deployments" tab

6. **Access your application**
   - Once deployed, click on the "Settings" tab
   - Find your application URL under "Domains"
   - Your application is now live!

## Local Development

To run this application locally:

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Initialize the SQLite database:
   ```
   python init_db.py
   ```

3. Run the application:
   ```
   python app.py
   ```

4. Access the application at http://localhost:5002
