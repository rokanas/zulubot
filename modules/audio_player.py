import os
import asyncio
import discord
import shutil
from pathlib import Path

class AudioPlayer:
    def __init__(self, guild_id=None):
        self.guild_id = guild_id
        self.queue = []
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.download_dir = "downloads"
    
    async def play_file(self, voice_client, file_path, title):
        """play an audio file"""

        if voice_client.is_playing():
            await self.stop(voice_client)
        
        try:
            # use ffmpeg to play the audio
            audio_source = discord.FFmpegPCMAudio(file_path)
            
            # play audio
            voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self._song_finished(e, file_path, title, False), voice_client.loop))
            
            self.is_playing = True
            self.is_paused = False
            self.current_track = (file_path, title)
            
            return
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            return f"Error playing: {str(e)}", None
        
    async def play_stream(self, voice_client, stream_url, title):
        """play audio directly from stream url"""
        if voice_client.is_playing():
            await self.stop(voice_client)
        
        try:
            # create ffmpeg options for streaming
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'  # disable video
            }
            
            # create audio source from stream url with ffmpeg
            audio_source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
            
            # can add volume control if needed
            # audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.5)
            
            # play audio stream
            voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self._song_finished(e, stream_url, title, True), voice_client.loop))
            
            self.is_playing = True
            self.is_paused = False
            self.current_track = (stream_url, title)
            
            return
            
        except Exception as e:
            print(f"Error streaming audio: {e}")
            return f"Error streaming: {str(e)}", None
    
    async def pause(self, voice_client):
        """pause current playback"""
        if voice_client and voice_client.is_playing() and not self.is_paused:
            voice_client.pause()
            self.is_paused = True
            return "De Zulu has paused de playback."
        elif voice_client and self.is_paused:
            return "De playback is already paused."
        return "Hhow can de Zulu pause when notting is playing?"
    
    async def resume(self, voice_client):
        """resume paused playback"""
        if voice_client and not voice_client.is_playing() and self.is_paused:
            voice_client.resume()
            self.is_paused = False
            return "De Zulu has resumed de playback."
        return "How can de Zulu resume when notting is playing?"
    
    # add command to skip to next track in queue

    async def stop(self, voice_client):
        """stop playback and clear queue"""
        if voice_client and (voice_client.is_playing() or self.is_paused):
            voice_client.stop()
            self.queue = []

            # give some time for processes to clean up
            await asyncio.sleep(0.5)
            
            return "De Zulu has stopped de playback."
        return "How can de Zulu stop when notting is playing?"
    
        # stopping also triggers _song_finished callback

    async def _song_finished(self, error, file_path, title, is_stream=False):
        """called when audio file finishes playing"""
        if error:
            print(f"Error in playback: {error}")
        
        self.is_playing = False
        self.current_track = None
        self.is_paused = False

        if not is_stream:
            # clean up downloaded files when playback finishes
            await self.cleanup()
        
        # play next song in queue if any
        # if self.queue and len(self.queue) > 0:
        #     next_url = self.queue.pop(0)
        #     # implementation for playing next in queue would go here
    
    async def add_to_queue(self, url):
        """add url to queue"""
        self.queue.append(url)
        return f"Added to queue (position {len(self.queue)})"
    
    def get_queue(self):
        """get current queue"""
        return self.queue
    
    async def cleanup(self):
        """delete all downloaded files"""
        try:
            # add short delay to allow ffmpeg to release file handles
            await asyncio.sleep(2)

            # get current file path if track is playing
            current_file = None
            if self.current_track:
                current_file = self.current_track[0]

            # check if directory exists
            if os.path.exists(self.download_dir):
                # delete each individual file except the current one
                for file in os.listdir(self.download_dir):
                    file_path = os.path.join(self.download_dir, file)
                    
                    # skip the file that's currently playing
                    if current_file and file_path == current_file:
                        print(f"Skipping currently playing file: {file_path}")
                        continue
                        
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            print(f"Cleaned up file: {file_path}")
                    except Exception as e:
                        print(f"Error removing file {file_path}: {e}")
                return True
        except Exception as e:
            print(f"Error cleaning up downloads: {e}")
            return False