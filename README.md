# Zulubot

A discord chatbot made for Zulu Empire server using Vosk (speech-2-text), Gemini (LLM) and Elevenlabs (text-2-speech).

To run locally, install [ffmpeg](https://www.ffmpeg.org/download.html). Be sure to add it to PATH (Windows).

Bot token and API keys are private so request the ```.env```.

Currently only transcribes local mic input for voice commands.

## Commands:

```!zulusummon``` to join voice channel (user must be in voice channel)

```!zuluask <message>``` to submit message (from either text chat or voice chat)

```!zulubegone``` to leave voice channel

```!zulucrypto <coin>``` to return live data on a crypto coin by name or symbol (or top 6 coins by market cap if no coin is provided)


### Voice commands (when Zulubot is in voice channel):

*"Zulubot"* to start listening

*"Answer me, Zulu"* to stop listening and submit message

*"Zulu begone"* to leave voice channel
