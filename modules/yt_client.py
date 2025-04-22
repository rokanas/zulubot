# modules/yt_client.py
import os
import yt_dlp
from pathlib import Path

class YTClient:
    def __init__(self):
        # create download directory if nonexistent
        self.download_dir = "downloads"
        Path(self.download_dir).mkdir(exist_ok=True)
        
    def download_from_url(self, url):
        """download audio from youtube url"""
        try:
            # create yt-dlp options
            ydl_options = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'noplaylist': True
            }

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                # download video and return path
                info_dict = ydl.extract_info(url, download=True)
                title = info_dict.get('title', 'Unknown Title')
                file_path = ydl.prepare_filename(info_dict)

            if os.path.exists(file_path):
                print(f"Downloaded: {title}, path: {file_path}")
                return file_path, title
            else:
                print(f"Warning: File not found at {file_path}")
                return None, f"File not downloaded correctly: {file_path}"
    
        except Exception as e:
            print(f"Error downloading from YouTube: {e}")
            return None, str(e)
    
    def download_from_search(self, search_query):
        """search youtube and download first result"""
        try:
            # create yt-dlp search query
            ydl_options = {
                'quiet': True,          # minimal logging
                'extract_flat': True,   # don't download all videos, just fetch urls
                'noplaylist': True,     # avoid playlists
            }

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                # search youtube
                results = ydl.extract_info(f"ytsearch:{search_query}", download=False)
                
                if not results.get('entries'):
                    return None, "No results found for this search query"
                
                # get first video from search results
                first_video = results['entries'][0]
                video_url = first_video['url']
                file_path, title = self.download_from_url(video_url)
            
            return file_path, title
            
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None, str(e)
