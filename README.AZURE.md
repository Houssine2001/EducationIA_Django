Azure deployment notes for EducationIA (evaluation_project)

What this adds
- A small `requirements-azure.txt` which references your main `requirements.txt` and adds `dnspython`, `whitenoise` and `pymongo`.
- A GitHub Actions workflow `.github/workflows/azure-python-deploy.yml` that installs dependencies, runs `collectstatic` and `migrate`, and deploys to Azure Web App.

Before pushing to GitHub / enabling the workflow
1. Create an Azure Web App (Linux) with Python 3.11 or create an App Service Plan + Web App.
2. In your GitHub repository settings -> Secrets, add two secrets used by the workflow:
   - `AZURE_WEBAPP_PUBLISH_PROFILE` : the publish profile XML from the Azure Web App (get from Azure Portal -> Get publish profile)
   - `AZURE_WEBAPP_NAME` : the name of your web app

3. In the Azure Portal, in your Web App -> Configuration -> Application settings, add the following app settings (environment variables):
   - `MONGO_URI` : your MongoDB Atlas connection string (example: `mongodb+srv://...`).
   - `USE_MONGO` : `1`
   - `DJANGO_SECRET_KEY` : a secure Django SECRET_KEY
   - `DJANGO_DEBUG` : `False`
   - `ALLOWED_HOSTS` : comma-separated hostnames your app will use (for example: `myapp.azurewebsites.net`)

Notes and caveats
- The workflow installs `evaluation_project/requirements-azure.txt`. That file includes `-r requirements.txt` so your existing requirements will be installed first, then the Azure extras are appended.
- DNS SRV resolution for `mongodb+srv://` requires `dnspython` which is why it's added in the azure requirements file.
- If your project relies on heavy ML packages (torch, transformers, whisper, etc.) the GitHub Action install step will take longer and the Azure deployment may take a while. Consider using a smaller runtime or separate service for ML workloads.

If you want, I can also add an Azure Resource Manager (ARM) / Terraform template or a GitHub Action step to automatically set the App Settings using the Azure CLI — but that requires an Azure service principal (credential) in GitHub Secrets.
