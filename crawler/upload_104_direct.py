import pandas as pd
from sqlalchemy import create_engine

# 先用測試資料，確認 MySQL + Redash 能不能通
data = [
    {
        "job_title": "資料工程師",
        "company": "測試公司A",
        "city": "桃園市",
        "salary": "40000",
        "url": "https://www.104.com.tw"
    },
    {
        "job_title": "資料工程師",
        "company": "測試公司B",
        "city": "台北市",
        "salary": "50000",
        "url": "https://www.104.com.tw"
    },
    {
        "job_title": "後端工程師",
        "company": "測試公司C",
        "city": "新北市",
        "salary": "45000",
        "url": "https://www.104.com.tw"
    }
]

df = pd.DataFrame(data)

# 你的 mysql.yml 裡面是：
# MYSQL_USER=user
# MYSQL_PASSWORD=test
# MYSQL_DATABASE=mydb
engine = create_engine("mysql+pymysql://user:test@mysql_mysql:3306/mydb")

df.to_sql(
    "job_104",
    con=engine,
    if_exists="replace",
    index=False
)

print("上傳完成，已建立 job_104 資料表")