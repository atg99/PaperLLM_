import re
import os

def split_text_into_pages(text):
    """
    주어진 텍스트에서 "==== Page N ====" 형식의 구분자를 찾아 페이지별로 분리합니다.
    각 페이지는 (페이지번호, 페이지 내용)의 튜플로 반환되며, 최종적으로
    페이지 번호를 key, 페이지 내용을 value로 하는 딕셔너리를 반환합니다.
    """
    # DOTALL 플래그를 사용하면 줄바꿈 문자도 포함하여 매칭할 수 있습니다.
    pattern = r'==== Page (\d+) ====(.*?)(?===== Page|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    pages = {}
    for num, content in matches:
        pages[num.strip()] = content.strip()
    return pages

def save_pages(page_dict, output_dir='pages'):
    """
    페이지 딕셔너리(page 번호: 페이지 내용)를 받아 output_dir 폴더에
    각 페이지를 'page_<번호>.txt' 파일로 저장합니다.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for page_num, content in page_dict.items():
        filename = os.path.join(output_dir, f'page_{page_num}.txt')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        #print(f"Page {page_num} saved to {filename}")

def process_text_files(directory):
    """
    지정된 디렉토리 내 모든 .txt 파일을 찾아 처리하는 함수.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)

            # 텍스트 파일 읽기
            with open(file_path, 'r', encoding='utf-8') as file:
                full_text = file.read()

            # 텍스트를 페이지 단위로 분리
            pages = split_text_into_pages(full_text)

            # 정규식 패턴 (_ 뒤에 숫자)
            pattern = r"_([0-9]+)"
            match = re.search(pattern, filename)

            # output 디렉토리 설정
            if match:
                output_dir = os.path.join("pages", f"{match.group(1)}/pages")
            else:
                output_dir = os.path.join("pages", "Unknown/pages")

            # 페이지 저장
            save_pages(pages, output_dir=output_dir)
            print(f"Processed: {filename} -> Saved in {output_dir}")

if __name__ == '__main__':
    texts_directory = "/Users/jejinan/Desktop/LLM_fine-tuning/texts"
    process_text_files(texts_directory)