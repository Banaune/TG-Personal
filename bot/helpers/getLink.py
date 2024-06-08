import os
import requests
import cloudscraper
import threading
from urllib.parse import urlparse, parse_qs
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from bot.helpers.upload import upload_file_to_telegram
from pyrogram.types import Message


# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

cloudscraper_instance = cloudscraper.create_scraper()

def write_to_file(data):
    try:
        with open("output.txt", "a") as file:
            file.write(data + "\n")
        logging.info("Data written to file successfully.")
    except Exception as e:
        logging.error(f"Error writing to file: {e}")

def download_part(url, start, end, filename, progress_bar):
    headers = {'Range': f'bytes={start}-{end}'}
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'r+b') as f:
            f.seek(start)
            for chunk in r.iter_content(chunk_size=8192):
                progress_bar.update(len(chunk))
                f.write(chunk)

def merge_files(part_filenames, destination):
    with open(destination, 'wb') as destination_file:
        for part_filename in part_filenames:
            with open(part_filename, 'rb') as part_file:
                destination_file.write(part_file.read())
            os.remove(part_filename)

def create_empty_file_with_size(filename, size):
    """Create an empty file with a specified size."""
    with open(filename, 'wb') as f:
        f.seek(size - 1)
        f.write(b'\0')

def download_file(url, filename, num_parts=4):
    try:
        with requests.head(url) as r:
            r.raise_for_status()
            total_size_in_bytes = int(r.headers.get('content-length', 0))
            part_size = total_size_in_bytes // num_parts

        # Create part files with expected size to ensure they exist
        part_filenames = [f"{filename}.part{i}" for i in range(num_parts)]
        for part_filename in part_filenames:
            create_empty_file_with_size(part_filename, part_size)

        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

        with ThreadPoolExecutor(max_workers=num_parts) as executor:
            futures = []
            for i in range(num_parts):
                start = part_size * i
                end = start + part_size - 1 if i < num_parts - 1 else total_size_in_bytes - 1
                futures.append(
                    executor.submit(download_part, url, start, end, part_filenames[i], progress_bar)
                )

            # Wait for all threads to complete
            for future in futures:
                future.result()

        progress_bar.close()
        merge_files(part_filenames, filename)
        logging.info(f"File downloaded successfully: {filename}")
        return filename, True
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        return None, False

def download_file_cloudscraper(url, filename):
    try:
        # Create 'downloads' directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)

        # Join 'downloads' with the filename
        filename = os.path.join('downloads', filename)
        with cloudscraper_instance.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"File downloaded successfully: {filename}")
        return filename, True
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        return None, False

def get_download_link(info):
    try:
        if info and info.get('ok'):
            payload = {
                "shareid": info['shareid'],
                "uk": info['uk'],
                "sign": info['sign'],
                "timestamp": info['timestamp'],
                "fs_id": info['list'][0]['fs_id']
            }
            response = requests.post("https://terabox-dl.qtcloud.workers.dev/api/get-download", json=payload)
            logging.info(f"POST request payload: {payload}")
            if response.status_code == 200:
                download_info = response.json()
                logging.info(f"Download info received: {download_info}")
                if download_info.get('ok'):
                    write_to_file(download_info['downloadLink'])
                    # Extract the original filename from the response
                    original_filename = info['list'][0]['filename']
                    # Call download_file function here with the obtained download link and original filename
                    # download_file(download_info['downloadLink'], original_filename)
                    filename, isSuccessful = download_file(download_info['downloadLink'], original_filename)
                    if not isSuccessful:
                        logging.error("Error downloading file.")
                        return
                    logging.info(f"Downloaded file: {filename}")
                    return filename
                    
                else:
                    logging.error("Download info 'ok' field is not True.")
            else:
                logging.error(f"POST request failed with status code {response.status_code}")
        else:
            logging.error("Info is None or 'ok' field is not True.")
    except Exception as e:
        logging.error(f"Error in get_download_link: {e}")

