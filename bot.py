# bot.py
import requests
import base64
import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from io import BytesIO

# कॉन्फिग फाइल से टोकन इम्पोर्ट करें
from config import TELEGRAM_BOT_TOKEN

# लॉगिंग सेटअप ताकि कोई एरर आए तो पता चले
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# केवल इन एक्सटेंशन वाली फाइलों को ही कोड फाइल माना जाएगा
# आप इस लिस्ट को अपनी जरूरत के हिसाब से बदल सकते हैं
CODE_FILE_EXTENSIONS = [
    '.py', '.js', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php', '.html',
    '.css', '.scss', '.less', '.ts', '.tsx', '.jsx', '.vue', '.swift', '.kt',
    '.rs', '.lua', '.pl', '.sh', '.bat', '.json', '.xml', '.yml', '.yaml', '.md',
    '.sql', '.dockerfile', 'Dockerfile', '.env.example', '.gitignore', 'requirements.txt'
]

def get_repo_files_recursive(owner, repo, path=""):
    """
    GitHub API का उपयोग करके रिपॉजिटरी की फाइलों को रिकर्सिव रूप से प्राप्त करता है।
    """
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Error fetching repo contents: {response.status_code} - {response.text}")
        return None

    files_content = []
    contents = response.json()

    for item in contents:
        if item['type'] == 'file':
            # चेक करें कि क्या फाइल का एक्सटेंशन हमारी लिस्ट में है
            if any(item['name'].endswith(ext) for ext in CODE_FILE_EXTENSIONS):
                try:
                    # फाइल का कंटेंट डाउनलोड करें
                    file_response = requests.get(item['download_url'])
                    if file_response.status_code == 200:
                        code = file_response.text
                        # फाइल का पाथ और कोड जोड़ें
                        files_content.append(f"/{item['path']}\n\n{code}\n\n")
                except Exception as e:
                    logger.error(f"Could not download file {item['path']}: {e}")

        elif item['type'] == 'dir':
            # अगर यह एक डायरेक्टरी है, तो इसके अंदर की फाइलों के लिए फंक्शन को फिर से कॉल करें
            files_content.extend(get_repo_files_recursive(owner, repo, item['path']))
            
    return files_content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start कमांड के लिए हैंडलर।"""
    await update.message.reply_text(
        "नमस्ते! मुझे किसी भी पब्लिक GitHub रिपॉजिटरी का लिंक भेजें।\n\n"
        "मैं उस रिपॉजिटरी की सभी कोड फाइलों को एक सिंगल टेक्स्ट फाइल में बदल दूँगा।"
    )

async def handle_repo_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """GitHub लिंक को हैंडल करता है।"""
    message_text = update.message.text
    if not message_text.startswith("https://github.com/"):
        await update.message.reply_text("कृपया एक वैध GitHub रिपॉजिटरी का लिंक भेजें।")
        return

    try:
        parts = message_text.strip().split('/')
        owner = parts[3]
        repo = parts[4].split('.')[0] # .git को हटाने के लिए
    except IndexError:
        await update.message.reply_text("लिंक सही फॉर्मेट में नहीं है। फॉर्मेट: https://github.com/owner/repo")
        return

    await update.message.reply_text(f"`{owner}/{repo}` रिपॉजिटरी को प्रोसेस किया जा रहा है... इसमें थोड़ा समय लग सकता है।", parse_mode='Markdown')

    try:
        all_files_data = get_repo_files_recursive(owner, repo)

        if not all_files_data:
            await update.message.reply_text("इस रिपॉजिटरी में कोई कोड फाइल नहीं मिली या रिपॉजिटरी को एक्सेस नहीं किया जा सका।")
            return

        # सभी फाइलों के कंटेंट को एक स्ट्रिंग में मिलाएँ
        full_code = "".join(all_files_data)
        
        # स्ट्रिंग को बाइट्स में बदलें ताकि इसे फाइल के रूप में भेजा जा सके
        output_file_bytes = full_code.encode('utf-8')
        
        # BytesIO का उपयोग करके इन-मेमोरी फाइल बनाएँ
        output_file = BytesIO(output_file_bytes)
        output_file.name = "file.txt"

        await update.message.reply_document(
            document=InputFile(output_file),
            filename="file.txt",
            caption=f"लीजिए, `{owner}/{repo}` रिपॉजिटरी का पूरा कोड।",
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        await update.message.reply_text("एक एरर आ गया है। कृपया सुनिश्चित करें कि रिपॉजिटरी पब्लिक है और लिंक सही है।")

def main() -> None:
    """बॉट को चलाता है।"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # कमांड्स को रजिस्टर करें
    application.add_handler(CommandHandler("start", start))
    
    # GitHub लिंक के लिए मैसेज हैंडलर
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_repo_link))

    # बॉट को पोलिंग मोड में चलाएँ
    application.run_polling()

if __name__ == '__main__':
    main()
