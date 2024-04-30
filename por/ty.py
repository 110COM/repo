import os
import random

def get_lines_containing_keyword(file_content, keyword):
    lines = file_content.split('\n')
    keyword_lines = [(line.strip(), index) for index, line in enumerate(lines) if keyword in line]
    return keyword_lines

def get_next_line(lines):
    if lines:
        selected_line, line_number = random.choice(lines)
        #print(f"随机选择的行号：{line_number}")
        return selected_line, line_number
    else:
        return None, None

def read_file_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    return file_content

def main():
	
    du_file_path = f"a/cts8" 
    ce_file_path = f"a/ce.m3u"    


    # 读取 du 文件内容
    du_content = read_file_content(du_file_path)

    # 从 du 文件内容中找到所有含有 CCTV2 的行
    cctv2_lines = get_lines_containing_keyword(du_content, 'CCTV2')
    #print(f"CCTV2 关键词所在行号：{[line[1] for line in cctv2_lines]}")

    # 从中随机选择一行
    selected_line, selected_line_number = get_next_line(cctv2_lines)
    if selected_line is not None:
        # 获取选定行的下一行数据
        next_line = get_next_line_after_selected_line(du_content, selected_line_number)
        if next_line is not None:
            #print(f"要替换 ce 文件数据的行号：{13}")
            #print(f"要替换 ce 文件数据的内容：{next_line}")
            replace_line(ce_file_path, 13, next_line)

    # 从 du 文件内容中找到所有含有 CCTV7 的行
    cctv7_lines = get_lines_containing_keyword(du_content, 'CCTV7')
    print(f"CCTV7 关键词所在行号：{[line[1] for line in cctv7_lines]}")

    # 从中随机选择一行
    selected_line, selected_line_number = get_next_line(cctv7_lines)
    if selected_line is not None:
        # 获取选定行的下一行数据
        next_line = get_next_line_after_selected_line(du_content, selected_line_number)
        if next_line is not None:
            #print(f"要替换 ce 文件数据的行号：{15}")
            #print(f"要替换 ce 文件数据的内容：{next_line}")
            replace_line(ce_file_path, 15, next_line)

def get_next_line_after_selected_line(file_content, selected_line_number):
    lines = file_content.split('\n')
    # 找到选定行之后的第一个非空行
    for i in range(selected_line_number + 1, len(lines)):
        next_line = lines[i].strip()
        # 忽略注释行
        if next_line and not next_line.startswith('#'):
            return next_line
    print("选定行的下一行不存在。")
    return None

def replace_line(file_path, line_number, new_content):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if line_number <= len(lines):
            lines[line_number - 1] = new_content + '\n'
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
        else:
            print(f"文件 {file_path} 不包含第 {line_number} 行。")
    except FileNotFoundError:
        print(f"未找到文件：{file_path}")

if __name__ == "__main__":
    main()
