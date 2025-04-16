import vosk
import pyaudio
import json

def transcribe(stop_event):
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

    # open text file in write mode
    with open(output_file_path, "w") as output_file:
        print("Listening for speech. Say 'Zulu begone' to stop.")

        # start streaming and recognize speech
        while not stop_event.is_set():
            data = stream.read(4096)        # read in chunks of 4096 bytes
            if rec.AcceptWaveform(data):    # accept waveform of input voice

                # parse JSON result and get recognized text
                result = json.loads(rec.Result())
                recognized_text = result['text']
                
                # write recognized text to file
                output_file.write(recognized_text + "\n")
                print(recognized_text)
                
                # check for the termination keyword            
                if any(keyword in recognized_text.lower() for keyword in ["zulu begone", "zulu be gone", "zulu begun"]):
                    print("Zulu banished. Stopping...")
                    break

    # stop and close stream
    stream.stop_stream()
    stream.close()

    # terminate pyaudio object
    p.terminate()

    # set event so external code also knows it's done
    stop_event.set()