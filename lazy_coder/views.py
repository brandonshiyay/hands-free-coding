from __future__ import division
from django.http import HttpResponse
from django.shortcuts import render
from .forms import UploadFileForm
from django.http import HttpResponseRedirect
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud.speech import enums
from google.cloud.speech import types
import io
import os
import re
import sys
import time
import pyaudio
from six.moves import queue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def index(request):
    return render(request, 'index.html')


def test(request):
    return HttpResponse('test')


# upload file to server and redirect user to processing page
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            handle_uploaded_file(f)
            # try to transcript the audio file and redirect based on result
            main(BASE_DIR + '/media/audio.wav')
            return HttpResponseRedirect('/result')
    else:
        form = UploadFileForm()
    return render(request, 'upload_form.html', {'form': form})


def handle_uploaded_file(file):
    with open(BASE_DIR + '/media/audio.wav', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


# result page, outputs the output from transcripts
def result(request):
    f = open(f'{BASE_DIR}/media/output.py', 'r').readlines()
    contents = ''
    for line in f:
        contents += line + '\n'
    return render(request, 'result.html', {'contents': contents})


def failed(request):
    return render(request, 'fail.html')

#
# def recognize(file_path):
#     done = False
#     client = speech_v1.SpeechClient()
#
#     # local_file_path = 'test.raw'
#     # The language of the supplied audio
#     language_code = "en-US"
#
#     # Sample rate in Hertz of the audio data sent
#     sample_rate_hertz = 16000
#
#     # Encoding of audio data sent. This sample sets this explicitly.
#     # This field is optional for FLAC and WAV audio formats.
#     encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
#     config = {
#         "language_code": language_code,
#         "sample_rate_hertz": sample_rate_hertz,
#         "encoding": encoding,
#     }
#     with io.open(file_path, "rb") as f:
#         content = f.read()
#     audio = {"content": content}
#
#     response = client.recognize(config, audio)
#     with open('/home/brandon/projects/hackuci2020/django/media/output.py', 'w+') as f:
#         for result in response.results:
#             # First alternative is the most probable result
#             alternative = result.alternatives[0]
#             f.write(alternative.transcript)
#         done = True
#
#     return done


def about(request):
    return render(request, 'about.html')

def rule(request):
    return render(request, 'rule.html')


def file_to_array(file_name):
    import speech_recognition as sr

    rec = sr.Recognizer()
    rec.pause_threshold = 1.0
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""{
    "type": "service_account",
    "project_id": "utility-heading-266903",
    "private_key_id": "224ac26c49c954cd67bdc6cdcf9dab34423bdb0e",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCfqNiDb7dpKVSN\n1OY9MAzGSCZ2/J8i/XHe3TFOywkFBhoPl4CfYrC/LjkGYpRbBOv8tLOM2XxXnOpA\naE6Nh9DSznayB+yf4wSt+1hWMDbD04uITLccKGZbc+EubSycQPpj17zrUTU31Pwm\n5dWiTA1MijuySmK43s1uTpCJSSDlw+piOhWGAm4AH0/WaGBEq2NR52YG6imJMwPW\nIRaZ5u3rR/8EDBQW2SH0zlpBpFeMh7fMN9e0DZohHZnKbAQ4Gy2IwvqSr/UCf/hs\nP85iGOu4ztBDv1JLreBmXgqkvwI9HTf/pyVvHKufZgU5oJ8BnZeg26582faRa4QX\nyDnrsMTLAgMBAAECggEAKSUBDvYmRPKCuL5JyzDrydlkGDvH4uN/idhk0ZJfM607\n4BLB8dEkDVCjH3MeGkqtagVDVCPj+EwWzhxTSgPbG8hbLEwAfb+qQA/K1wM7ycFl\nbu2eLqJ2plC5khZObcINBNfe9qGJ3maDyJ5oLJf+wV/KPIsQ3+WC+U9Dzi1LTgqD\nZ2UO7t3P2eQV4ZYmmOrd1LWnMuSEGwNAJ3Ier6Yq1ga1QKT+QjfU/HqFzKXQSYDK\nEhMMREUYbTRtXcRCkqGeYl5li3IcIOtaGthhfv5uXEvkx7x4U0cNt8yI5diGf9tt\nNpZPam9E9TdtZRYc7g3Tc+J/fwLIDtNZIUuX0t/78QKBgQDdQLgrlI8U99J3GFmn\nhSBHIbImn3arUrx+BvQJm0DiXDRMIkGKAsXzUggb/RS2ov7FsG958N1xYhvebzfd\nG/SQZ3rEw85qAP/qSOudgxC531/pL0opnlJBxYzhr+zChUOCilX2Fr/TP033zDHQ\nacoQfpX60zcPZ8qRqVkV3UzhIwKBgQC4u9JtVQLGbkSDaLQXJmHLNOZKx4Kqfu1P\n0mKhrlhHP1LTpdafIR/Z2oRc/XYx3IdFCfSPrBjpZas/e9v5iDkXRY7YyYFXyYfF\nKlbt5f2UMn8ezjpQvjkHlT9wAqOG/93BQDYg0+8NJb7qVFLmuMSTGQbaEJV43YPn\nxATtqbcMOQKBgGRjgS0E8wboiy5Odh90X/jmaRbtM8L4f14PeZsCPqZ2f6QrxuD/\n8SE+Dz/jzQoxWrgIHgyOJWvUwCBlBkvk60q6KRIuZfHjEjsTaxTE60nq+HGta1EG\n7Pu6zvl4AU0hekg4zFgkalVHW/EbTV7rISvqw9JTE6CBz3/X/vvUtZVRAoGBALbM\nzQ55Z9SZetyaOFMMHQtrHlNzF17FWOl64zTgg+SEyd47paQzsAPwkrg9676tXYG4\ntzOQddpHS+z3EJbc8LmRkCf/RilreBlnqzugMYx7Z4VBRz1s7pwNWQfq5IyLFpHL\ni4Ryk4PsDP5uUNaUkZiJ1FjmvjIq6QLn2oSfQ04pAoGBAKlvoauCrbREy/RQqj6z\nOU+SalgDTQWp8fvDMHgydYrklqhMzHkbJQvlOztNrQn4zDLS39/ipbgw/QCqv6vP\nxdxIyp9pHand6N05RIuiWtJJ3l4ysN0jd1YVoivWQEzhHXSfntdwpw1dwcYuvDy+\n7x/asCfdQ2Noe7XK5Qn1RuVv\n-----END PRIVATE KEY-----\n",
    "client_email": "tts-792@utility-heading-266903.iam.gserviceaccount.com",
    "client_id": "110267369242481007486",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tts-792%40utility-heading-266903.iam.gserviceaccount.com"
    }
    """
    audioF = file_name
    with sr.AudioFile(audioF) as sourceF:
        audio = rec.record(sourceF)
        data = rec.listen(sourceF)

        print(sourceF.DURATION)
        print(data)
        print("File Reading")

    print("File Text is: ")
    try:
        text = rec.recognize_google(audio)
        print(text)
        text = rec.recognize_google_cloud(audio, GOOGLE_CLOUD_SPEECH_CREDENTIALS)
        print(text)
        a = text.split("cut")
        print(a)
        return a

    except Exception as e:
        print(e)


# Audio recording parameters
RATE = 15500
CHUNK = int(RATE / 10)  # 100ms

tabs = 0
undo_list = []


def listen_print_loop(repo):
    num_chars_printed = 0
    arith_ops = ['+', '-', '*', '/']

    for response in repo:

        final_output = response  # (transcript + overwrite_chars).strip().lower()
        global tabs, undo_list

        print(final_output)
        # Exit recognition if any of the transcribed phrases could be
        # one of our keywords.
        if re.search(r'\b(exit)\b', response, re.I):
            print('Exiting..')
            break

        elif (final_output[0:4] == 'undo'):
            f = open('output.py', 'r')
            lines = f.readlines()
            undo_list.append(lines[-1])
            del lines[-1]
            f = open('output.py', 'w')
            f.writelines(lines)

            f.close()

        elif (final_output[0:4] == 'redo'):
            if len(undo_list) > 0:
                f = open('output.py', 'a+')
                f.write(undo_list[-1])
                undo_list = undo_list[:-1]
                f.close()

        elif (final_output[0:7] == "in main"):
            tabs += 1

            f = open('output.py', 'a+')
            f.write("if __name__ == '__main__':\n")
            f.close()

        elif (final_output[0:15] == 'define function'):
            sign_func(final_output[16:])

        elif (final_output == 'close function'):
            tabs -= 1

            f = open('output.py', 'a+')
            f.write('\n')
            f.close()

        elif (final_output[0:13] == 'call function'):
            call_func(final_output[14:])

        elif (final_output[0:5] == 'print'):
            f = open('output.py', 'a+')

            for i in range(tabs):
                f.write('\t')

            if (final_output[6:14] == 'variable'):
                f.write('print(%s)\n' % '_'.join(final_output[15:].split()))
            else:
                f.write('print("%s")\n' % final_output[6:])

            f.close()

        elif (any(x in final_output for x in arith_ops)):
            sign_arith(final_output)

        else:
            sign_var(final_output)

        num_chars_printed = 0


d = {
    'integer': 'int',
    'string': 'str',
    'float': 'float'
}


def sign_var(input_str):
    try:
        var = re.match('^[a-z A-Z]* (is|equals)', input_str).group(0).split()
        var_type = var[0]
        var_name = '_'.join(var[1:-1])
        r = re.compile('(?:is|equals).*$')
        var_val = ' '.join(re.search(r, input_str).group().split(' ')[1:])

        f = open('output.py', 'a+')

        for i in range(tabs):
            f.write('\t')

        if var_type == 'string':
            f.write('%s = %s("%s")\n' % (var_name.lower(), d[var_type], var_val))
        elif var_type == 'integer' or 'float':
            f.write('%s = %s(%s)\n' % (var_name.lower(), d[var_type], var_val))

        f.close()

    except:
        print('Syntax Error')


def sign_func(input_str):
    try:
        func_sign = re.match('^[a-z A-Z]*(parameter|parameters)', input_str).group(0)
        # print(func_sign)
        func_parameters = re.match('%s(.*)' % func_sign, input_str).group(1)
        r = re.compile('(parameter|parameters).*$')
        func_sign = '_'.join(func_sign.split()[:-1])
        func_parameters = ', '.join(re.search(r, input_str).group().split(' ')[1:])
        global tabs

        f = open('output.py', 'a+')

        for i in range(tabs):
            f.write('\t')

        f.write('def %s(%s):\n' % (func_sign, func_parameters))
        f.close()

        tabs += 1

    except:
        print('Syntax Error')


def call_func(input_str):
    try:
        func_call = input_str.split()
        # print(func_call)
        func_sign = func_call[0]

        if func_call[1] != 'arguments' and func_call[1] != 'argument':
            raise Exception

        func_args = []
        is_variable = False

        for argument in func_call[2:]:
            if argument == 'variable':
                is_variable = True
            elif is_variable == True:
                func_args.append(argument)
                is_variable = False
            else:
                func_args.append(argument)

        func_args = ', '.join(func_args)

        f = open('output.py', 'a+')

        for i in range(tabs):
            f.write('\t')

        f.write('%s(%s)\n' % (func_sign, func_args))

        f.close()

    except:
        print('Syntax Error')


def sign_arith(input_str):
    try:
        str_spl = input_str.split('equals')
        # print(str_spl)

        if len(str_spl[0]) == 0 or any(char.isdigit() for char in str_spl[0]):
            raise Exception

        f = open('output.py', 'a+')

        for i in range(tabs):
            f.write('\t')

        f.write('%s = %s\n' % ('_'.join(str_spl[0].split()), str_spl[1].strip()))
        f.close()
    except:
        print("Syntax Error")


def main(file_name):
    with open('output.py', "w"):
        pass
        # Now, put the transcription responses to use.
        temp = file_to_array(file_name)
        listen_print_loop(temp)
