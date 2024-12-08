
############# global variable settings ###########################
deleted_contents_path="./utils/deleted_contents"

# 是否含违禁词
def contains_prohibited_words(tag, prohibited_words):
    for word in prohibited_words:
        if word in tag.text:
            return True
    return False


# 侧栏过滤函数
def filter_detail_page(soup,prohibited_words):
    # 只处理特定的 <li> 标签
    for li in soup.find_all('li'):
        if li.find_all('li'):
            continue  # If li contains other lis, skip it
        if contains_prohibited_words(li, prohibited_words):
            with open(deleted_contents_path, 'a') as file:
                file.write("删除的标签内容:\n")
                file.write(li.prettify())
                file.write("\n")
            li.extract()

    # 只处理特定的 <div> 标签
    for div in soup.find_all('div'):
        if div.find_all('div'):
            continue  # If li contains other lis, skip it
        if contains_prohibited_words(div, prohibited_words):
            with open(deleted_contents_path, 'a') as file:
                file.write("删除的标签内容:\n")
                file.write(div.prettify())
                file.write("\n")
            div.extract()

    # 热看板块过滤
    target_class = 'bbc-iinl4t euhul101'
    divs = soup.find_all('div', class_=target_class)
    for div in divs:
        for li in div.find_all('li'):
            a_tag = li.find('a')
            if a_tag and any(word in a_tag.get_text() for word in prohibited_words):
                with open(deleted_contents_path, 'a') as file:
                    file.write("删除的标签内容:\n")
                    file.write(li.prettify())
                    file.write("\n")
                li.extract()
    return soup

# 根据blacklist.txt，删除href标签，不可能修改源码，测试的时候可以用
def remove_href(soup, hrefs_to_remove):
    for black_href in hrefs_to_remove:  # 遍历黑名单

        # 找到所有带有指定href的标签
        tags_with_href = soup.find_all(href=black_href)

        # 从BeautifulSoup对象中删除这些标签
        for tag in tags_with_href:
            tag.decompose()
    # 返回修改后的HTML内容
    return str(soup)
