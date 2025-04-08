from openai import OpenAI
import write_in

client = OpenAI(
    api_key="sk-dmJbSErTWxkcoo6JFO7Iuhmw3EPInwMmgt4APN44jNqv7LRg",
    base_url="https://a.fe8.cn/v1"
)

def read_va_file():
    """分块读取大文件（每次4KB）"""
    desktop_path = "C:\\Users\\Lenovo\\Desktop\\llm\\llm\\PMAMTJ40_4_5\\modelPMAMTJ\\veriloga\\veriloga.va"
    try:
        content = []
        with open(desktop_path, 'r') as f:
            while True:
                chunk = f.read(4096)  # 关键改动：分块读取
                if not chunk:
                    break
                content.append(chunk)
        return ''.join(content)
    except:
        return "文件读取失败，请确认桌面存在veriloga.va文件"
        
def chat_session():
    messages = [
        {"role": "system", "content": "你只做一件事：当用户说'分析文件'时，帮助用户分析代码"}
    ]
    
    print("文件分析助手已就绪（输入'分析文件'开始）")
    while True:
        user_input = input("\n您：").strip()
        
        if user_input == '退出':
            break
            
        # 核心文件处理逻辑
        if user_input == "分析文件":
            content = read_va_file()
            user_input = "请分析以下verilogA代码中有哪些部分与高低阻态相关\n" + content
            
        messages.append({"role": "user", "content": user_input})
        

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.3
        )
        print(response)
        ai_response = response.choices[0].message.content
        print("\n助手：", ai_response)
        messages.append({"role": "assistant", "content": ai_response})

if __name__ == "__main__":
    chat_session()
