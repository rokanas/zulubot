import os
import asyncio
import discord
import shutil
from pathlib import Path    

class AudioPlayer:
    def __init__(self, server_id=None, text_channel=None): 
        self.server_id = server_id      # optional for use in other servers
        self.queue = []
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.download_dir = "downloads"
        self.text_channel = text_channel
    
    async def play(self, ctx, source, title, is_stream=False, text_callback=None):
        """play an audio file from filepath or stream url"""
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            # add audio to queue if already playing
            self.queue.append((source, title, is_stream, text_callback))
            return f"Added to de queue [position {len(self.queue)}]: {title}"

        try:
            if is_stream:
                # stream options for urls
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'  # disable video
                }
                # create audio source from stream url with ffmpeg
                audio_source = discord.FFmpegPCMAudio(source, **ffmpeg_options)

                # volume control (to bring in line with speech volume)
                audio_source = discord.PCMVolumeTransformer(audio_source, volume=0.5)

            else:
                # create ffmpeg audio source from download filepath
                audio_source = discord.FFmpegPCMAudio(source)
            
            # play audio with _song_finished callback
            voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self._song_finished(e, ctx), voice_client.loop))
            
            self.is_playing = True
            self.is_paused = False
            self.current_track = (source, title, is_stream, text_callback)

            # execute text callback immediately if audio starts playing now
            if text_callback:
                await text_callback()
            
            return f"▶️ Now playing: {title}"
            
        except Exception as e:
            print(f"Error playing audio: {e}")
            return f"Error playing: {str(e)}"
    
    async def pause(self, voice_client):
        """pause current playback"""
        if voice_client and voice_client.is_playing() and not self.is_paused:
            voice_client.pause()
            self.is_paused = True
            return "⏸️ De Zulu has paused de playback."
        elif voice_client and self.is_paused:
            return "⏸️ De playback is already paused."
        return "How can de Zulu pause when notting is playing?"
    
    async def resume(self, voice_client):
        """resume paused playback"""
        if voice_client and not voice_client.is_playing() and self.is_paused:
            voice_client.resume()
            self.is_paused = False
            return "▶️ De Zulu has resumed de playback."
        return "How can de Zulu resume when notting is playing?"
    
    async def skip(self, voice_client):
        """skip to next track in queue"""
        if len(self.queue) == 0:
            if voice_client.is_playing() or self.is_paused:
                voice_client.stop()
                return "De Zulu has skipped de current track. No mo tracks left in de queue."
            return "How can de Zulu skip de current track when notting is playing and de queue is empty?"
            
        # stop current track
        if voice_client.is_playing() or self.is_paused:
            voice_client.stop()
            return "⏭️ De Zulu is skipping to de next track..."
        else:
            # if nothing playing but queue has items, play next item
            await self._play_next(voice_client)
            return f"▶️ Now playing: {self.current_track[1]}"

    async def get_queue(self):
        """get formatted queue status message"""
        if not self.current_track and not self.queue:
            return "Der are no tracks in de queue."
            
        status = []
        
        if self.current_track:
            status.append(f"▶️ **Now Playing:** {self.current_track[1]}")
            
        if self.queue:
            status.append("\n**Queue:**")
            for i, (_, title, _) in enumerate(self.queue, 1):
                status.append(f"{i}. {title}")
        else:
            status.append("\nDer are no mo tracks in de queue.")
            
        return "\n".join(status)

    async def stop(self, voice_client):
        """stop playback and clear queue"""
        if voice_client and (voice_client.is_playing() or self.is_paused):
            voice_client.stop()
            self.queue = []
            self.is_playing = False
            self.is_paused = False
            self.current_track = None

            # give some time for processes to clean up
            await asyncio.sleep(0.5)
            
            return "⏹️ De Zulu has stopped de playback and cleared de queue."
        elif len(self.queue) > 0:
            self.queue = []
            return "De Zulu has cleared de queue."
        return "How can de Zulu stop when notting is playing?"
    
        # stopping also triggers _song_finished callback

    async def _song_finished(self, error, ctx):
        """called when audio file finishes playing"""
        if error:
            print(f"Error in playback: {error}")

        finished_track = self.current_track
        
        self.current_track = None
        self.is_playing = False
        self.is_paused = False      

        # check if finished track was file that needs cleanup
        if finished_track and not finished_track[2]:  # if not a stream
            await self.cleanup()
        
        # play next song in queue if any
        if self.queue and len(self.queue) > 0:
            await self._play_next(ctx)

    async def _play_next(self, ctx):
        """play next item in queue"""
        if not self.queue:
            return
            
        next_item = self.queue.pop(0)
        source_url, title, is_stream, text_callback = next_item
        
        try:
            # send message to text channel from callback (callback messages need to be explicitly sent back)
            await ctx.send(f"▶️ Now Playing: {title}") 

            await self.play(ctx, source_url, title, is_stream, text_callback)
        
        except Exception as e:
            print(f"Error playing next track: {e}")
            # try to play next track in queue if this one fails
            if self.queue:
                await self._play_next(ctx.voice_client)
    
    async def cleanup(self):
        """delete all downloaded files"""
        try:
            # add short delay to allow ffmpeg to release file handles
            await asyncio.sleep(2)

            # get current file path if track is playing
            current_file = None
            if self.current_track and not self.current_track[2]: # if a file, not a stream
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