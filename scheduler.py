import os
import time
import schedule
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import facebook
from PIL import Image
import mimetypes
from facebook_scheduler import FacebookScheduler
from config import (
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
    SCHEDULE_INTERVAL,
    CHECK_INTERVAL
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# class FacebookScheduler:
#     def __init__(self):
#         self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
#         self.page_id = os.getenv('FACEBOOK_PAGE_ID')
#         self.graph = facebook.GraphAPI(access_token=self.access_token, version='3.1')
        
#         # Create necessary directories if they don't exist
#         self.posts_dir = Path('posts')
#         self.stories_dir = Path('stories')
#         self.posted_dir = Path('posted')
        
#         for directory in [self.posts_dir, self.stories_dir, self.posted_dir]:
#             directory.mkdir(exist_ok=True)

#     def get_media_type(self, file_path):
#         """Determine if the file is an image or video."""
#         mime_type, _ = mimetypes.guess_type(file_path)
#         if mime_type:
#             if mime_type.startswith('image/'):
#                 return 'image'
#             elif mime_type.startswith('video/'):
#                 return 'video'
#         return None

#     def post_to_facebook(self, file_path, is_story=False):
#         """Post content to Facebook."""
#         try:
#             media_type = self.get_media_type(file_path)
#             if not media_type:
#                 logging.error(f"Unsupported file type: {file_path}")
#                 return False

#             with open(file_path, 'rb') as media:
#                 if is_story:
#                     # Post as story
#                     if media_type == 'image':
#                         self.graph.put_photo(
#                             image=media,
#                             message='',
#                             published=False,
#                             scheduled_publish_time=int(time.time()) + 60
#                         )
#                     else:  # video
#                         self.graph.put_video(
#                             video_file=media,
#                             title='',
#                             description='',
#                             published=False,
#                             scheduled_publish_time=int(time.time()) + 60
#                         )
#                 else:
#                     # Post as regular post
#                     if media_type == 'image':
#                         self.graph.put_photo(
#                             image=media,
#                             message='',
#                             published=False,
#                             scheduled_publish_time=int(time.time()) + 60
#                         )
#                     else:  # video
#                         self.graph.put_video(
#                             video_file=media,
#                             title='',
#                             description='',
#                             published=False,
#                             scheduled_publish_time=int(time.time()) + 60
#                         )

#             # Move file to posted directory
#             posted_path = self.posted_dir / file_path.name
#             os.rename(file_path, posted_path)
#             logging.info(f"Successfully scheduled {file_path.name}")
#             return True

#         except Exception as e:
#             logging.error(f"Error posting {file_path}: {str(e)}")
#             return False

#     def check_and_schedule_posts(self):
#         """Check for new content and schedule posts."""
#         # Check posts directory
#         for file_path in self.posts_dir.glob('*'):
#             if file_path.is_file():
#                 self.post_to_facebook(file_path, is_story=False)

#         # Check stories directory
#         for file_path in self.stories_dir.glob('*'):
#             if file_path.is_file():
#                 self.post_to_facebook(file_path, is_story=True)

def main():
    scheduler = FacebookScheduler()
    
    # Schedule the check based on configuration
    schedule.every(SCHEDULE_INTERVAL).hours.do(scheduler.check_and_schedule_posts)
    
    # Initial check
    scheduler.check_and_schedule_posts()
    
    logging.info("Scheduler started. Press Ctrl+C to exit.")
    
    while True:
        schedule.run_pending()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 