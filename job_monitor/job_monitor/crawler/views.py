import json
from django.http import JsonResponse
from crawler.spider import run_spider
import pymysql
import re
def parse_salary_to_year(salary_str):
    """
    把薪资转换成年薪（单位：万元）
    规则：
    10-15K -> 10K * 12
    8-12K·14薪 -> 8K * 14
    """

    if not salary_str:
        return None

    salary_str = str(salary_str).lower().replace(' ', '')

    if '面议' in salary_str:
        return None

    # 提取最低薪资
    nums = re.findall(r'(\d+)', salary_str)
    if not nums:
        return None

    low_k = int(nums[0])

    # 默认12薪
    month = 12

    m = re.search(r'(\d+)薪', salary_str)
    if m:
        month = int(m.group(1))

    # 年薪（万元）
    yearly = low_k * month / 10

    return yearly
def run(request):

    # ===== 接收POST数据 =====
    data = json.loads(request.body)
    keyword = data.get("major")

    # 运行爬虫
    run_spider(keyword)

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345twgdh',
        database='job_data',
        charset='utf8mb4'
    )

    cursor = conn.cursor()

    # 城市
    cursor.execute("""
        SELECT city, COUNT(*) FROM liepin_jobs
        GROUP BY city LIMIT 10
    """)
    city = cursor.fetchall()

    # 学历
    cursor.execute("""
        SELECT education, COUNT(*) FROM liepin_jobs
        GROUP BY education
    """)
    edu = cursor.fetchall()

    # 工作经验
    cursor.execute("""
        SELECT experience, COUNT(*) FROM liepin_jobs
        GROUP BY experience
    """)
    exp = cursor.fetchall()

    # 薪资
    salary_bucket = {
        "5k以下": 0,
        "5-10k": 0,
        "10-15k": 0,
        "15-20k": 0,
        "20k以上": 0
    }

    cursor.execute("SELECT salary FROM liepin_jobs")
    rows = cursor.fetchall()
    print(1, rows)
    for row in rows:
        print(2, row)
        yearly = parse_salary_to_year(row[0])

        if yearly is None:
            continue

        # 转回月薪区间（方便你原图表）
        month_k = yearly * 10 / 12

        if month_k < 5:
            salary_bucket["5k以下"] += 1
        elif month_k < 10:
            salary_bucket["5-10k"] += 1
        elif month_k < 15:
            salary_bucket["10-15k"] += 1
        elif month_k < 20:
            salary_bucket["15-20k"] += 1
        else:
            salary_bucket["20k以上"] += 1
    print(salary_bucket)
    conn.close()

    return JsonResponse({
        "city":list(city),
        "edu":list(edu),
        "exp":list(exp),
        "salary":list(salary_bucket.items())
    })