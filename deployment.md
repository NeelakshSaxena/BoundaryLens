# BoundaryLens Deployment Guide (Bengaluru Region)

This guide covers how to deploy the BoundaryLens frontend specifically for the **Bengaluru Region** (`frontend_bengaluru`) using Vercel. 

Since the frontend is a purely static web application (HTML, CSS, Vanilla JS + MapLibre), it does not require a build step and can be hosted quickly on Vercel's global edge network.

## Prerequisites
- A [Vercel](https://vercel.com/) account.
- The project code pushed to a GitHub, GitLab, or Bitbucket repository.

## Vercel Deployment Instructions

### 1. Import the Project
1. Log in to your Vercel dashboard.
2. Click on **Add New...** and select **Project**.
3. Under **Import Git Repository**, locate your BoundaryLens repository and click **Import**.

### 2. Configure Project Settings
Once imported, you'll be taken to the **Configure Project** screen. Apply the exact settings shown below:

1. **Project Name**: `BoundaryLens`
2. **Application Preset**: Select **Python** from the dropdown.
3. **Root Directory**: Leave it as `./` (the default).

### 3. Build and Output Settings
Since the project runs as a Python application with a static frontend, the default build settings can be left as is:

- **Build Command**: `Empty` (or `Override` toggled off)
- **Output Directory**: `Empty` (or `Override` toggled off)
- **Install Command**: `Empty` (or `Override` toggled off)

*Vercel will build the Python environment (if required) and serve the frontend statically.*

### 4. Deploy
1. Click the **Deploy** button.
2. Vercel will process the static files and provide you with a live production URL (e.g., `boundarylens-bengaluru.vercel.app`).
3. Open the URL to verify the map loads correctly.

---

## Verifying the Deployment
After deployment, confirm the following:
- The map successfully loads the dark theme base layer.
- The view is strictly locked to the **Bengaluru** bounding box (panning completely outside the region should snap the user back).
- 3D features and popups trigger as expected when interacting with datasets.
