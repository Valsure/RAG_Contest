from flask import Flask, request, jsonify, render_template
import mysql.connector
import requests

# 配置 MySQL 数据库连接
db_config = {
    'host': '47.95.204.27',
    'port': 3306,   
    'user': 'root',
    'password': '123456',
    'database': 'test1'
}

def query_user(query):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    # cursor.execute('SELECT age, job FROM users WHERE name = %s', (name,))
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


if __name__ == '__main__':
    url = "http://127.0.0.1:8005/generate"
    query = input("输入要查询的内容：")
    
    data = {
    "text": query
    }
    print("---------------")
    response = requests.post(url, json=data)
    query = response.json()['generated_text']
    print("大模型生成的sql语句为： ", query)
    print("---------------")
    print("数据库检索中...")
    if query_user(query):
        print("结果为： ", query_user(query))
    else:
        print('检索失败')
    

