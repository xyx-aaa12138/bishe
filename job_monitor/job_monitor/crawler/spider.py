import time
import random
from urllib.parse import quote
from DrissionPage import ChromiumPage, ChromiumOptions
import pymysql


BASE_URL = 'https://www.liepin.com/zhaopin/?key='


# ======================
# 数据库
# ======================
def get_db():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345twgdh',
        database='job_data',
        charset='utf8mb4',
        autocommit=False
    )
    return conn, conn.cursor()


# ======================
# 无头浏览器配置 ⭐⭐⭐
# ======================
def get_browser():

    co = ChromiumOptions()

    # ⭐ 无头模式
    co.headless(True)

    # 禁用自动化标记
    co.set_argument('--disable-blink-features=AutomationControlled')

    # 随机UA
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)"
    ]

    co.set_user_agent(random.choice(ua_list))

    return ChromiumPage(co)


INSERT_SQL = """
INSERT IGNORE INTO liepin_jobs(
    job_title, city, area, salary,
    experience, education, company,
    industry, job_link, company_link
)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


# ======================
# 随机等待（防封核心）
# ======================
def random_sleep(a=2, b=5):
    time.sleep(random.uniform(a, b))


# ======================
# 数据采集
# ======================
def get_data(dp, cursor, conn, url):

    dp.listen.start('searchfront4c.pc-search-job')
    dp.get(url)

    batch_data = []

    for page in range(1, 11):

        print(f'采集第{page}页')

        try:
            if page == 1:
                resp = dp.listen.wait(count=2, timeout=15)
                json_data = resp[-1].response.body
            else:
                resp = dp.listen.wait(timeout=15)
                json_data = resp.response.body
        except:
            print("请求超时，跳过")
            continue

        job_list = json_data['data']['data']['jobCardList']

        for item in job_list:
            try:
                city_info = item['job']['dq'].split('-')
                city = city_info[0]
                area = city_info[1] if len(city_info) > 1 else '未知'

                job = item['job']
                comp = item['comp']

                batch_data.append((
                    job.get('title'),
                    city,
                    area,
                    job.get('salary'),
                    job.get('requireWorkYears'),
                    job.get('requireEduLevel'),
                    comp.get('compName'),
                    comp.get('compIndustry'),
                    job.get('link'),
                    comp.get('link')
                ))

                # 批量写入
                if len(batch_data) >= 50:
                    cursor.executemany(INSERT_SQL, batch_data)
                    conn.commit()
                    batch_data.clear()

            except Exception as e:
                print("解析失败:", e)

        # ⭐ 模拟人类滚动
        dp.scroll.to_bottom()
        random_sleep()

        next_btn = dp.ele('css:.ant-pagination-next')
        if next_btn:
            next_btn.click()
            random_sleep(3, 6)
        else:
            break

    if batch_data:
        cursor.executemany(INSERT_SQL, batch_data)
        conn.commit()


# ======================
# 外部调用入口
# ======================
def run_spider(keyword):

    url = BASE_URL + quote(keyword)

    dp = get_browser()
    conn, cursor = get_db()

    try:
        get_data(dp, cursor, conn, url)
        print("采集完成")

    finally:
        cursor.close()
        conn.close()
        dp.quit()