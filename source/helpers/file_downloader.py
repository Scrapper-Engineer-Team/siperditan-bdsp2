import aiohttp
import yt_dlp
import aiofiles
import os
import asyncio


async def download_file(links, filename, save_path):
    try:
        os.makedirs(save_path, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(links) as response:
                response.raise_for_status()

                full_path = os.path.join(save_path, filename)

                async with aiofiles.open(full_path, 'wb') as file:
                    await file.write(await response.read())

                print(f"File '{filename}' berhasil diunduh dan disimpan di '{save_path}'.")
    except aiohttp.ClientError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


async def download_video(url, path, filename):
    try:
        # Fungsi untuk melacak kemajuan
        def hook(d):
            if d['status'] == 'downloading':
                print(f'Downloading: {d["filename"]} ({d["_percent_str"]})')
            elif d['status'] == 'finished':
                print(f'Done downloading: {d["filename"]}')

        outmpl = f'{path}%(title)s.%(ext)s'
        if filename is not None:
            outmpl = f'{path}/{filename}.%(ext)s'

        # Opsi untuk mendownload video
        ydl_opts = {
            'outtmpl': outmpl,
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'progress_hooks': [hook],
            'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe'
        }

        # Fungsi untuk mendownload dalam thread terpisah
        def run_download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f'Mendownload video dari: {url}')
                ydl.download([url])
                print('Video berhasil didownload!')

        # Menjalankan download dalam thread terpisah
        await asyncio.to_thread(run_download)

    except Exception as e:
        print(f'Error: {e}')