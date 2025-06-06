import os
from bs4 import BeautifulSoup
import json
import re

data_=[]

files=os.listdir(f'{os.getcwd()}/discourse_json')

for file in files:
    d=json.load(open(f'{os.getcwd()}/discourse_json/{file}'))
    posts=d['post_stream']['posts']
    for post in posts:
        data=post['cooked']
        soup=BeautifulSoup(data, 'html.parser')
        text=soup.get_text(strip=True)
        images=[img['src'] for img in soup.find_all('img')]
        url=post['post_url']
        doc={
            'text': text,
            'images': images,
            'url': url,
        }
        data_.append(doc)

files=os.listdir(f'{os.getcwd()}/tds_pages_md')

for file in files:
    md_path = os.path.join(os.getcwd(), 'tds_pages_md', file)
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    meta_path = os.path.join(os.getcwd(), 'metadata.json')
    with open(meta_path, 'r', encoding='utf-8') as meta_file:
        metadata = json.load(meta_file)

    # Extract image URLs from markdown
    images = re.findall(r'!\[.*?\]\((.*?)\)', text)
    # Get plain text without markdown syntax
    text_only = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # remove images
    text_only = re.sub(r'[`*_>#-]', '', text_only)  # remove common markdown symbols
    text_only = text_only.strip()
    text_only = " ".join(text_only.split())  # normalize whitespace
    text_only = " ".join(text_only.split("\n"))  
    for f in metadata:
        if f['filename']==file:
            url = f['original_url']
            break
    

    doc = {
        'text': text_only,
        'images': images,
        'url': url,
    }
    data_.append(doc)

json.dump(data_, open(f'final_data.json', 'w'), indent=4, ensure_ascii=False)