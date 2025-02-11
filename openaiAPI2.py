import os
import aiohttp
import asyncio
import aiofiles
import re
from tqdm.asyncio import tqdm

# OpenAI API 키 설정
API_KEY = "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"
API_URL = "https://api.openai.com/v1/chat/completions"

# OpenAI 요청 설정
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

SYSTEM_PROMPT = '''
Summary of the paper

The length of the summary can be adjusted flexibly depending on the length of the document

If there is an argument, the basis should be included

The summary style should be organized to maintain the original tone of the paper, but be concise and contain key contents

No special characters should be used

Cover the key concepts without missing information
'''

def extract_number(text):
    """문자열에서 숫자만 추출하여 반환 (숫자가 없으면 큰 값 반환)"""
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else float('inf')

async def summarize_text(session, page_path, summary_path):
    """비동기적으로 OpenAI API 요청을 보내고 요약 결과를 저장하는 함수"""
    if os.path.exists(summary_path):
        print(f"Skipping {summary_path}, already exists.")
        return  # 이미 처리된 파일이면 건너뛰기

    # 파일 읽기
    async with aiofiles.open(page_path, 'r', encoding='utf-8') as file:
        page_text = await file.read()

    # OpenAI API 요청 데이터
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": page_text},
        ],
        "temperature": 0.6,
    }

    try:
        async with session.post(API_URL, headers=HEADERS, json=payload) as response:
            if response.status != 200:
                print(f"API Error for {page_path}: {await response.text()}")
                return

            result = await response.json()
            summary = result["choices"][0]["message"]["content"]

            # 결과 저장
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            async with aiofiles.open(summary_path, "w", encoding="utf-8") as summary_file:
                await summary_file.write(summary)

            print(f"Saved: {summary_path}")

    except Exception as e:
        print(f"Error processing {page_path}: {e}")

async def process_pages(directory, max_concurrent_requests=5):
    """순서를 보장하면서 비동기적으로 pages 디렉토리 내 모든 페이지를 요약"""
    
    # 폴더 이름을 숫자 기준 정렬
    folders = sorted(
        [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))],
        key=extract_number
    )

    queue = asyncio.Queue()

    for folder in folders[580:]:
        pages_dir = os.path.join(directory, folder, "pages")
        if not os.path.isdir(pages_dir):
            continue

        summary_dir = os.path.join(directory, "summary", folder)
        os.makedirs(summary_dir, exist_ok=True)

        # 파일을 숫자 기준 정렬
        page_files = sorted(
            [f for f in os.listdir(pages_dir) if f.endswith(".txt")],
            key=extract_number
        )

        for filename in page_files:
            page_path = os.path.join(pages_dir, filename)
            summary_path = os.path.join(summary_dir, filename)
            await queue.put((page_path, summary_path))

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(max_concurrent_requests)

        async def worker():
            while not queue.empty():
                page_path, summary_path = await queue.get()
                async with semaphore:
                    await summarize_text(session, page_path, summary_path)
                queue.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(max_concurrent_requests)]
        await tqdm.gather(*workers, desc="Processing pages")
        await queue.join()

# 실행
if __name__ == "__main__":
    directory = "/Users/jejinan/Desktop/LLM_fine-tuning/pages"  # 기본 디렉토리 설정
    asyncio.run(process_pages(directory, max_concurrent_requests=10))
