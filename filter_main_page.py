import logging
from tkinter import Tk, messagebox
from bs4 import BeautifulSoup
import os
# os.environ['NO_PROXY']="https://www.bbc.com/zhongwen/simp"
import requests

############# global variable settings ###########################
local_save_path = "./save_webpages"  # 爬取网页保存到本地的位置
deleted_contents_path="./utils/deleted_contents"



def write_html(file_path, file_content, prefix, write_or_not):
    count = 1
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    full_file_path = os.path.join(file_path, f"{prefix}{count}.html")
    while os.path.exists(full_file_path):
        count += 1
        full_file_path = os.path.join(file_path, f"{prefix}{count}.html")

    if write_or_not == 1:
        with open(full_file_path, 'w', encoding='utf-8') as file:
            file.write(file_content)
        logging.info("处理后的网页写入到: %s", full_file_path)
        # print("处理后的网页写入到：", full_file_path)
    return full_file_path

#转换网页链接->文件夹名称
def transfer_link_to_filename(base_url):
    filename_list = list(filter(None, base_url.split("/")))
    # print("filename_list",filename_list)
    filename = ""
    # 检查列表长度，并根据元素的存在构建文件名
    if len(filename_list) > 1 and filename_list[1]:  # 检查第二个元素是否存在且非空
        filename += filename_list[1]
    if len(filename_list) > 2 and filename_list[2]:  # 检查第三个元素是否存在且非空
        filename += "_" + filename_list[2]
    if len(filename_list) > 3 and filename_list[3]:  # 检查第四个元素是否存在且非空
        filename += "_" + filename_list[3]
    return  filename

#获取在线网页内容
def get_content_online(url_path, proxies=None, encoding='utf-8', timeout=5):
    try:
        headers = {'Connection': 'close'}
        if proxies is None:
            response = requests.get(url_path, headers=headers, verify=False, timeout=timeout)
        else:
            response = requests.get(url_path, headers=headers, verify=False, proxies=proxies, timeout=timeout)

        response.encoding = encoding  # 指定编码
        return response
    except requests.exceptions.Timeout:
        logging.info("请求超时")
    except ConnectionError as e:
        logging.info(e)
    except requests.exceptions.RequestException as e:
        logging.info(e)
    # 显示 messagebox 前，创建一个隐藏的 Tkinter 主窗口
    root = Tk()
    root.withdraw()  # 隐藏主窗口
    messagebox.showerror("错误", "无法连接到网站，请检查代理设置或网络连接。")
    root.destroy()  # 销毁主窗口
    return None

#获取在线网页内容并保存到本地
def get_index_html(url,path,proxies):  # 爬虫获取html
    # print("proxies_I_get",proxies)
    # proxies = {
    #     'http': f'http://127.0.0.1:{10809}',
    #     'https': f'http://127.0.0.1:{10809}',
    # }
    # print("proxies_after",proxies)


    response = get_content_online(url, proxies)
    if not response:
        logging.info("请求失败，请检查代理设置或网络连接。")
    html_content = response.text
    if not response:
        logging.info("请求失败，请检查代理设置或网络连接。")
    if response.status_code == 200:
        save_path = save_online_content_to_local(base_url = url,html_content = html_content)
        return save_path
    else:
        logging.info("获取HTML失败，状态码为: %d", response.status_code)
        # print("获取HTML失败，状态码为：", response.status_code)
        return "error status code!"

# 将txt转为列表，黑名单和敏感词导入可用
def import_file_to_list(file_path):
    try:
        with open(file_path, 'r',encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
            return lines
    except FileNotFoundError:
        logging.info("文件未找到！")
        # print("文件未找到！")
        return []

def get_save_path(base_url,path, suffix):
    filename = transfer_link_to_filename(base_url)
    mkdir=os.path.join(path, filename)
    if suffix:
        filename = filename + '.html'
    save_path = os.path.join(path, filename)  # 相对+文件名
    return save_path

def save_online_content_to_local(base_url,html_content):
    save_path = get_save_path(base_url,local_save_path,1)
    # 保存网页内容到文件
    with open(save_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    # print("网页已保存到本地路径：", save_path)

# 对<li>标签的不同情况进行细分，以适应主页不同板块结构
def remove_tags_with_prohibited_words(soup,prohibited_words):
    # <li>下<span>标签过滤
    for span in soup.find_all('span'):
        if any(word in span.get_text() for word in prohibited_words):
            parent_li = span.find_parent('li')
            if parent_li:
                with open(deleted_contents_path, 'a') as file:
                    file.write("删除的标签内容:\n")
                    file.write(parent_li.prettify())
                    file.write("\n")
                parent_li.extract()

    # <li>下<a><p>标签过滤
    for li in soup.find_all('li'):
        h3_tag = li.find('h3')
        a_tag = li.find('a')
        p_tag = li.find('p')
        if (a_tag and any(word in a_tag.get_text() for word in prohibited_words)) or (p_tag and any(word in p_tag.get_text() for word in prohibited_words)):
            with open("deleted_contents", 'a') as file:
                file.write("删除的标签内容:\n")
                file.write(li.prettify())
                file.write("\n")
            li.extract()

    # 热看板块过滤
    target_class = 'bbc-iinl4t euhul101'
    divs = soup.find_all('div', class_=target_class)
    for div in divs:
        for li in div.find_all('li'):
            a_tag = li.find('a')
            if a_tag and any(word in a_tag.get_text() for word in prohibited_words):
                with open("deleted_contents", 'a') as file:
                    file.write("删除的标签内容:\n")
                    file.write(li.prettify())
                    file.write("\n")
                li.extract()
    return soup
