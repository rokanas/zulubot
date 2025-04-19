# modules/speech_processor.py
import vosk
import pyaudio
import json
import re

class SpeechProcessor:
    def __init__(self):
        self.model_path = "stt_models/vosk-model-small-en-us-0.15"
        
        # Command keywords
        self.activation_phrases = [
            "zulubot", "zulu but", "zulu bought", "zillow but", "zillow bought"
        ]

        self.submission_phrase = "answer me zulu"
        
        self.termination_phrases = [
            "zulu begone", "zulu be gone", "zulu begun", 
            "zillow begone", "zillow be gone", "zillow begun"
        ]
    
    def transcribe(self, stop_event, callback=None):
        """transcribe speech and trigger callback when complete phrase is detected"""
        try:
            # initialize model
            model = vosk.Model(self.model_path)
            rec = vosk.KaldiRecognizer(model, 16000)
            
            # set up audio stream
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=2048
            )
            
            # processing state
            transcript_buffer = ""
            is_listening = False
            pending_activation = False
            
            print("Listening for activation phrase: 'Zulubot'")
            print("Say 'Zulu begone' at any time to stop")
            
            # main processing loop
            while not stop_event.is_set():
                try:
                    # read audio data
                    data = stream.read(4096)
                    
                    # process complete phrases
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        recognized_text = result.get('text', '').lower()
                        
                        if not recognized_text:
                            continue
                            
                        # always check for termination first
                        if self._contains_any(recognized_text, self.termination_phrases):
                            print("Zulu banished. Stopping...")
                            break
                        
                        # check for activation if not currently transcribing
                        if not is_listening:
                            if self._contains_any(recognized_text, self.activation_phrases):
                                is_listening = True
                                pending_activation = True
                                print(f"Activation detected! Now transcribing...")
                                continue
                        
                        # process text when in listening/transcription mode
                        if is_listening:
                            # handle submission phrase to complete input
                            if self.submission_phrase in recognized_text:
                                # get text stripped of the submission phrase
                                split_text = recognized_text.split(self.submission_phrase, 1)
                                clean_text = split_text[0].strip()
                                
                                # add text to buffer if not empty
                                if clean_text:
                                    transcript_buffer += clean_text + " "
                                
                                # process complete buffer
                                if transcript_buffer.strip():
                                    final_text = transcript_buffer.strip()
                                    print(f"Sending buffer: {final_text}")
                                    # send text to callback if provided
                                    if callback:
                                        callback(final_text)
                                
                                # reset state
                                transcript_buffer = ""
                                is_listening = False
                                pending_activation = False
                                print("Transcript captured and sent.")
                            
                            # regular speech processing
                            else:
                                # filter out activation phrase if needed
                                if pending_activation:
                                    clean_text = self._filter_keywords(recognized_text, self.activation_phrases)
                                    if clean_text:
                                        transcript_buffer += clean_text + " "
                                    pending_activation = False
                                else:
                                    transcript_buffer += recognized_text + " "
                                    print(recognized_text)
                    
                    # also check partial results for commands
                    partial_result = json.loads(rec.PartialResult())
                    if 'partial' in partial_result and partial_result['partial']:
                        partial_text = partial_result['partial'].lower()
                    
                        # check for termination
                        if self._contains_any(partial_text, self.termination_phrases):
                            print("[Partial] Detected termination command")
                            break
                        
                        # check for activation
                        if not is_listening and self._contains_any(partial_text, self.activation_phrases):
                            print("[Partial] Detected activation phrase")
                            is_listening = True
                            pending_activation = True
                
                except IOError as e:
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
            # clean up resources
            try:
                if 'stream' in locals() and stream:
                    stream.stop_stream()
                    stream.close()
                
                if 'p' in locals() and p:
                    p.terminate()
                    
                print("Speech recognition resources cleaned up.")
            except Exception as e:
                print(f"Error during cleanup: {e}")
            
            # signal completion
            stop_event.set()
    
    def _contains_any(self, text, keywords):
        """check if text contains any keywords"""
        return any(keyword in text for keyword in keywords)
    
    def _filter_keywords(self, text, keywords):
        """remove any keywords from text"""
        filtered_text = text
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            filtered_text = pattern.sub("", filtered_text)
        return filtered_text.strip()