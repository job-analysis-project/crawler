# 從 worker.py 匯入 Celery app 實例
# 所有的 task 都要透過 app 來註冊, 才能被 Celery worker 識別
from crawler.worker import app
import requests
from bs4 import BeautifulSoup
import re 


# @app.task() 是 Celery 的裝飾器 (decorator)
# 有了這個裝飾器, 普通的 Python 函式就會變成「可派送的任務」
# 沒有裝飾的函式只能在本地呼叫, 無法透過 RabbitMQ 派送

# global variable for the cake job listing url
CAKE_JOB_URL = "https://www.cake.me/jobs"
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
}

# crawer for cake resume
@app.task()
def cake_crawler(search_terms="data engineer"):
    # # 這裡只是示範, 實際專案會在這裡執行爬蟲邏輯
    # print("crawler")
    # print("upload db")
    # # task 的回傳值可以透過 AsyncResult.get() 取得 (若有設定 result backend)

    # covert space to `%20` for url encoding
    encoded_terms = search_terms.replace(" ", "%20")
    search_url = f"{CAKE_JOB_URL}/{encoded_terms}"

    # send a GET request to the search URL
    parsed_jobs = []
    try:
        response = requests.get(search_url, headers=DEFAULT_HEADERS, timeout=10)
        if  response.status_code != 200:
            print(f"Failed to access the website. Status code: {response.status_code}")

            return []
        soup = BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Network error occurred:{e}")
        return []
    # empty list to store the parsed job features
    parsed_jobs = []

    # extracting data from soup object
    # find all job listings on the page
    job_listings = soup.find_all("a", class_="JobSearchItem-module-scss-module___szW4W__jobTitle")

    # the features blocks for each job listing
    features_lst = soup.find_all("div", class_="JobSearchItem-module-scss-module___szW4W__features")
    
    for job, features in zip(job_listings, features_lst):
        
        # initialize an empty list to store the features
        job_feature = {
            "job_title": job.get_text(strip=True),
            "job_type": None,
            "seniority": None,
            "location": None,
            "salary": None,
            "experience": None,
            "management_resp": None
        }

        # extract the features for each job listing
        rows = features.find_all("div", class_=re.compile("inlineMessage"))
        for row in rows:
            # identify the icon tag
            icon_tag = row.find("i", class_="fa")
            if not icon_tag:
                continue
            classes = icon_tag.get("class", [])

            label_div = row.find("div", class_=re.compile("__label"))
            if not label_div:
                continue

            # logic to determine the feature type based on the icon class
            if any("fa-user" in cls for cls in classes):
                links = label_div.find_all("a")
                if len(links) >= 1:
                    job_feature["job_type"] = links[0].get_text(strip=True)
                if len(links) >= 2:
                    job_feature["seniority"] = links[1].get_text(strip=True)
            
            elif any("fa-map-marker" in cls for cls in classes):
                locations = [a.get_text(strip=True) for a in label_div.find_all("a")]
                job_feature["location"] = ", ".join(locations) if locations else label_div.get_text(strip=True)
            
            elif any("fa-dollar-sign" in cls for cls in classes):
                job_feature["salary"] = label_div.get_text(strip=True) 

            elif any("fa-business-time" in cls for cls in classes):
                job_feature["experience"] = label_div.get_text(strip=True)

            elif any("fa-sitemap" in cls for cls in classes):
                job_feature["management_resp"] = label_div.get_text(strip=True)
            
        parsed_jobs.append(job_feature)
        
    return parsed_jobs
