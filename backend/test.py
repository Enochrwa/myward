import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import pyperclip

def scrape_links_and_media(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    all_links = set()
    media_files = set()

    video_extensions = ['.mp4', '.webm', '.mkv', '.mov', '.flv', '.avi']
    audio_extensions = ['.mp3', '.wav', '.aac', '.ogg', '.m4a']
    all_extensions = video_extensions + audio_extensions

    # Extract from <a>, <source>, <video>, <audio>, <iframe>
    for tag in soup.find_all(['a', 'source', 'video', 'audio', 'iframe']):
        href = tag.get('href') or tag.get('src')
        if href:
            full_url = urljoin(url, href)
            if any(full_url.lower().endswith(ext) for ext in all_extensions):
                media_files.add(full_url)
            elif urlparse(full_url).scheme in ['http', 'https']:
                all_links.add(full_url)

    # Extract from JavaScript content using regex
    for script in soup.find_all('script'):
        if script.string:
            matches = re.findall(r'https?://[^\s\'"]+\.(mp4|mp3|webm|mkv|mov|flv|avi|wav|aac|ogg|m4a)', script.string)
            for match in matches:
                media_url = re.search(r'(https?://[^\s\'"]+\.' + match + ')', script.string)
                if media_url:
                    media_files.add(media_url.group(1))

    return {
        'all_links': sorted(all_links),
        'media_files': sorted(media_files)
    }


if __name__ == '__main__':
    url = 'https://www.agasobanuyetimes.com'
    result = scrape_links_and_media(url)

    if result:
        print("\n🔗 All Links:")
        print("\n".join(result['all_links']))

        print("\n🎬 Media Files (Video & Audio):")
        print("\n".join(result['media_files']))

        # Copy to clipboard
        if result['media_files']:
            pyperclip.copy('\n'.join(result['media_files']))
            print("\n✅ Media links copied to clipboard.")

        # Save to file
        with open('media_links.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(result['media_files']))
            print("💾 Media links saved to media_links.txt.")
    else:
        print("⚠️ No media links found.")
