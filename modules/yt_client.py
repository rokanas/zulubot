# modules/yt_client.py
import os
import shutil
from pathlib import Path
from pytube import YouTube, Search

class YTClient:
    def __init__(self, download_dir="downloads"):
        self.download_dir = download_dir
        self._create_download_dir()
    
    def _create_download_dir(self):
        """create download directory if nonexistent"""
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        
    def download_from_url(self, url):
        """download audio from youtube url"""
        try:
            # create youtube object
            yt = YouTube(url)
            
            # get audio stream (highest quality)
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
            
            if not audio_stream:
                return None, "No audio stream found for this video"
            
            # download audio
            file_path = audio_stream.download(output_path=self.download_dir)
            
            print(f"Downloaded: {yt.title}")
            return file_path, yt.title
        
        except Exception as e:
            print(f"Error downloading from YouTube: {e}")
            return None, str(e)
    
    def download_from_search(self, search_query):
        """search youtube and download first result"""
        try:
            # search youtube
            search_results = Search(search_query)
            
            if not search_results.results:
                return None, "No results found for this search query"
            
            # download first result
            first_video = search_results.results[0]
            file_path, title = self.download_from_url(first_video.watch_url)
        
            return (file_path, title)
            
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None, str(e)
    
    def cleanup(self):
        """delete all downloaded files"""
        try:
            # check if directory exists
            if os.path.exists(self.download_dir):
                # remove all files in directory
                shutil.rmtree(self.download_dir)
                # recreate empty directory
                self._create_download_dir()
                return True
        except Exception as e:
            print(f"Error cleaning up downloads: {e}")
            return False