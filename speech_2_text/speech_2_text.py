import vosk
import pyaudio
import json
import time

def transcribe(stop_event, callback=None):
    # set model path
    # download models from https://alphacephei.com/vosk/models
    model_path = "speech_2_text/models/vosk-model-small-en-us-0.15"

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
                    frames_per_buffer=8192)

    # set path for output text file
    output_file_path = "speech_2_text/output.txt"

    # def reset_output_file():
    #     with open(output_file_path, "w") as f:
    #         f.write("")

    # # open text file in write mode
    # with open(output_file_path, "w") as output_file:
    #     print("Listening for speech. Say 'Zulu begone' to stop.")

    #     # reset output file
    #     reset_output_file()

    transcript_buffer = ""

    print("Listening for speech. Say 'Zulu begone' to stop.")

    # start streaming and recognize speech
    while not stop_event.is_set():
        data = stream.read(4096)        # read in chunks of 4096 bytes
        if rec.AcceptWaveform(data):    # accept waveform of input voice

            # parse JSON result and get recognized text
            result = json.loads(rec.Result())
            recognized_text = result['text']

            if recognized_text:
                lower_text = recognized_text.lower()

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
                        
                        # # write to file if needed
                        # with open(output_file_path, "w") as f:
                        #     f.write(transcript_buffer.strip() + "\n")
                    
                    # Reset buffer after processing
                    transcript_buffer = ""
                
                # check for termination keyword
                elif any(keyword in lower_text for keyword in ["zulu begone", "zulu be gone", "zulu begun"]):
                    print("Zulu banished. Stopping...")
                    break
                
                # regular speech (not containing commands)
                else:
                    print(recognized_text)
                    transcript_buffer += recognized_text + " "
        
        # also process partial results to get more real-time responses
        # ensures 'zulu over' is detected even if said without sufficient pause
        partial_result = json.loads(rec.PartialResult())
        if 'partial' in partial_result and partial_result['partial']:
            partial_text = partial_result['partial'].lower()
            if "zulu over" in partial_text and transcript_buffer.strip():
                print(f"[Partial] Detected 'zulu over' command")

    # stop and close stream
    stream.stop_stream()
    stream.close()

    # terminate pyaudio object
    p.terminate()

    # set event so external code also knows it's done
    stop_event.set()