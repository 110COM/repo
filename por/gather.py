import requests
import os
import re
import aiohttp
import asyncio
import subprocess
import json


urls = [
    #"https://raw.githubusercontent.com/longlonglaile2/tv/main/itv.txt",
    "https://raw.githubusercontent.com/GOgo8Go/env/main/itv.txt",
    #"http://example3.com"
]


keywords = ["udp", "rtp", "aaaaa", "购", "推荐", "宣传", "酒店", "视频", "新疆卫视", "西藏卫视", "星空卫视", "/PLTV/", "chinamobile", "广场舞"]


def fetch_content(url, timeout=10):
    print(f"正在访问页面: {url}")
    try:
        response = requests.get(url, timeout=timeout)
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        print(f"获取 {url} 时出错: {e}")
        return None


def filter_content(content, keywords):
    lines = content.split('\n')
    filtered_lines = [line for line in lines if not any(keyword in line for keyword in keywords)]
    return '\n'.join(filtered_lines)


def get_resolution(name, url, timeout=15):
    process = None
    try:
        cmd = ['ffprobe', '-print_format', 'json', '-show_streams', '-select_streams', 'v', url]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=timeout)
        info = json.loads(stdout.decode())
        width = int(info['streams'][0]['width'])
        height = int(info['streams'][0]['height'])
        if width >= 1920 and height >= 1080:
            return name, url
    except subprocess.TimeoutExpired:
        process.kill()
    except Exception as e:
        pass
    finally:
        if process:
            process.wait()
    return None


async def check_url(name, url, session):
    try:
        async with session.get(url, timeout=1) as response:
            if response.status == 200:
                return name, url
    except Exception as e:
        #print(f"检查 {url} 时出错: {e}")
        pass
    return None


async def check_url_with_semaphore(name, url, session, semaphore):
    async with semaphore:
        return await check_url(name, url, session)


async def process_urls(name_url_pairs, max_concurrent_requests=100):
    print("正在检测所有URL的有效性")
    async with aiohttp.ClientSession() as session:
        tasks = []
        semaphore = asyncio.Semaphore(max_concurrent_requests)  # 限制并发请求数量

        # 创建任务
        for name, url in name_url_pairs:
            
            if name.isdigit():
                continue
                
            # 修改 name
            name = name.replace("奥运匹克", "")
            name = name.replace("军农", "")
            name = name.replace("上海东方卫视", "东方卫视")
            name = name.replace("冬奥纪实", "纪实科教")
            name = name.replace("BTV纪实科教", "纪实科教")
            name = name.replace("上海纪实", "纪实人文")
            name = name.replace("福建东南卫视", "东南卫视")
            name = name.replace("湖南金鹰卡通", "金鹰卡通")
            name = name.replace("金鹰卡通卫视", "金鹰卡通")
            
            name = re.sub(r'\b怀旧剧场\b', 'CCTV怀旧剧场', name)
            name = re.sub(r'\b第一剧场\b', 'CCTV第一剧场', name)
            name = re.sub(r'\b世界地理\b', 'CCTV世界地理', name)
            name = re.sub(r'\b风云音乐\b', 'CCTV风云音乐', name)
            name = re.sub(r'\b风云剧场\b', 'CCTV风云剧场', name)
            name = re.sub(r'\b女性时尚\b', 'CCTV女性时尚', name)
            name = re.sub(r'\bCCTV文化\b', 'CCTV文化精品', name)
            name = re.sub(r'\b中国教育4\b', 'CETV4', name)
            name = re.sub(r'\b茶\b', '茶频道', name)
            name = re.sub(r'\b长影\b', '长影频道', name)
            name = re.sub(r'\b金色\b', '金色学堂', name)
            
            name = re.sub(r'\b家庭影院\b', 'CHC家庭影院', name)
            name = re.sub(r'\b(?:电影|CHC电影)\b', 'CHC影迷电影', name)
            
            name = re.sub(r'\b(?:兵器|兵器科技|CCTV兵器)\b', 'CCTV兵器科技', name)
            name = re.sub(r'\b(?:台球|央视台球|CCTV台球)\b', 'CCTV央视台球', name)
            name = re.sub(r'\b(?:足球|风云足球|CCTV足球)\b', 'CCTV风云足球', name)
            name = re.sub(r'\b(?:高尔夫|高尔夫网球)\b', 'CCTV高尔夫网球', name)
            name = re.sub(r'\b(?:世界地理|地理世界)\b', 'CCTV世界地理', name)
            name = re.sub(r'\b(?:教育一套|中国教育|中国教育1|中国教育电视台)\b', 'CETV1', name)
            
            name = re.sub(r'\b(?:珠江台|珠江卫视)\b', '广东珠江', name)
            name = re.sub(r'\b(?:南方卫视|广东南方卫视)\b', '大湾区卫视', name)
            
            if name in ["广西", "湖南", "东方", "北京", "浙江", "江苏", "深圳", "天津", "山东", "湖北", "上海", "东南", "吉林", "四川", "安徽", "广东", "辽宁", "重庆", "黑龙江", "东方", "云南", "广西", "河北", "海南", "甘肃", "贵州", "陕西", "青海"]:
                name = name + "卫视"
            
            
            task = check_url_with_semaphore(name, url, session, semaphore)
            tasks.append(task)

        # 执行所有任务
        valid_urls = await asyncio.gather(*tasks)
        return [result for result in valid_urls if result is not None]


async def check_resolution_with_semaphore(name, url, semaphore):
    async with semaphore:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, get_resolution, name, url)
        return result


async def process_resolutions(name_url_pairs, max_concurrent_requests=30):
    print("正在检测所有URL的分辨率")
    tasks = []
    semaphore = asyncio.Semaphore(max_concurrent_requests)  # 限制并发请求数量

    # 创建任务
    for name, url in name_url_pairs:
        task = check_resolution_with_semaphore(name, url, semaphore)
        tasks.append(task)

    # 执行所有任务
    valid_resolutions = await asyncio.gather(*tasks)
    return [result for result in valid_resolutions if result is not None]


all_filtered_content = []
for url in urls:
    content = fetch_content(url)
    if content:
        filtered_content = filter_content(content, keywords)
        all_filtered_content.append(filtered_content)


final_content = "\n".join(all_filtered_content)


unique_lines = set(final_content.split('\n'))
final_content = "\n".join(unique_lines)



name_url_pairs = []
for line in final_content.split('\n'):
    if ',' in line:
        name, url = line.split(',', 1)
        name_url_pairs.append((name.strip(), url.strip()))


valid_name_url_pairs = asyncio.run(process_urls(name_url_pairs))


valid_name_url_resolutions = asyncio.run(process_resolutions(valid_name_url_pairs))



with open("jiee/gather", 'a', encoding='utf-8') as file:
    for name, url in valid_name_url_resolutions:
        line = f"{name},{url}"
        #print(line)
        file.write(line + "\n")



with open("jiee/gather", 'r', encoding='utf-8') as file:
    lines = file.readlines()

unique_lines = list(dict.fromkeys(line.strip() for line in lines))

with open("jiee/gather", 'w', encoding='utf-8') as file:
    for line in unique_lines:
        file.write(line + "\n")


print(f"有效数据已写入")
