# Zulubot

A multi-purpose discord bot made for Zulu Empire server.

To run locally, install [ffmpeg](https://www.ffmpeg.org/download.html). Be sure to add it to PATH (Windows).

Bot token and API keys are private so request the ```.env```.

## Commands:

```!zulusummon``` to summon Zulubot to your voice channel (you must be in one).

```!zulubegone``` to kick Zulubot from voice channel.

```!zuluask <message>``` to send message to Zulubot, and he will respond in text. If you're in voice channel, Zulubot will also answer out loud.

```!zulusay <message>``` to send message to Zulubot, and he will narrate it in voice channel.

```!zulusetpersona``` to set Zulubot's persona for his spoken answers.

```!zulupersonas``` to display list of available personas.

```!zuluplay <text> || <yt-url>``` to play song from youtube by search term or URL (you must be in voice channel). Adds to queue if audio already playing.

```!zulupause``` to pause currently playing audio (including response to ```!zuluask``` and ```!zulusay```).

```!zuluresume``` to resume paused playback.

```!zuluskip``` to skip current playback and play next in queue.

```!zuluqueue``` to display pending items in the playback queue.

```!zulustop``` to stop all playback and clear the queue.

```!zulucrypto``` to display current top 6 cryptocurrencies by market cap.

```!zulucrypto <coin name> || <coin symbol>``` to display live crypto data of coin specified.

```!zuluhelp``` to display list of valid commands.


### Voice commands (Zulubot must be in voice channel):

*"Zulubot!"* to start listening

*"Answer me, Zulu!"* to stop listening and submit message

*"Zulu, begone!"* to leave voice channel

NOTE: Voice commands currenly only work on local mic input.

### Tech-stack:

- **Vosk** for speech-2-text
- **Gemini API** for LLM responses
- **Elevenlabs API** for text-2-speech
- **CoinMarketCap API** for live crypto data
- **yt_dlp** for youtube downloads