def extract_params(url):
    try:
        path = urlparse(url).path
        shorturl = path.split('/')[-1]
        logging.info(f"Shorturl extracted: {shorturl}")
        return {'shorturl': [shorturl]}
    except Exception as e:
        logging.error(f"Error extracting params: {e}")
        return None
    
def get_info(url):
    try:
        params = extract_params(url)
        if not params:
            logging.error("No params extracted from URL.")
            return None
        shorturl = params['shorturl'][0] if 'shorturl' in params else None
        if shorturl:
            response = requests.get(f"https://terabox-linker.tinn.workers.dev/api/get-info?shorturl={shorturl}&pwd=")
            logging.info(f"GET request for info sent with shorturl: {shorturl}")
            if response.status_code == 200:
                response_data = response.json()
                logging.info(f"Response data received: {response_data}")
                write_to_file(str(response_data))
                return response_data
            else:
                logging.error(f"GET request failed with status code {response.status_code}")
        else:
            logging.error("Shorturl param not found in URL.")
    except Exception as e:
        logging.error(f"Error in get_info: {e}")
    return None

def validate_download_mime_type(url):
    try:
        response = cloudscraper_instance.get(url)
        logging.info(f"GET request sent to URL: {url}, status code: {response.status_code}, headers: {response.headers}, content-type: {response.headers.get('content-type')}")
        if response.status_code == 200:
            content_type = response.headers.get('content-type')
            logging.info(f"Content-Type: {content_type}")
            if content_type and (content_type.startswith('video') or content_type.startswith('audio') or content_type.startswith('multipart')) or content_type.startswith('application') or content_type.startswith('image'):
                logging.info("Valid content type; can proceed with download.")
                content_disposition = response.headers.get('content-disposition')
                filename = None
                if content_disposition:
                    filename_parts = content_disposition.split('filename=')
                    if len(filename_parts) > 1:
                        filename = filename_parts[1]
                        filename = filename.strip('"')
                if not filename:
                    # Fallback to the path in the URL
                    parsed_url = urlparse(url)
                    filename = os.path.basename(parsed_url.path)
                logging.info(f"Filename: {filename}")
                return True, filename
            else:
                logging.error("Invalid content type; not a video.")
        else:
            logging.error(f"GET request failed with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Error in validate_download_mime_type: {e}")
    return False, None

    
async def telegram_bot_function(url, client, message: Message):
    try:
        logging.info(f"Starting process for URL: {url}")
        info = get_info(url)
        if info:
            filename = get_download_link(info)
            if filename:
                logging.info(f"Downloaded file: {filename}")
                upload_file_to_telegram(client, message, filename)
            else:
                await message.edit("Download link not retrieved; cannot proceed to download file.")
                logging.error("Download link not retrieved; cannot proceed to download file.")
        else:
            logging.error("No info retrieved; cannot proceed to get download links.")
    except Exception as e:
        logging.error(f"Error in process_url: {e}")

async def general_download_and_upload(url, client, message):
    try:
        logging.info(f"Starting process for URL: {url}")
        if not url.startswith("http"):
            url = "http://" + url

        isValid, filename = validate_download_mime_type(url)
        if not isValid:
            await client.send_message(message.chat.id, f"Invalid download link: {url}")
            return
        logging.info(f"isValid: {isValid}, filename: {filename}")
        if isValid:
            filename, isSuccessful = download_file_cloudscraper(url, filename)
            if not isSuccessful:
                logging.error("Error downloading file.")
                return
            await upload_file_to_telegram(client, message, filename)
        else:
            logging.error("No info retrieved; cannot proceed to get download link.")
    except Exception as e:
        logging.error(f"Error in process_url: {e}")

def follow_redirects(url):
    try:
        response = cloudscraper_instance.get(url, allow_redirects=False)
        if response.status_code == 302:
            location = response.headers.get('Location')
            logging.info(f"Redirect location: {location}")
            return location
        else:
            logging.error(f"Non-redirect status code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error in follow_redirects: {e}")
    return None