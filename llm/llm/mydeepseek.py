from openai import OpenAI

content = []
desktop_path = "C:\\Users\\Lenovo\\Desktop\\llm\\llm\\PMAMTJ40_4_5\\modelPMAMTJ\\veriloga\\veriloga.va"
if 1 :
    with open(desktop_path, 'r') as f:
        while True:
            chunk = f.read(4096)  # 关键改动：分块读取
            if not chunk:
                break
            content.append(chunk)

content = ''.join(content)

mydeepseek = OpenAI(api_key="sk-b58cd4954ecd43c18c304cfaca0e9a0e", base_url="https://api.deepseek.com")

send_json = [{"role": "system", "content": "你只做一件事,找到.va文件中最主要的五个错误并修复。执行寻找错误并修复这个事情三次,给我三个回复并用中文回复"},
            {"role": "user", "content": content}]

receive = mydeepseek.chat.completions.create(model='deepseek-reasoner',
                                            messages= send_json)
print(receive.choices[0].message.content)