from flask import Flask, request, jsonify, render_template
import sqlite3
import requests

app = Flask(__name__, static_folder='static')

API_KEY = 'sk-d71d1dcbaf2e46b7b75823cea7078911'

BASE_PROMPT = """
你是一个文字整合专家，你会收到一个用户的问题以及对应的答案，但是这个答案只有关键部分，没有完整的语句。
你需要结合问题与答案，将它们整合为一个完整的答案。
例如你会收到以下信息：
question:"有哪些人的年龄低于23"
answer:"[('Alice',),('小美'),('SpongeBob')]"
那么你的任务是把这两个信息整合为："Alice，小美，SpongeBob的年龄低于23"，并且输出。
只允许输出整合的信息，禁止输出其他废话
"""

PROMPT = """
question: %s
answer: %s
"""

db_file = "/hy-tmp/project/WWW2025/RAG/database1.db"

def integrate_message(query, answer):
    content = PROMPT % (query, answer)
    headers = {'Content-Type': 'application/json'}
    try:
        data = {
            'model': "qwen-plus-1127",
            'messages': [
                {"role": "system", "content": BASE_PROMPT},
                {"role": "user", "content": content}
            ]
        }
        headers['Authorization'] = API_KEY
        r = requests.post('https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions', headers=headers, json=data)
        response = r.json()
        response = response['choices'][0]['message']['content']
        return response
    except Exception as e:
        print(e)
    return 'unknown'

def query_user(query):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Exception as e:
        print("查询出错：", e)
        result = []
    conn.close()
    return result

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 查询路由
@app.route('/query', methods=['POST'])
def query():
    user_input = request.form.get('query')
    if not user_input:
        return jsonify({"error": "查询内容不能为空"}), 400

    # 发送用户输入到LLM服务以生成sql查询语句
    url = "http://127.0.0.1:8005/generate"
    data = {"text": user_input}
    response = requests.post(url, json=data)
    generated_sql = response.json().get('generated_text', '')

    if not generated_sql:
        return jsonify({"error": "SQL 生成失败"}), 500

    query_result = query_user(generated_sql)

    if query_result:
        answer = integrate_message(user_input, query_result)
        return jsonify({"sql": generated_sql, "result": query_result, "response": answer})
    else:
        return jsonify({"error": "查询无结果"}), 404

if __name__ == '__main__':
    app.run(debug=True)
