import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# OpenAI API 클라이언트 설정
client = OpenAI(api_key=os.environ.get('API_KEY'))  # 여기에 실제 API 키 입력

# 시스템 메시지 정의
sys_message = '''
Summary of the paper

The length of the summary can be adjusted flexibly depending on the length of the document

If there is an argument, the basis should be included

The summary style should be organized to maintain the original tone of the paper, but be concise and contain key contents

No special characters should be used

Cover the key concepts without missing information
'''

def summarize_text(text):
    """
    OpenAI API를 사용하여 텍스트를 요약하는 함수.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": sys_message},
                {"role": "user", "content": text},
            ],
            temperature=0.5
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None

def extract_number(text):
    """문자열에서 숫자를 추출하여 반환하는 함수"""
    match = re.search(r'\d+', text)
    return int(match.group()) if match else float('inf')

def process_pages(directory):
    """
    `pages` 디렉토리 내 모든 페이지를 요약하고 `summary/{번호}/page_{n}.txt`에 저장.
    """
    ss = 0
    ff = 0
    fails = []

    # 1️⃣ 상위 폴더 정렬 (예: 1/, 2/, 3/ ...)
    folders = sorted(
        [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))],
        key=extract_number
    )

    for folder in tqdm(folders, desc="Processing folders", unit="folder"):
        pages_dir = os.path.join(directory, folder, "pages")
        if not os.path.isdir(pages_dir):
            continue
        
        summary_dir = os.path.join(directory, "summary", folder)
        os.makedirs(summary_dir, exist_ok=True)

        # 2️⃣ 내부 `pages` 폴더 내 파일 정렬 (예: page_1.txt, page_2.txt, ..., page_10.txt)
        page_files = sorted(
            [f for f in os.listdir(pages_dir) if f.endswith(".txt")],
            key=extract_number
        )
        
        for filename in page_files:
            page_path = os.path.join(pages_dir, filename)
            
            with open(page_path, 'r', encoding='utf-8') as file:
                page_text = file.read()

            summary = summarize_text(page_text)

            if summary:
                summary_path = os.path.join(summary_dir, filename)
                with open(summary_path, "w", encoding="utf-8") as summary_file:
                    summary_file.write(summary)
                    print(f"{summary_path} saved")

if __name__ == '__main__':
    texts_directory = "/Users/jejinan/Desktop/LLM_fine-tuning/pages"
    print(process_pages(texts_directory))