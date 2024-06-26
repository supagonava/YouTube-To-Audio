from pydub import AudioSegment
from pytube import YouTube
from time import sleep
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import Future

import os
import re
import requests
import shutil
import urllib.parse
import tqdm


def download_mp3_youtube(link_url: str):

    # Validating input url
    try:
        video_url = link_url
        result = urllib.parse.urlparse(video_url)

        # Check if the URL is valid and belongs to YouTube.com
        if result.scheme == "https" and result.netloc == "www.youtube.com" or "youtu.be" in video_url:
            yt = YouTube(video_url)
            title = yt.title

            # Send a request to the URL and check if the video is available
            response = requests.get(video_url)
            if "Video unavailable" in response.text:
                raise ValueError("Video is not available on YouTube")
            else:
                sleep(1)
                # Downloading the audio stream
                audio_stream = yt.streams.filter(only_audio=True).first()
                audio_file = os.path.join(os.getcwd(), f"temp/{title}.mp4")
                audio_stream.download(output_path=os.getcwd(), filename=f"temp/{title}.mp4")

                # Convert the downloaded audio to MP3
                audio: AudioSegment = AudioSegment.from_file(os.path.abspath(audio_file), format="mp4")
                mp3_file = os.path.join(os.getcwd(), f"temp/{title}.mp3")
                audio.export(os.path.abspath(mp3_file), format="mp3", bitrate="320k")

                # Clean up - remove the original MP4 audio file
                os.remove(audio_file)
                shutil.move(mp3_file, os.path.join(os.getcwd(), "temp", os.path.basename(mp3_file)))
        else:
            raise ValueError("Invalid URL or URL does not belong to youtube.com")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    os.makedirs("temp", exist_ok=True)
    youtubelist = ["YOUR_LINKS"]

    futures: list[Future] = []
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        for url_txt in youtubelist:
            futures.append(executor.submit(download_mp3_youtube, url_txt))

        for f in tqdm.tqdm(futures, total=len(futures)):
            try:
                result = f.result()
                results.append(result)
            except Exception as e:
                print(f"Download failed for {f}: {e}")
                results.append(None)
