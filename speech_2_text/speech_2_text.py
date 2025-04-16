import vosk
import pyaudio
import json
import time
import threading

def transcribe(stop_event, callback=None):
    # set model path
    # download models from https://alphacephei.com/vosk/models
    model_path = "speech_2_text/models/vosk-model-small-en-us-0.15"

    try:
        # initialize model using path
        model = vosk.Model(model_path)

         # alternatively download path directly during runtime
        # haven't tried this yet, don't want to accidentally download the 1.8GB one into some obscure cache folder
        # model = vosk.Model(lang="en-us")

        # create speech recognizer (sample rate of 16000 Hz)
        rec = vosk.KaldiRecognizer(model, 16000)

        # open mic stream
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=2048)

        transcript_buffer = ""
        is_transcribing = False
        pending_activation = False  # flag to track if we've seen an activation phrase that needs filtering

        print("Listening for activation phrases: 'Zulubot', 'Zulu but', 'Zulu bought', 'Zillow but', 'Zillow bought'")
        print("Say 'Zulu begone' at any time to stop")

        # termination keywords
        termination_keywords = [
            "zulu begone", 
            "zulu be gone", 
            "zulu begun", 
            "zillow begone", 
            "zillow be gone", 
            "zillow begun"
        ]

        # activation keywords
        activation_keywords = [
            "zulubot", 
            "zulu but", 
            "zulu bought", 
            "zillow but", 
            "zillow bought"
        ]

        # start streaming and recognize speech
        while not stop_event.is_set():
            try:
                data = stream.read(4096)        # read in chunks of 4096 bytes
                if rec.AcceptWaveform(data):    # accept waveform of input voice
                    
                    # parse JSON result and get recognized text
                    result = json.loads(rec.Result())
                    recognized_text = result['text']

                    if recognized_text:
                        lower_text = recognized_text.lower()
                        
                        # always check for termination keywords first, regardless of state
                        if any(keyword in lower_text for keyword in termination_keywords):
                            print("Zulu banished. Stopping...")
                            break
                        
                        # check for activation phrase if not currently transcribing
                        if not is_transcribing:
                            for keyword in activation_keywords:
                                if keyword in lower_text:
                                    is_transcribing = True
                                    print(f"Activation phrase '{keyword}' detected! Now transcribing...")
                                    pending_activation = True
                                    break
                            if is_transcribing:
                                continue  # skip activation phrase from being transcribed
                        
                        # Only process text if we're in transcribing mode
                        if is_transcribing:
                            # handle zulu over command
                            if "zulu over" in lower_text:
                                # extract text before "zulu over"
                                text_parts = lower_text.split("zulu over", 1)
                                before_over = text_parts[0].strip()
                                
                                # add text before "zulu over" to buffer
                                if before_over:
                                    transcript_buffer += before_over + " "
                                
                                # process complete buffer
                                if transcript_buffer.strip():
                                    print(f"Sending buffer: {transcript_buffer.strip()}")
                                    if callback:
                                        callback(transcript_buffer.strip())
                                
                                # reset buffer and stop transcribing
                                transcript_buffer = ""
                                is_transcribing = False
                                pending_activation = False
                                print("Transcript sent. Listening for activation phrases again.")
                            
                            # regular speech (not containing commands) - only process if transcribing
                            else:
                                # if ther eis pending activation phrase, filter it out
                                if pending_activation:
                                    # check if any activation keyword is in text and remove it
                                    clean_text = recognized_text
                                    for keyword in activation_keywords:
                                        if keyword.lower() in lower_text:
                                            # remove keyword (case-insensitive)
                                            import re
                                            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                                            clean_text = pattern.sub("", clean_text).strip()
                                    
                                    # only add non-empty text after filtering
                                    if clean_text:
                                        print(f"Filtered text: {clean_text}")
                                        transcript_buffer += clean_text + " "
                                    
                                    # reset the pending flag
                                    pending_activation = False
                                else:
                                    # process normal text
                                    print(recognized_text)
                                    transcript_buffer += recognized_text + " "
                
                # also process partial results to get more real-time responses
                partial_result = json.loads(rec.PartialResult())
                if 'partial' in partial_result and partial_result['partial']:
                    partial_text = partial_result['partial'].lower()
                    
                    # always check for termination keywords in partial results
                    if any(keyword in partial_text for keyword in termination_keywords):
                        print("[Partial] Detected termination command")
                        break
                    
                    # check for activation phrase in partial results when not transcribing
                    if not is_transcribing:
                        if any(keyword in partial_text for keyword in activation_keywords):
                            print("[Partial] Detected activation phrase")
                            is_transcribing = True
                            pending_activation = True
                            continue
                    
                    # check for "zulu over" in partial results when transcribing
                    if is_transcribing and "zulu over" in partial_text:
                        print(f"[Partial] Detected 'zulu over' command")
            
            except IOError as e:
                # handle potential buffer overflows or other stream errors
                if "Input overflowed" in str(e):
                    print("Warning: Input buffer overflow. Continuing...")
                    continue
                else:
                    print(f"Error reading from stream: {e}")
                    break
            
            except Exception as e:
                print(f"Unexpected error in speech recognition: {e}")
                break

    except Exception as e:
        print(f"Error initializing speech recognition: {e}")
    
    finally:
        # ensure cleanup even if exceptions occur
        try:
            if 'stream' in locals() and stream:
                stream.stop_stream()
                stream.close()
            
            if 'p' in locals() and p:
                p.terminate()
                
            print("Speech recognition resources cleaned up.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        # set event so external code also knows it's done
        stop_event.set()