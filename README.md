# Facebook Post and Story Scheduler

This application helps you schedule Facebook posts and stories from local folders. It monitors specified directories for content and automatically posts them according to your schedule.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory with your Facebook API credentials:
```
FACEBOOK_ACCESS_TOKEN=your_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
```

3. Create two folders in the project directory:
   - `posts/` - for regular Facebook posts
   - `stories/` - for Facebook stories

## Usage

1. Place your content in the appropriate folders:
   - Put post content (images/videos) in the `posts/` folder
   - Put story content in the `stories/` folder

2. Run the scheduler:
```bash
python scheduler.py
```

3. The scheduler will automatically detect new content and schedule it according to your settings.

## Features

- Automatically schedules posts and stories from local folders
- Supports both images and videos
- Configurable posting schedule
- Easy to use interface
- Error handling and logging

## Note

Make sure you have the necessary Facebook API permissions and a valid access token with the required scopes:
- `pages_manage_posts`
- `pages_read_engagement`
- `publish_to_groups` 