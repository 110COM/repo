import re
import time
import asyncio
import aiohttp
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def setup_browser():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--window-size=720,720')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36")
    options.page_load_strategy = 'none'
    
    browser = webdriver.Chrome(options=options)
    return browser

def fetch_page_data(browser, urls):
    ip_pattern = re.compile(r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+")
    found_ips = set()
    
    for url in urls:
        try:
            print(f"Fetching {url}...")
            browser.get(url)
            time.sleep(10)  # 等待页面加载，这里简单粗暴地等待固定时间
            page_source = browser.page_source
            ips = ip_pattern.findall(page_source)
            if ips:
                print(f"Found IPs for {url}:")
                for ip in ips:
                    print(ip)
                    found_ips.add(ip)
            else:
                print(f"No IPs found for {url}.")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    
    return found_ips

async def process_json_data(sem, session, url):
    async with sem:
        try:
            async with session.get(url, timeout=120) as response:
                if response.status != 200:
                    print(f"请求发生错误，跳过 {url}")
                    return []

                json_data = await response.json()
                processed_data = []
                if isinstance(json_data, dict) and 'data' in json_data:
                    for item in json_data['data']:
                        if isinstance(item, dict):
                            name = item.get('name')
                            urlx = item.get('url')
                            if ',' in urlx:
                                urlx = urlx.replace(',', 'aaaaaaaa')

                            if "购" in name or "酒店" in name or "视频" in name or "推荐" in name:
                                continue

                            name = name.replace("cctv", "CCTV")
                            name = name.replace("中央", "CCTV")
                            name = name.replace("央视", "CCTV")
                            name = name.replace("高清", "")
                            name = name.replace("Tel", "")
                            name = name.replace("超高", "")
                            name = name.replace("测试", "")
                            name = name.replace("HD", "")
                            name = name.replace("标清", "")
                            name = name.replace("频道", "")
                            name = name.replace("-", "")
                            name = name.replace("—", "")
                            name = name.replace(" ", "")
                            name = name.replace("PLUS", "+")
                            name = name.replace("＋", "+")
                            name = name.replace("(", "")
                            name = name.replace(")", "")
                            name = re.sub(r"CCTV(\d+)台", r"CCTV\1", name)
                            name = name.replace("CCTV1综合", "CCTV1")
                            name = name.replace("CCTV2财经", "CCTV2")
                            name = name.replace("CCTV3综艺", "CCTV3")
                            name = name.replace("CCTV4国际", "CCTV4")
                            name = name.replace("CCTV4中文国际", "CCTV4")
                            name = name.replace("CCTV4欧洲", "CCTV4")
                            name = name.replace("CCTV5体育", "CCTV5")
                            name = name.replace("CCTV6电影", "CCTV6")
                            name = name.replace("CCTV7军事", "CCTV7")
                            name = name.replace("CCTV7军农", "CCTV7")
                            name = name.replace("CCTV7农业", "CCTV7")
                            name = name.replace("CCTV7国防军事", "CCTV7")
                            name = name.replace("CCTV8电视剧", "CCTV8")
                            name = name.replace("CCTV9记录", "CCTV9")
                            name = name.replace("CCTV9纪录", "CCTV9")
                            name = name.replace("CCTV10科教", "CCTV10")
                            name = name.replace("CCTV11戏曲", "CCTV11")
                            name = name.replace("CCTV12社会与法", "CCTV12")
                            name = name.replace("CCTV12法制", "CCTV12")
                            name = name.replace("CCTV13新闻", "CCTV13")
                            name = name.replace("CCTV新闻", "CCTV13")
                            name = name.replace("CCTV14少儿", "CCTV14")
                            name = name.replace("CCTV少儿", "CCTV14")
                            name = name.replace("CCTV15音乐", "CCTV15")
                            name = name.replace("CCTV16奥林匹克", "CCTV16")
                            name = name.replace("CCTV17农业农村", "CCTV17")
                            name = name.replace("CCTV17农业", "CCTV17")
                            name = name.replace("CCTV17农村", "CCTV17")
                            name = name.replace("CCTV5+体育赛视", "CCTV5+")
                            name = name.replace("CCTV5+体育赛事", "CCTV5+")
                            name = name.replace("CCTV5+体育", "CCTV5+")
                            name = name.replace("上海东方卫视", "东方卫视")
                            name = name.replace("福建东南卫视", "东南卫视")
                            name = name.replace("CETV1", "中国教育1")
                            name = name.replace("CETV4", "中国教育4")

                            # 添加
                            if name in ["广西", "湖南", "东方", "北京", "浙江", "江苏", "深圳", "天津", "山东", "湖北", "上海", "东南", "吉林", "四川", "安徽", "广东", "辽宁", "重庆", "黑龙江", "东方", "云南", "广西", "河北", "海南", "甘肃", "贵州", "陕西", "青海"]:
                                name = name + "卫视"

                            if 'udp' in urlx or 'rtp' in urlx or '宣传' in urlx:
                                continue

                            processed_data.append((name, urlx))
                
                return processed_data
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return []

async def main():
    urls = [   
        "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22hebei%22",        #河北
       "https://www.zoomeye.org/searchResult?q=%2Fiptv%2Flive%2Fzh_cn.js%20%2Bcountry%3A%22CN%22%20%2Bsubdivisions%3A%22beijing%22",   #北京
        
    ]  # 替换成您想访问的URLs

    browser = setup_browser()
    unique_ips = fetch_page_data(browser, urls)
    browser.quit()

    processed_urls = [f"{ip}/iptv/live/1000.json?key=txiptv" for ip in unique_ips]
    
    processed_data = []

    sem = asyncio.Semaphore(50)  # 限制并发数量为50
    async with aiohttp.ClientSession() as session:
        tasks = [process_json_data(sem, session, url) for url in processed_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result, url in zip(results, processed_urls):
            if result is None:      # 如果无法解析JSON数据，则跳过该请求的处理
                continue

            X = re.search(r'http://(.*?)/', url).group(1)  # 使用正则表达式提取IP地址部分
            for name, urlx in result:
                if 'http' in urlx:
                    processed_data.append((name, urlx))  # 将数据添加到列表中
                else:
                    processed_data.append((name, f'http://{X}{urlx}'))  # 如果不包含http，则添加完整IP地址
        
    # 打印生成的数据，根据是否包含http选择不同的格式
    for name, urlx in processed_data:
        print(f"{name},{urlx}")

    # 将处理后的数据写入文件
    #script_dir = os.path.dirname(os.path.abspath(__file__))
    #output_file_path = os.path.join(script_dir, 'itv.txt')
	  output_file_path = f"jiee/itv.txt"
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for name, urlx in processed_data:
            file.write(f"{name},{urlx}\n")  # 写入不同格式的数据到文件

    print("数据已打印和写入文件。")



if __name__ == "__main__":
    asyncio.run(main())
