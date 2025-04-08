from openai import OpenAI
import write_in
import os
import datetime

client = OpenAI(
    api_key="sk-dmJbSErTWxkcoo6JFO7Iuhmw3EPInwMmgt4APN44jNqv7LRg",
    base_url="https://a.fe8.cn/v1"
)

def read_va_file():
    """安全读取文件并创建备份"""
    src_file = r"C:\Users\朱权海\Desktop\llm\PMAMTJ40_4_5\modelPMAMTJ\veriloga\veriloga.va"
    backup_dir = r"C:\Users\朱权海\Desktop\llm\PMAMTJ40_4_5\modelPMAMTJ\veriloga\backup"

    try:
        # 创建备份目录
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # 生成带时间戳的备份文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        backup_file = f"veriloga_backup_{timestamp}.va"
        
        # 使用write_in的文件复制功能
        write_in.file_copy(os.path.dirname(src_file), backup_dir, os.path.basename(src_file))
        
        # 重命名备份文件
        src_backup = os.path.join(backup_dir, "veriloga.va")
        write_in.file_rename(backup_dir, "veriloga.va", backup_file)
        
        with open(src_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"文件操作失败：{str(e)}"

def save_corrected_code(content: str):
    """使用write_in函数安全保存修正代码"""
    target_dir = r"C:\Users\朱权海\Desktop\llm\PMAMTJ40_4_5\modelPMAMTJ\veriloga"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
    new_file = f"veriloga_corrected_{timestamp}.va"
    temp_file = "temp_corrected.va"
    
    try:
        # 先写入临时文件
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 使用write_in的文件移动功能
        write_in.file_move(os.getcwd(), target_dir, temp_file)
        
        # 重命名为正式文件名
        src_path = os.path.join(target_dir, temp_file)
        write_in.file_rename(target_dir, temp_file, new_file)
        
        print(f"\n助手：文件已保存至 {os.path.join(target_dir, new_file)}")
        
    except Exception as e:
        print(f"\n文件保存失败：{str(e)}")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

def extract_code(response: str) -> str:
    """增强型代码提取"""
    code_blocks = []
    pos = 0
    while True:
        start = response.find('```', pos)
        if start == -1:
            break
        start += 3
        end = response.find('```', start)
        code = response[start:end].strip() if end != -1 else response[start:].strip()
        code_blocks.append(code)
        pos = end + 3 if end != -1 else len(response)
    return '\n\n'.join(code_blocks)

def chat_session():
    messages = [
        {"role": "system", "content": "请找到代码的错误，并仅输出修改过后的整份代码。"}
    ]
    
    print("专业VA文件分析系统已就绪（输入'分析文件'开始）")
    while True:
        user_input = input("\n您：").strip()
        
        if user_input == '退出':
            break
            
        if user_input == "分析文件":
            content = read_va_file()
            if "失败" in content:
                print(f"\n助手：{content}")
                continue
            user_input = f"请分析并修正以下VA文件，仅输出正确的整份代码：\n{content}"
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                temperature=0.3
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            print(f"\nAPI请求失败：{str(e)}")
            continue
        
        print("\n助手：", ai_response)
        
        if user_input.startswith("请分析并修正"):
            new_code = extract_code(ai_response)
            if new_code:
                save_corrected_code(new_code)
            else:
                print("\n助手：未检测到有效代码块")

        messages.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    chat_session()
