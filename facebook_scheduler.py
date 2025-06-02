import os
import time
import logging
import mimetypes
import facebook
import requests
from datetime import datetime
from pathlib import Path
from config import (
    FACEBOOK_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID,
    FACEBOOK_API_VERSION,
    POSTS_DIR,
    STORIES_DIR,
    POSTED_DIR,
    POST_DELAY,
    SUPPORTED_EXTENSIONS,
    POSTING_TIMES,
    STORY_TIMES,
    MAX_POSTS_PER_DAY,
    MAX_STORIES_PER_DAY,
    DEFAULT_POST_MESSAGE,
    DEFAULT_STORY_MESSAGE
)

def post_photo_story(page_id, page_access_token, photo_path):
    graph = facebook.GraphAPI(access_token=page_access_token, version=FACEBOOK_API_VERSION)
    # 1. Upload photo (not published)
    with open(photo_path, "rb") as photo_file:
        photo = graph.put_photo(
            image=photo_file,
            published=False,
            album_path=f"{page_id}/photos"
        )
    photo_id = photo["id"]
    # 2. Publish as story (no scheduled_publish_time)
    story = graph.request(
        f"{page_id}/photo_stories",
        post_args={"photo_id": photo_id},
        method="POST"
    )
    return story

def post_video_story(page_id, page_access_token, video_path):
    # 1. Initialize session
    init_res = requests.post(
        f"https://graph.facebook.com/v{FACEBOOK_API_VERSION}/{page_id}/video_stories",
        params={"access_token": page_access_token},
        data={"upload_phase": "start"}
    )
    init_data = init_res.json()
    video_id = init_data["video_id"]
    upload_url = init_data["upload_url"]

    # 2. Upload video
    file_size = os.path.getsize(video_path)
    with open(video_path, "rb") as f:
        video_data = f.read()
    upload_res = requests.post(
        upload_url,
        headers={
            "offset": "0",
            "file_size": str(file_size)
        },
        data=video_data
    )
    upload_data = upload_res.json()
    if not upload_data.get("success"):
        raise Exception("Video upload failed")

    # 3. Finish upload (publish as story, no scheduled_publish_time)
    finish_res = requests.post(
        f"https://graph.facebook.com/v{FACEBOOK_API_VERSION}/{page_id}/video_stories",
        params={"access_token": page_access_token},
        data={
            "upload_phase": "finish",
            "video_id": video_id
        }
    )
    return finish_res.json()

class FacebookScheduler:
    def __init__(self):
        self.access_token = FACEBOOK_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.graph = facebook.GraphAPI(
            access_token=self.access_token,
            version=FACEBOOK_API_VERSION
        )
        self.posts_today = 0
        self.stories_today = 0
        self.last_reset = datetime.now().date()

    def reset_daily_counts(self):
        """Reset daily post and story counts if it's a new day."""
        current_date = datetime.now().date()
        if current_date > self.last_reset:
            self.posts_today = 0
            self.stories_today = 0
            self.last_reset = current_date

    def is_supported_file(self, file_path):
        """Check if the file extension is supported."""
        ext = file_path.suffix.lower()
        return (ext in SUPPORTED_EXTENSIONS['images'] or 
                ext in SUPPORTED_EXTENSIONS['videos'])

    def get_media_type(self, file_path):
        """Determine if the file is an image or video."""
        ext = file_path.suffix.lower()
        if ext in SUPPORTED_EXTENSIONS['images']:
            return 'image'
        elif ext in SUPPORTED_EXTENSIONS['videos']:
            return 'video'
        return None

    def get_next_posting_time(self, is_story=False):
        """Get the next available posting time."""
        current_time = datetime.now().strftime("%H:%M")
        times = STORY_TIMES if is_story else POSTING_TIMES
        
        for time_str in times:
            if time_str > current_time:
                return time_str
        
        # If no time is available today, return the first time for tomorrow
        return times[0]

    def post_to_facebook(self, file_path, is_story=False):
        """Post content to Facebook Page."""
        try:
            # Reset daily counts if needed
            self.reset_daily_counts()

            # Check daily limits
            if is_story and self.stories_today >= MAX_STORIES_PER_DAY:
                logging.warning("Maximum stories per day reached")
                return False
            elif not is_story and self.posts_today >= MAX_POSTS_PER_DAY:
                logging.warning("Maximum posts per day reached")
                return False

            # Check if file is supported
            if not self.is_supported_file(file_path):
                logging.error(f"Unsupported file type: {file_path}")
                return False

            media_type = self.get_media_type(file_path)
            next_time = self.get_next_posting_time(is_story)
            
            # For stories, use the new API (no scheduling)
            if is_story:
                if media_type == 'image':
                    result = post_photo_story(self.page_id, self.access_token, str(file_path))
                    logging.info(f"Photo story result: {result}")
                elif media_type == 'video':
                    result = post_video_story(self.page_id, self.access_token, str(file_path))
                    logging.info(f"Video story result: {result}")
                else:
                    logging.warning("Unsupported story media type.")
                    return False
                self.stories_today += 1
            else:
                # For regular posts
                if media_type == 'image':
                    # Post photo immediately (no scheduling, for debugging)
                    with open(file_path, 'rb') as media:
                        self.graph.put_photo(
                            image=media,
                            message=DEFAULT_POST_MESSAGE,
                            album_path=f"{self.page_id}/photos",
                            published=True  # Immediate post
                            # scheduled_publish_time removed for debugging
                        )
                    self.posts_today += 1
                    logging.info(f"Photo post published immediately: {file_path.name}")
                elif media_type == 'video':
                    # For videos: post immediately, do NOT use scheduled_publish_time
                    with open(file_path, 'rb') as media:
                        self.graph.put_video(
                            video_file=media,
                            title=DEFAULT_POST_MESSAGE,
                            description=DEFAULT_POST_MESSAGE,
                            album_path=f"{self.page_id}/videos",
                            published=True
                        )
                    self.posts_today += 1
                    logging.info(f"Video post published immediately: {file_path.name}")
                else:
                    logging.warning("Unsupported post media type.")
                    return False

            # Move file to posted directory
            posted_path = POSTED_DIR / file_path.name
            os.rename(file_path, posted_path)
            
            return True

        except facebook.GraphAPIError as fe:
            # Special handling for scheduled_publish_time errors
            if 'scheduled_publish_time can only be specified for page photos' in str(fe):
                logging.error(f"Scheduled publish time error for {file_path}: {str(fe)}. This parameter is only valid for regular page photo posts.")
            else:
                logging.error(f"GraphAPIError posting {file_path}: {str(fe)}")
            return False
        except Exception as e:
            logging.error(f"Error posting {file_path}: {str(e)}")
            return False

    def check_and_schedule_posts(self):
        """Check for new content and schedule posts."""
        # Check posts directory
        for file_path in POSTS_DIR.glob('*'):
            if file_path.is_file():
                self.post_to_facebook(file_path, is_story=False)

        # Check stories directory
        for file_path in STORIES_DIR.glob('*'):
            if file_path.is_file():
                self.post_to_facebook(file_path, is_story=True) 