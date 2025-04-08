import requests
import json
import os
import re

# 配置参数
INPUT_FOLDER = r"C:\\Users\\Lenovo\Desktop\\llm\\sotmodel\\"
DESCRIPTION_PATH = os.path.join(INPUT_FOLDER, "explanation.txt")
DEEPSEEK_API_KEY = "sk-b58cd4954ecd43c18c304cfaca0e9a0e"
API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-reasoner"

def get_sorted_va_files(folder_path):
    #获取按数字排序的Verilog-A文件列表
    va_files = []
    pattern = re.compile(r'SOT(\d+)\.va$', re.IGNORECASE)
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            match = pattern.match(filename)
            if match:
                num = int(match.group(1))
                va_files.append((num, file_path))
    
    # 按数字升序排列
    va_files.sort(key=lambda x: x[0])
    return [file[1] for file in va_files]

def read_large_file(file_path):
    #读取文件内容，自动处理编码
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='gbk') as file:
            return file.read()

def analyze_single_file(verilog_path, description_path):
    #分析单个Verilog-A文件
    try:
        verilog_content = read_large_file(verilog_path)
        description_content = read_large_file(description_path)
    except IOError as e:
        print(f"文件读取错误: {str(e)}")
        return None

    system_prompt = """You are a professional hardware design engineer with expertise in Verilog-A code analysis and debugging. Based on the code and descriptions provided by the user, please:
    1.Analyze syntax and semantic errors in the code
    2.Check for any electrical characteristics errors in the code
    3.Provide specific modification suggestions
    4.Include COMPLETE corrected code in ```verilog block
    Please list the issues in bullet points and provide corrected code examples,MUST include COMPLETE corrected code in ```verilog code block!"""

    user_prompt = f"""Please analyze the following VerilogA code:
    [Description of design]
    {description_content}

    [Code to be reviewed]
    {verilog_content}

    Please respond in the following format:
    1.Code Issue Analysis
    2.Modification Recommendations
    3.Complete Corrected Code"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 4096
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API请求失败: {str(e)}")
        return None

def process_all_files():
    #处理所有符合条件的文件
    va_files = get_sorted_va_files(INPUT_FOLDER)
    
    if not va_files:
        print("未找到符合命名规则的Verilog-A文件")
        return

    print(f"找到 {len(va_files)} 个待处理文件")
    
    for idx, va_file in enumerate(va_files, 1):
        print(f"\n{'='*40}")
        print(f"正在处理第 {idx}/{len(va_files)} 个文件：{os.path.basename(va_file)}")
        
        result = analyze_single_file(va_file, DESCRIPTION_PATH)
        
        if result and 'choices' in result and result['choices']:
            analysis = result['choices'][0]['message']['content']
            print(f"\n分析结果:\n{analysis}")
            
            # 保存分析结果到文件
            output_file = os.path.join(INPUT_FOLDER, f"analysis_{idx}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(analysis)
            print(f"分析结果已保存至：{output_file}")
        else:
            print("未收到有效响应")

if __name__ == "__main__":
    process_all_files()