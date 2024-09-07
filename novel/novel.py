import requests
from bs4 import BeautifulSoup
import time
import re
import os


# 網站特定的選擇器
SITE_SELECTORS = {
    0: {  # 小說狂人
        'title': {'tag': 'div', 'class': 'name'},
        'content': {'tag': 'div', 'class': 'content'},
        'next_page': None,
        'next_chapter': {'tag': 'a', 'class': 'next-chapter'}
    },
    1: {  # 第一文學
        'title': {'tag': 'h1', 'class': 'title'},
        'content': {'tag': 'div', 'class': 'content'},
        'next_page': {'tag': 'a', 'string': '下一页'},
        'next_chapter': {'tag': 'a', 'string': '下一章'}
    }
}

def get_element(soup, tag, **kwargs):
    return soup.find(tag, **kwargs)

def scrape_page(url, selectors):
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"無法獲取 {url}: 狀態碼 {response.status_code}")
        return None, None, None, None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title_div = get_element(soup, selectors['title']['tag'], class_=selectors['title']['class'])
    content_div = get_element(soup, selectors['content']['tag'], class_=selectors['content']['class'])
    next_page = get_element(soup, selectors['next_page']['tag'], string=selectors['next_page']['string']) if selectors['next_page'] else None
    
    # 處理 next_chapter 的查找
    if 'class' in selectors['next_chapter']:
        next_chapter = get_element(soup, selectors['next_chapter']['tag'], class_=selectors['next_chapter']['class'])
    else:
        next_chapter = get_element(soup, selectors['next_chapter']['tag'], string=selectors['next_chapter']['string'])
    
    if not title_div or not content_div:
        print(f"無法找到標題或內容在 {url}")
        return None, None, None, None

    title = title_div.get_text(strip=True)
    content = content_div.get_text(separator='\n')  # 保留原始換行符

    # 移除脚本和样式内容
    content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL)
    
    next_page_url = next_page['href'] if next_page else None
    next_chapter_url = next_chapter['href'] if next_chapter else None
    
    return title, content, next_page_url, next_chapter_url


def get_full_url(base_url, href):
    # 構建完整的URL
    if href.startswith('/'):
        link = base_url + href
    elif href.startswith('http'):
        link = href
    else:
        link = base_url + '/' + href.lstrip('/')

    # 移除重複的 'https://' 部分
    if '//' in link:
        parts = link.split('//', 2)  # 只分割兩次，確保只處理第一次重複的部分
        if len(parts) > 2:
            link = parts[0] + '//' + parts[2]  # 重新組合URL，去掉多餘的部分

    return link


def scrape_novel(start_url, output_file, site_choice):
    if site_choice in [0, 1]:
        selectors = SITE_SELECTORS[site_choice]
    else:
        # 使用自定義選擇器
        selectors = {
            'title': {'tag': input("標題標籤 (默認 h1): ") or 'h1', 'class': input("標題類名 (默認 title): ") or 'title'},
            'content': {'tag': input("內容標籤 (默認 div): ") or 'div', 'class': input("內容類名 (默認 content): ") or 'content'},
            'next_page': {'tag': input("下一頁標籤 (默認 a): ") or 'a', 'string': input("下一頁文字 (默認 下一页): ") or '下一页'},
            'next_chapter': {'tag': input("下一章標籤 (默認 a): ") or 'a', 'string': input("下一章文字 (默認 下一章): ") or '下一章'}
        }
    
    base_url = 'https://' + start_url.split('/')[2]
    current_url = start_url
    current_chapter_title = None
    current_chapter_content = ""
    chapter_count = 0

    with open(output_file, mode='w', encoding='utf-8') as output:
        while current_url:
            print(f"正在抓取: {current_url}")
            title, content, next_page_url, next_chapter_url = scrape_page(current_url, selectors)
            
            if title and content:
                if title != current_chapter_title:
                    # 新的章節開始
                    if current_chapter_title:
                        # 寫入上一章的內容
                        formatted_content = f"# {current_chapter_title}\n\n{current_chapter_content}\n\n"
                        output.write(formatted_content)
                        print(f"已添加: {current_chapter_title}")
                        chapter_count += 1
                    current_chapter_title = title
                    current_chapter_content = content
                else:
                    # 同一章節的下一頁
                    current_chapter_content += "\n" + content

            if next_page_url:
                current_url = get_full_url(base_url, next_page_url)
            elif next_chapter_url:
                # 寫入當前章節並移動到下一章
                formatted_content = f"# {current_chapter_title}\n\n{current_chapter_content}\n\n"
                output.write(formatted_content)
                print(f"已添加: {current_chapter_title}")
                chapter_count += 1
                current_url = get_full_url(base_url, next_chapter_url)
                current_chapter_title = None
                current_chapter_content = ""
            else:
                # 沒有下一頁也沒有下一章，結束抓取
                if current_chapter_title:
                    formatted_content = f"# {current_chapter_title}\n\n{current_chapter_content}\n\n"
                    output.write(formatted_content)
                    print(f"已添加: {current_chapter_title}")
                    chapter_count += 1
                current_url = None

            time.sleep(1)  # 添加延遲以避免過於頻繁的請求

    return chapter_count

