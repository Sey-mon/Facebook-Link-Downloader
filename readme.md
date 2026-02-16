<<<<<<< HEAD
# Facebook Video Downloader

A Flask-based web application that allows you to download Facebook videos in various quality options.

## Features

- Download Facebook videos in different quality formats
- Simple and intuitive web interface
- Video preview with thumbnail and details
- Multiple quality options

## Deployment to Render

### Step 1: Push to GitHub

Make sure your code is pushed to a GitHub repository:

```bash
git add .
git commit -m "Add Render deployment configuration"
git push
```

### Step 2: Deploy on Render

1. Go to [Render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` configuration
5. Click **"Apply"** to use the blueprint configuration
6. Wait for the deployment to complete (5-10 minutes)

### Alternative: Manual Setup

If you prefer manual configuration:

1. Go to [Render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: facebook-link-downloader
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click **"Create Web Service"**

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd facebook-link-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Technologies Used

- **Flask** - Web framework
- **yt-dlp** - Video downloading library
- **Gunicorn** - Production WSGI server
- **HTML/CSS/JavaScript** - Frontend

## License

MIT License
=======
This is a Facebook Link Downloader
>>>>>>> 46f59c2db2b6273314cf1e38f668cc12773cf515
