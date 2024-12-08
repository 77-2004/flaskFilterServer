# app.py
import requests

from filter_main_page import get_index_html,remove_tags_with_prohibited_words
from filter_content_page_side_bar import remove_href,filter_detail_page
from bs4 import BeautifulSoup
import logging

from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

def filter_html(html_content, prohibited_words):
    html_content = request.data.decode('utf-8')
    # print(html_content)
    # 这里添加过滤逻辑
    soup = BeautifulSoup(html_content, 'lxml')  # 创建Beautiful Soup对象
    # print(soup)
    # hrefs_to_remove = import_file_to_list(blacklist_path)  # 将敏感链接文件转为列表
    # prohibited_words = import_file_to_list(prohibited_words_path)  # 将敏感词文件转为列表
    # for script in soup.find_all('body'):
    #     script.decompose()
    hrefs_to_remove=['俄乌战争','六四',"台湾"]
    prohibited_words=hrefs_to_remove
    logging.info("hrefs_to_remove %s", hrefs_to_remove)
    logging.info("prohibited_words %s", prohibited_words)
    # print("hrefs_to_remove",hrefs_to_remove)
    # print("prohibited_words",prohibited_words)
    # prohibited_words = ['中国', '俄乌战争']  # 敏感词列表
    # 主页、其他页面的过滤
    soup = remove_tags_with_prohibited_words(soup, prohibited_words)  # 返回处理后的soup

    # 侧边栏过滤方法
    modified_html = remove_href(filter_detail_page(soup, prohibited_words),
                                hrefs_to_remove)  # 先处理<li>标签，避免<li>中的<div>子标签删除完毕后留下空的<li>标签

    modified_html = str(modified_html)  # 将BeautifulSoup对象转换回字符串
    modified_soup = modified_html
    # print(modified_html)
    # if "台湾" in modified_html:
    #     print("wqerqwerwqr")
    #     modified_html = modified_html.replace('台湾',"我靠")
    return jsonify({'html': modified_html})

@app.route('/filter', methods=['POST'])

def filter_url():
    data = request.get_json()
    url = data.get("url")  # 获取客户端传来的 URL
    prohibited_words = ["俄乌战争", "六四", "台湾"]  # 示例敏感词

    try:
        # 请求网页内容
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，会抛出异常

        # 过滤 HTML
        filtered_html = filter_html(response.text, prohibited_words)

        # 返回过滤后的 HTML
        return jsonify({"html": filtered_html}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400
if __name__ == '__main__':
    app.run(debug=True,port=24464)
