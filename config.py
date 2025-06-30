# config.py

# वे फ़ाइल एक्सटेंशन जिन्हें हम कोड फाइलें मानते हैं। आप इस सूची में और जोड़ सकते हैं।
# We consider file extensions that we believe are code files. You can add more to this list.
CODE_EXTENSIONS = {
    '.py', '.js', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs', '.php',
    '.html', '.css', '.scss', '.less', '.xml', '.json', '.yaml', '.yml', '.md',
    '.sh', '.bat', '.ps1', '.rb', '.ts', '.tsx', 'Dockerfile', '.env', '.sql'
}

# जिन फ़ाइलों या डायरेक्ट्री को पूरी तरह से अनदेखा करना है।
# Files or directories to completely ignore.
IGNORED_ITEMS = {
    '.git', '.github', '.vscode', 'node_modules', 'dist', 'build', '__pycache__',
    'package-lock.json', 'yarn.lock'
}

# बाइनरी या गैर-टेक्स्ट फ़ाइल एक्सटेंशन जिन्हें अनदेखा किया जाना है।
# Binary or non-text file extensions to be ignored.
IGNORED_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.exe', '.dll', '.so',
    '.o', '.a', '.lib', '.class', '.jar', '.war', '.ear', '.mp3',
    '.mp4', '.avi', '.mkv', '.mov', '.webm', '.woff', '.woff2', '.ttf',
    '.eot', '.otf'
}
