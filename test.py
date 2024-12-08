from bs4 import BeautifulSoup
import webbrowser

# 横栏过滤
def filter_section_by_h3(soup, sensitive_words):
    """
    根据<h3>标签内容过滤<ytd-item-section-renderer>标签
    """
    sections = soup.find_all('ytd-item-section-renderer', recursive=True)

    for section in sections:
        h3_tag = section.find('h3')
        if h3_tag:
            h3_content = h3_tag.text.strip()
            if any(word in h3_content for word in sensitive_words):
                section.extract()
                print({h3_content})

# 竖栏过滤
def filter_reel_item_by_span(soup, sensitive_words):
    """
    根据<span>标签内容过滤<ytd-reel-item-renderer>标签
    """
    reel_items = soup.find_all('ytd-reel-item-renderer')

    for reel_item in reel_items:
        h3_tag = reel_item.find('h3')
        if h3_tag:
            a_tag = h3_tag.find_next('a')
            if a_tag:
                span_tag = a_tag.find_next('span')
                if span_tag:
                    span_content = span_tag.text.strip()
                    if any(word in span_content for word in sensitive_words):
                        reel_item.extract()
                        print({span_content})

# 他人感兴趣板块过滤
def filter_video_renderer_by_aria_label(soup, sensitive_words):
    """
    根据aria-label属性值过滤<ytd-video-renderer>标签
    """
    video_renderers = soup.find_all('ytd-video-renderer')

    for video_renderer in video_renderers:
        h3_tag = video_renderer.find('h3')
        if h3_tag:
            a_tag = h3_tag.find_next('a')
            if a_tag:
                aria_label = a_tag.get('aria-label', '')
                if any(word in aria_label for word in sensitive_words):
                    video_renderer.extract()
                    print({aria_label})



# app.py
from filter_main_page import get_index_html,remove_tags_with_prohibited_words
from filter_content_page_side_bar import remove_href,filter_detail_page
from bs4 import BeautifulSoup
import logging

from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
@app.route('/filter', methods=['POST'])
def filter_html():
    html_content = request.data.decode('utf-8')
    # print(html_content)
    # 这里添加过滤逻辑
    soup = BeautifulSoup(html_content, 'lxml')  # 创建Beautiful Soup对象
    # print(soup)
    # hrefs_to_remove = import_file_to_list(blacklist_path)  # 将敏感链接文件转为列表
    # prohibited_words = import_file_to_list(prohibited_words_path)  # 将敏感词文件转为列表
    # for script in soup.find_all('body'):
    #     script.decompose()
    hrefs_to_remove=['俄乌战争','六四']
    prohibited_words=hrefs_to_remove
    sensitive_words=hrefs_to_remove
    logging.info("hrefs_to_remove %s", hrefs_to_remove)
    logging.info("prohibited_words %s", prohibited_words)
    # print("hrefs_to_remove",hrefs_to_remove)
    # print("prohibited_words",prohibited_words)
    # prohibited_words = ['中国', '俄乌战争']  # 敏感词列表
    # 横栏/竖栏/他人感兴趣板块 过滤
    print("----------------------------------横栏板块过滤内容-----------------------------------")
    filter_section_by_h3(soup, sensitive_words)
    print("\n--------------------------------竖栏板块过滤内容-----------------------------------")
    filter_reel_item_by_span(soup, sensitive_words)
    print("\n-------------------------------他人在看板块过滤内容---------------------------------")
    filter_video_renderer_by_aria_label(soup, sensitive_words)
    modified_html = str(soup)  # 将BeautifulSoup对象转换回字符串
    modified_soup = modified_html
    # print(modified_html)
    # if "台湾" in modified_html:
    #     print("wqerqwerwqr")
    #     modified_html = modified_html.replace('台湾',"我靠")
    return jsonify({'html': modified_html})
if __name__ == '__main__':
    app.run(debug=True,port=24464)

