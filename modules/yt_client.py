# modules/yt_client.py
import os
import yt_dlp
from pathlib import Path

class YTClient:
    def __init__(self):
        # create download directory if nonexistent
        self.download_dir = "downloads"
        Path(self.download_dir).mkdir(exist_ok=True)

    def get_audio_stream(self, url):
        """extract direct audio stream url from youtube url"""
        try:
            # options to extract audio url
            ydl_options = {
                'format': 'bestaudio/best',
                'quiet': False,         # don't hide logging   
                'noplaylist': True,     # avoid playlists
                'extract_audio': True,  # extract audio only
                'skip_download': True,  # don't download, just get info
            }

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                # extract info without downloading
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get('title', 'Unknown Title')
                
                # get direct stream url
                if 'url' in info_dict:
                    stream_url = info_dict['url']
                else:
                    # handle formats list if direct url not available
                    formats = info_dict.get('formats', [])
                    if formats:
                        # get best audio format
                        audio_formats = [f for f in formats if f.get('acodec') != 'none']
                        if audio_formats:
                            stream_url = audio_formats[0]['url']
                        else:
                            stream_url = formats[0]['url']
                    else:
                        raise Exception("No suitable format found")
                        
                return stream_url, title

        except Exception as e:
            print(f"Error extracting stream URL: {e}")
            return None, str(e)
        
    def search_for_url(self, search_query):
        """search youtube and get stream url for first result"""
        try:
            # create yt-dlp search query
            ydl_options = {
                'quiet': False,         # don't hide logging 
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
                video_url = first_video['url'] if 'url' in first_video else first_video['id']
                
                # ff we only got the id, create full youtube url
                if 'youtube.com' not in video_url and 'youtu.be' not in video_url:
                    video_url = f"https://www.youtube.com/watch?v={video_url}"
                
                # get stream url and title
                stream_url, title = self.get_audio_stream(video_url)
            
            return stream_url, title
            
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None, str(e)
        
    def download_from_url(self, url):
        """legacy method for downloading audio from youtube url"""
        try:
            # create yt-dlp options
            ydl_options = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
                'quiet': False,         # don't hide logging
                'noplaylist': True      # avoid playlists
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
