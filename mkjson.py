import os
import json
import re

def extract_number(text):
    """문자열에서 숫자를 추출하여 정수로 반환합니다. 숫자가 없으면 무한대를 반환합니다."""
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else float('inf')

def create_json_dataset(base_directory, output_file):
    """
    주어진 디렉토리 구조를 탐색하여 각 논문의 제목, 페이지 전문, 요약본을 포함한 JSON 데이터를 생성합니다.
    결과는 지정된 output_file에 저장됩니다.
    """
    dataset = []

    # 논문 폴더를 숫자 순으로 정렬
    paper_folders = sorted(
        [f for f in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, f))],
        key=extract_number
    )

    for folder in paper_folders:
        pages_dir = os.path.join(base_directory, folder, "pages")
        summary_dir = os.path.join(base_directory, "summary", folder)

        if not os.path.isdir(pages_dir) or not os.path.isdir(summary_dir):
            continue

        # 페이지 파일을 숫자 순으로 정렬
        page_files = sorted(
            [f for f in os.listdir(pages_dir) if f.endswith(".txt")],
            key=extract_number
        )

        for page_file in page_files:
            page_path = os.path.join(pages_dir, page_file)
            summary_path = os.path.join(summary_dir, page_file)

            if not os.path.exists(page_path) or not os.path.exists(summary_path):
                continue

            with open(page_path, 'r', encoding='utf-8') as p_file:
                page_content = p_file.read()

            with open(summary_path, 'r', encoding='utf-8') as s_file:
                summary_content = s_file.read()

            # 데이터셋에 추가
            dataset.append({
                "논문번호": folder,
                "페이지": str(extract_number(page_file)),
                "페이지 전문": page_content,
                "요약본": summary_content
            })

    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(dataset, json_file, ensure_ascii=False, indent=4)

    print(f"JSON 데이터셋이 '{output_file}'에 성공적으로 저장되었습니다.")

# 사용 예시
base_directory = "/Users/jejinan/Desktop/LLM_fine-tuning/pages"
output_file = "dataset.json"
create_json_dataset(base_directory, output_file)
