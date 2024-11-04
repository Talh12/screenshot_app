import os
import uuid
from datetime import datetime
import pymongo
from minio import Minio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from flask import Flask, render_template, request, redirect, url_for, flash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration for MinIO and MongoDB
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.environ.get('MINIO_BUCKET_NAME', 'screenshots')
MONGO_USERNAME = os.environ.get('MONGO_USERNAME')
MONGO_PASSWORD = os.environ.get('MONGO_PASSWORD')
MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@mongodb.database.svc.cluster.local:27017/website_screenshots?authSource=admin'

# Initialize MinIO and MongoDB clients
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
mongo_client = pymongo.MongoClient(MONGO_URI)
collection = mongo_client['website_screenshots']['screenshots']

# Create MinIO bucket if it doesn't exist
if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
    minio_client.make_bucket(MINIO_BUCKET_NAME)

def get_next_screenshot_filename():
    """Generates a unique screenshot filename using UUID."""
    return f"{uuid.uuid4()}.png"

def take_screenshot(url):
    """Takes a screenshot of the provided URL."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--remote-debugging-port=9222')
    
    # Use direct path to chromedriver
    driver = webdriver.Chrome(options=chrome_options)
    screenshot_filename = get_next_screenshot_filename()
    
    try:
        driver.get(url)
        driver.save_screenshot(screenshot_filename)
        return screenshot_filename
    finally:
        driver.quit()

def upload_to_minio(file_name):
    """Uploads a screenshot to MinIO and returns the file URL."""
    minio_key = f"screenshots/{file_name}"
    minio_client.fput_object(MINIO_BUCKET_NAME, minio_key, file_name)
    os.remove(file_name)  # Delete local copy after upload
    return f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/{minio_key}"

def store_metadata(url, minio_url):
    """Stores metadata for the screenshot in MongoDB."""
    collection.insert_one({"url": url, "minio_url": minio_url, "timestamp": datetime.now()})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/screenshot', methods=['POST'])
def screenshot():
    url = request.form['url']
    screenshot_filename = take_screenshot(url)
    minio_url = upload_to_minio(screenshot_filename)
    
def store_metadata(url, minio_url):
    """Stores metadata for the screenshot in MongoDB."""
    metadata = {
        "url": url,
        "date_time": datetime.now()
    }
    collection.insert_one(metadata)

# Add this new route to view metadata
@app.route('/metadata')
def view_metadata():
    # Retrieve all metadata from MongoDB, sorted by date_time in descending order
    metadata = collection.find({}, {'_id': 0, 'url': 1, 'date_time': 1}).sort('date_time', -1)
    return render_template('metadata.html', metadata=metadata)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)