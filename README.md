# Zulubot

A multi-purpose discord bot made for Zulu Empire server.

To run locally, install [ffmpeg](https://www.ffmpeg.org/download.html). Be sure to add it to PATH (Windows).

Bot token and API keys are private so request the ```.env```.

## Commands:

```!zulusummon``` to summon zulubot to your voice channel (you must be in one).

```!zulubegone``` to leave the voice channel.

```!zuluask <message>``` to send message to Zulubot, and he will respond in text. If you're in voice channel, Zulubot will also answer out loud.

```!zulucrypto <coin name> || <coin symbol>``` to show live crypto data. Returns top 6 coins by market cap if no coin name / symbol specified.

```!zuluplay <text> || <yt-url>``` to play song from youtube by search or URL (you must be in voice channel). Adds to queue if audio already playing.

```!zulupause``` to pause currently playing audio (including response to ```!zuluask```).

```!zuluresume``` to resume paused playback.

```!zuluskip``` to skip current playback and play next in queue.

```!zuluqueue``` to display pending items in the playback queue.

```!zulustop``` to stop all playback and clear the queue.


### Voice commands (Zulubot must be in voice channel):

*"Zulubot"* to start listening

*"Answer me, Zulu"* to stop listening and submit message

*"Zulu begone"* to leave voice channel

NOTE: Voice commands currenly only work on local mic input.

### Tech-stack:

- **Vosk** for speech-2-text
- **Gemini API** for LLM responses
- **Elevenlabs API** for text-2-speech
- **CoinMarketCap API** for live crypto data
- **yt_dlp** for youtube downloads