from django.shortcuts import render
from django.http import JsonResponse
import pymysql
from crawler.spider import run_spider
import re

def dashboard(request):
    return render(request, 'dashboard.html')



def search(request):

    keyword = request.GET.get("keyword")

    # ⭐调用爬虫
    run_spider(keyword)

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='12345twgdh',
        database='job_data',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
