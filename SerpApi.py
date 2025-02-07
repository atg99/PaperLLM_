from serpapi import GoogleSearch

def search_google_scholar(query):
    # SERP API 엔드포인트와 필요한 파라미터 구성
    params = {
    "engine": "google_scholar",
    "q": query,
    "api_key": "92af89a34c71f99c26c49e4432238190ed3cd819f9bbc2c14df0cf45e650942d"

    }
    
    # GET 요청 보내기
    search = GoogleSearch(params)    
    # HTTP 오류 발생 시 예외 처리
    results = search.get_dict()
    organic_results = results["organic_results"]
    print(type(organic_results))
    # JSON 결과 반환
    return organic_results

# 테스트 실행
if __name__ == "__main__":
    p = "Attention Is All You Need Ashish Vaswani, Noam Shazeer, Niki Parmar"
    results = search_google_scholar("biology")
    #print(results)
