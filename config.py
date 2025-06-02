import os
from pathlib import Path
from dotenv import load_dotenv
import facebook

# Load environment variables
load_dotenv()

# Facebook API Configuration
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID')  # Facebook Page ID for posts and stories
FACEBOOK_API_VERSION = "3.1"  # Use a supported version for facebook-sdk

# Directory Configuration
BASE_DIR = Path(__file__).parent
POSTS_DIR = BASE_DIR / 'posts'      # For regular posts
STORIES_DIR = BASE_DIR / 'stories'  # For stories (photo/video)
POSTED_DIR = BASE_DIR / 'posted'    # For processed content

# Create necessary directories
for directory in [POSTS_DIR, STORIES_DIR, POSTED_DIR]:
    directory.mkdir(exist_ok=True)

# Schedule Configuration
POSTING_TIMES = [
    "17:05",  # 9:00 AM post
]

STORY_TIMES = [
    "17:05",  # 10:00 AM story
]

# Post Limits
MAX_POSTS_PER_DAY = 1
MAX_STORIES_PER_DAY = 1

# Supported File Extensions (per API requirements)
SUPPORTED_EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
    'videos': ['.mp4']  # .mp4 recommended for stories
}

# Story Media Requirements (for reference/documentation)
STORY_PHOTO_MAX_SIZE_MB = 4
STORY_VIDEO_MAX_SIZE_MB = 60  # 60 seconds max duration
STORY_VIDEO_MIN_RESOLUTION = (540, 960)
STORY_VIDEO_RECOMMENDED_RESOLUTION = (1080, 1920)

# Scheduler Settings
CHECK_INTERVAL = 60  # seconds between checks
POST_DELAY = 60  # seconds before posting
SCHEDULE_INTERVAL = 1  # hours between checks

# Logging Configuration
LOG_FILE = BASE_DIR / 'scheduler.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Post Configuration
DEFAULT_POST_MESSAGE = ""  # Default message for posts
DEFAULT_STORY_MESSAGE = ""  # Default message for stories

graph = facebook.GraphAPI(access_token=FACEBOOK_ACCESS_TOKEN, version=FACEBOOK_API_VERSION)
with open("posts/chris-barbalis-vazZtmYFgFY-unsplash (1).jpg", "rb") as photo_file:
    result = graph.put_photo(
        image=photo_file,
        message="Test immediate post",
        album_path=f"{FACEBOOK_PAGE_ID}/photos",
        published=True
    )
print(result) 