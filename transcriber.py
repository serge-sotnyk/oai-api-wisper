import argparse
import os
import glob
from openai import OpenAI
import dotenv

dotenv.load_dotenv()


def transcribe_file(client: OpenAI,
                    audio_path: str,
                    user_choice: str) -> str:
    txt_path = audio_path + '.txt'
    if os.path.exists(txt_path):
        print(f'Transcription file {txt_path} already exists.')
        while user_choice not in {'k', 'v', 's', 'o'}:
            if user_choice not in {'k', 'v'}:
                user_choice = input(
                    'Choose an option (sokv): Skip / Overwrite / sKip all / oVerwrite all: '
                ).lower()
                if user_choice in {'s', 'k'}:
                    print('Skipping file.')
                    return user_choice if user_choice == 'k' else ''
                elif user_choice not in {'o', 'v'}:
                    print('Invalid option. Please choose one of the following: s/o/k/v')

    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(model='whisper-1', file=audio_file)
    with open(txt_path, 'w') as txt_file:
        txt_file.write(transcript.text)
    print(f'Transcription saved to {txt_path}')
    return user_choice


def main():
    parser = argparse.ArgumentParser(description='Transcribe audio files using OpenAI.')
    parser.add_argument('paths', nargs='*', help='Paths to audio files or directories.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-o', '--overwrite', action='store_true',
                       help='Overwrite existing transcription files.')
    group.add_argument('-k', '--skip', action='store_true',
                       help='Skip existing transcription files.')
    args = parser.parse_args()

    client = OpenAI()
    user_choice = ''

    for path in args.paths:
        if os.path.isdir(path):
            audio_files = glob.glob(os.path.join(path, '*'))
        else:
            audio_files = [path]

        for audio_file in audio_files:
            user_choice = transcribe_file(client, audio_file, user_choice)
            if user_choice and user_choice.lower() in ['k', 'v']:
                break


if __name__ == '__main__':
    main()
