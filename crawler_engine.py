import requests
from bs4 import BeautifulSoup
import re
import time

def clean_text(text):
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def get_chapter(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'gb18030'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Title
        title_h2 = soup.find('h2')
        title = title_h2.get_text(strip=True) if title_h2 else ''
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title_match = re.search(r'_(.*?)_', title_tag.text)
                if title_match:
                    title = title_match.group(1)
        
        # Text container
        brs = soup.find_all('br')
        parents = {}
        for br in brs:
            p = br.parent
            parents[p] = parents.get(p, 0) + 1
        
        chapter_str = url.split("=")[-1]
        
        if not parents:
            return title or f'Chapter {chapter_str}', 'No text found or VIP locked.'
            
        text_container = max(parents, key=parents.get)
        
        for tag in text_container.find_all(['script', 'style', 'div', 'span', 'h2']):
            tag.decompose()
            
        text = text_container.get_text('\n', strip=True)
        text = text.replace('\xa0', ' ')
        text = clean_text(text)
        
        return title or f'Chapter {chapter_str}', text
    except Exception as e:
        return f'Chapter {url.split("=")[-1]}', f'Error fetching chapter: {e}'

def parse_novel_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'gb18030'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        title_tag = soup.find('h1', itemprop='name')
        novel_title = title_tag.get_text(strip=True) if title_tag else "Unknown_Novel"
        
        author_tag = soup.find('span', itemprop='author')
        author_name = author_tag.get_text(strip=True) if author_tag else "Unknown_Author"
        
        # Find total chapters (look for max chapterid in links)
        links = soup.find_all('a', href=re.compile(r'chapterid=\d+'))
        max_chapter = 0
        for l in links:
            m = re.search(r'chapterid=(\d+)', l.get('href', ''))
            if m:
                c = int(m.group(1))
                if c > max_chapter:
                    max_chapter = c
                    
        return novel_title, author_name, max_chapter
    except Exception as e:
        return "Unknown_Novel", "Unknown_Author", 0