def get_novel_info(url, site_choice):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.content, 'html.parser')
        base_url = '/'.join(url.split('/')[:3])  # 獲取基礎 URL

        if site_choice == 0:  # 小說狂人
            # 找到目錄頁鏈接
            catalog_link = soup.select_one('div.position a[href*="/n/"]')
            if catalog_link:
                catalog_url = get_full_url(base_url, catalog_link['href'])
                catalog_response = requests.get(catalog_url)
                if catalog_response.status_code == 200:
                    catalog_soup = BeautifulSoup(catalog_response.content, 'html.parser')
                    title = catalog_soup.select_one('div.info span.title')
                    author = catalog_soup.select_one('div.info span.author a')
                    if title and author:
                        return title.text.strip('《》'), author.text.strip()

        elif site_choice == 1:  # 第一文學
            # 找到目錄頁鏈接
            catalog_link = soup.select_one('div.section-opt a[href*="/xiaoshuo/"]')
            if catalog_link:
                catalog_url = get_full_url(base_url, catalog_link['href'])
                catalog_response = requests.get(catalog_url)
                if catalog_response.status_code == 200:
                    catalog_soup = BeautifulSoup(catalog_response.content, 'html.parser')
                    title = catalog_soup.select_one('div.top h1')
                    author = catalog_soup.select_one('div.top div.fix p:first-of-type')
                    if title and author:
                        return title.text.strip(), author.text.replace('作者：', '').strip()

        return None, None
    except Exception as e:
        print(f"獲取小說信息時發生錯誤: {e}")
        return None, None

def get_user_input_novel_info():
    novel_title = input("請輸入小說名稱: ")
    novel_author = input("請輸入作者名稱: ")
    return novel_title, novel_author

def main():
    start_url = input("請輸入小說起始頁的URL: ")
    
    # 選擇網站
    site_choice = input("選擇網站 (0: 小說狂人, 1: 第一文學, 2: 其他，默認為 1): ")
    site_choice = int(site_choice) if site_choice in ['0', '1', '2'] else 1
    
    # 嘗試自動獲取小說信息
    novel_title, novel_author = get_novel_info(start_url, site_choice)
    
    # 如果自動獲取失敗，詢問用戶
    if not novel_title or not novel_author:
        print("無法自動獲取小說信息。請手動輸入。")
        novel_title, novel_author = get_user_input_novel_info()
    
    output_file = f'《{novel_title}》{novel_author}.txt'
    output_file = "".join(c for c in output_file if c.isalnum() or c in (' ', '《', '》', '.')).rstrip()
    
    chapter_count = scrape_novel(start_url, output_file, site_choice)
    print(f"小說《{novel_title}》已抓取完成，共 {chapter_count} 章，並保存到 '{output_file}'。")

if __name__ == '__main__':
    main()


