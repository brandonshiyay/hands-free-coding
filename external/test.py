from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import io
import sys


def sample_recognize(local_file_path):
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    # """

    client = speech_v1.SpeechClient()

    # local_file_path = 'test.raw'

    # The language of the supplied audio
    language_code = "en-US"

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 16000

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    response = client.recognize(config, audio)
    with open('/home/brandon/projects/hackuci2020/django/media/output.py', 'w+') as f:
	    for result in response.results:
	        # First alternative is the most probable result
	        alternative = result.alternatives[0]
	        f.write(alternative.transcript)
    print('Done...!')





if __name__ == '__main__':
	if len(sys.argv)!=2:
		print('Wrong numbers of arguments')
	else:
		sample_recognize(sys.argv[1])