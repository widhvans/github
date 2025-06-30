# bot.py

import requests
import base64
import os
from urllib.parse import urlparse

# config.py से सेटिंग्स इम्पोर्ट करें
# Import settings from config.py
try:
    from config import CODE_EXTENSIONS, IGNORED_ITEMS, IGNORED_EXTENSIONS
except ImportError:
    print("त्रुटि: सुनिश्चित करें कि 'config.py' फ़ाइल इसी डायरेक्टरी में मौजूद है।")
    exit()

def get_repo_files(owner, repo, path=''):
    """
    GitHub API का उपयोग करके रिपॉजिटरी की फ़ाइलों और डायरेक्ट्री को रिकर्सिव रूप से प्राप्त करता है।
    Recursively gets the repository's files and directories using the GitHub API.
    """
    api_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    response = requests.get(api_url)
    
    # रेट लिमिट या अन्य त्रुटियों के लिए जाँच करें
    # Check for rate limits or other errors
    if response.status_code != 200:
        print(f"त्रुटि: API से डेटा प्राप्त करने में विफल। स्टेटस कोड: {response.status_code}")
        print(f"संदेश: {response.json().get('message', 'कोई संदेश नहीं')}")
        return

    items = response.json()
    
    for item in items:
        # अनदेखा की जाने वाली आइटम को छोड़ दें
        # Skip items that should be ignored
        if item['name'] in IGNORED_ITEMS:
            continue

        if item['type'] == 'dir':
            # अगर यह एक डायरेक्टरी है, तो इसके अंदर की फाइलों के लिए रिकर्सिव रूप से कॉल करें
            # If it's a directory, recursively call for the files inside it
            yield from get_repo_files(owner, repo, item['path'])
        
        elif item['type'] == 'file':
            # फ़ाइल एक्सटेंशन की जाँच करें
            # Check the file extension
            file_extension = os.path.splitext(item['name'])[1]
            # यदि फ़ाइल का कोई एक्सटेंशन नहीं है, तो उसके नाम की जाँच करें (जैसे Dockerfile)
            # If the file has no extension, check its name (like Dockerfile)
            is_code_file = file_extension in CODE_EXTENSIONS or item['name'] in CODE_EXTENSIONS

            if is_code_file and file_extension not in IGNORED_EXTENSIONS:
                yield item

def main():
    """
    मुख्य फ़ंक्शन जो प्रक्रिया को चलाता है।
    The main function that runs the process.
    """
    repo_url = input("सार्वजनिक GitHub रिपॉजिटरी का URL दर्ज करें: ")
    
    # URL से owner और repo का नाम निकालें
    # Extract owner and repo name from the URL
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if parsed_url.netloc != 'github.com' or len(path_parts) < 2:
        print("अमान्य GitHub रिपॉजिटरी URL। कृपया 'https://github.com/owner/repo' फॉर्मेट में URL दर्ज करें।")
        return
        
    owner, repo = path_parts[0], path_parts[1]
    output_filename = "file.txt"

    print(f"रिपॉजिटरी '{owner}/{repo}' को प्रोसेस किया जा रहा है...")

    try:
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            # रिपॉजिटरी से सभी योग्य फ़ाइलें प्राप्त करें
            # Get all eligible files from the repository
            files_to_process = list(get_repo_files(owner, repo))

            if not files_to_process:
                print("कोई योग्य कोड फ़ाइल नहीं मिली या रिपॉजिटरी तक नहीं पहुँचा जा सका।")
                return

            for item in files_to_process:
                file_path = item['path']
                print(f"प्रोसेस हो रही है: {file_path}")
                
                # फ़ाइल का कंटेंट प्राप्त करें
                # Get the content of the file
                content_response = requests.get(item['download_url'])
                if content_response.status_code == 200:
                    try:
                        content = content_response.content.decode('utf-8')
                    except UnicodeDecodeError:
                        print(f" चेतावनी: {file_path} को utf-8 के रूप में डीकोड नहीं किया जा सका। इस फ़ाइल को छोड़ा जा रहा है।")
                        continue

                    # अनुरोध के अनुसार फ़ाइल में लिखें
                    # Write to the file as per the request
                    output_file.write(f"/{file_path}\n")
                    output_file.write(f"{content}\n")
                    output_file.write("\n") # फाइलों के बीच एक खाली लाइन
                else:
                    print(f"चेतावनी: {file_path} को डाउनलोड नहीं किया जा सका।")

        print(f"\nप्रक्रिया पूरी हुई! सारा कोड '{output_filename}' फ़ाइल में सहेज लिया गया है।")

    except requests.exceptions.RequestException as e:
        print(f"एक नेटवर्क त्रुटि हुई: {e}")
    except Exception as e:
        print(f"एक अप्रत्याशित त्रुटि हुई: {e}")

if __name__ == "__main__":
    main()
