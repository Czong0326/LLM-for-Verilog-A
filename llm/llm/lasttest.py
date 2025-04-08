import requests
import json
import os
import re
import time
import difflib

# 配置参数
INPUT_FOLDER = r"D:\\llm\\sotmodel\\"
CORRECT_CODE_PATH = os.path.join(INPUT_FOLDER, "correct.va")
DESCRIPTION_PATH = os.path.join(INPUT_FOLDER, "explanation.txt")
DEEPSEEK_API_KEY = "sk-b58cd4954ecd43c18c304cfaca0e9a0e"
API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-reasoner"
MAX_RETRIES = 4  # 最大重试次数

# 用户自定义错误列表
USER_ERRORS = [

    {
        "error_type": "Logical Operator Error",
        "description": "Misuse of logical operators, such as confusing AND/OR."
    },
    {
        "error_type": "Premature Termination",
        "description": "Missing semicolon when defining a module, for example, a line of code is written as 'module diode_circuit', which lacks a semicolon."
    },
    {
        "error_type": "Variable Type Error",
        "description": "Incorrect variable type when defining variables, for example, writing 'analog begin' as 'vanlog begin'."
    },
    {
        "error_type": "Variable Name Error",
        "description": "In subsequent code, the variable name is different from the one defined earlier, which may involve adding, omitting, or changing characters. For example, the variable name 'pos.V' is incorrectly written as 'pos.v'."
    },
    {
        "error_type": "Assignment Symbol Error",
        "description": "In assignment code, there is a misuse of <= and <+. <= is used for procedural assignment to simulate the behavior of digital logic and sequential logic; <+ is used for continuous assignment to simulate the physical behavior of analog circuits. Misusing these two symbols will lead to model errors."
    },
    {
        "error_type": "Incomplete Syntax Structure",
        "description": "For example, the 'end' or 'begin' in the 'begin...end' structure is missing."
    },
    {
        "error_type": "Macro Call Error",
        "description": "When calling a macro in subsequent code, the backtick (`) before the macro keyword is omitted. For example, 'sqrt' is written without the backtick, resulting in the macro not being called correctly."
    },
    {
        "error_type": "Voltage Representation Error in Analog",
        "description": "The symbol for representing voltage should be V() instead of U()."
    },
    {
        "error_type": "Error in Getting Current Time",
        "description": "The '$' is forgotten when getting the current time. For example, 'current_time = $time' is written as 'current_time = time;'."
    },
    {
        "error_type": "Cross Function Usage Error",
        "description": "In the use of the 'cross' function, the meanings of 1 and -1 are confused (for example, when detecting from below the threshold to above the threshold), or the number of parameters of the 'cross' function is incorrect."
    },
    {
        "error_type": "`include, `define Usage Error",
        "description": "When using `include or `define, the file name or macro name in the parentheses is misspelled, or the '`' symbol is missing before the misspelled 'include' or 'define' keyword."
    },
    {
        "error_type": "Physical Constant Value Error",
        "description": "The values of constants such as 'e' and 'Kb' are incorrect. For example, 'e' is wrongly written as '1.6e-20'."
    },
    {
        "error_type": "Shape Parameter Error",
        "description": "The size definitions of device shape parameters such as 'rec', 'ellip', and 'circle' are incorrect."
    },
    {
        "error_type": "Physical Constant Value Error",
        "description": "The values of constants such as 'e' and 'Kb' are incorrect. For example, 'e' is wrongly written as '1.6e-20'."
    },
    {
        "error_type": "Confusing Calculation Formulas for Different Shapes",
        "description": "The calculation formulas for 'shape1' and 'shape2' are different, but they are used interchangeably in the code."
    },
    {
        "error_type": "Confusing Equality and Assignment",
        "description": "In the 'if' statement, '==' and '=' are used interchangeably."
    },
    {
        "error_type": "Temperature Judgment Condition Error",
        "description": "There is a misunderstanding of 'temp_var'. In the 'if' statement, 'temp_var' should be a temperature variable, not a boolean variable."
    },
    {
        "error_type": "Confusing DC and AC Analysis",
        "description": "DC analysis is mistaken for AC analysis. For example, 'if(analysis(\"dc\"))' is wrongly written as 'if(analysis(\"ac\"))'."
    },
    {
        "error_type": "Threshold Error",
        "description": "The threshold setting is not practical. For example, '@(above(Id - IcP, +1))' is wrongly written as '@(above(Id - IcP, -1))'."
    },
    {
        "error_type": "Port Declaration Error",
        "description": "A bidirectional port is declared as a unidirectional port. For example, 'inout Duration' is wrongly written as 'input Duration'."
    },
    {
        "error_type": "Vc Calculation Formula Error",
        "description": "Vc = T2 - T1 is wrongly written as Vc = T1 - T2."
    },
    {
        "error_type": "Confusing Parallel and Anti - Parallel Resistors",
        "description": "The resistances of parallel and anti - parallel states are different, but they are confused."
    },
    {
        "error_type": "Initial Value Assignment Error for MTJ Magnetization Direction",
        "description": "During DC analysis, the initial value is assigned as the steady state; during transient analysis, the initial value is assigned as the non - steady state."
    },
        {
        "error_type": "Incorrect Assignment of Actual Resistance",
        "description": "The parallel state should be assigned as 'Rp'; the anti - parallel state should be assigned as 'Rap'. However, 'Rp' is written as 'Rap' during assignment."
    },
    {
        "error_type": "Resistance Calculation Error for Parallel and Anti - Parallel States",
        "description": "The formulas for calculating the resistances of parallel and anti - parallel states are incorrect. The correct formulas should be 'Rp = Ro' and 'Rap = Rp * (1 + TMRR)'."
    },
    {
        "error_type": "Critical Current Calculation Error",
        "description": "The formula for the critical current is incorrect. The correct formula should be 'IcAP = gap * surface'."
    },
    {
        "error_type": "Sequence Error",
        "description": "When starting DC analysis, the judgment of the parallel state is incorrect. For example, the order of the two lines of code 'if(Vb >= (IcP * Rp))' and 'if(Vc >= (IcAP * Rap))' is wrong."
    },
    {
        "error_type": "Characteristic Time Formula Error",
        "description": "The formula for the characteristic time is wrong. 'tau = tau0 * exp(Em * (1 - abs(Id / IcP)) / (`Kb * temp * 40 * `M_PI))' is wrongly written as 'tau = tau0 / exp(Em * (1 - abs(Id / IcP)) / (`Kb * temp * 40 * `M_PI))'."
    },
    {
        "error_type": "Threshold Judgment Condition Error in Neel - Brown Model",
        "description": "The threshold judgment condition in the Neel - Brown model is incorrect. 'if(Vb > brown_threshold)' is wrongly written as 'if(Vb < brown_threshold)'."
    },
    {
        "error_type": "Critical Voltage Direction Judgment Error in Neel - Brown Model",
        "description": "The judgment of the critical voltage direction in the Neel - Brown model is incorrect. For example, 'if (Vb < 0.8 * IcP * Rp)' is wrongly written as 'if (Vb > 0.8 * IcP * Rp)'."
    },
    {
        "error_type": "State Output Error",
        "description": "The state output under 'transition' analysis is incorrect and is confused with DC analysis. For example, 'I(Ttrans) <+ transition(ix, 0, 1e - 12, 1e - 12)' is wrongly written as 'V(Ttrans) <+ ix'."
    },
    {
        "error_type": "Seeding Initial Value Not Assigned in Random Number",
        "description": "The initial value is not assigned to 'seeding'."
    },
    {
        "error_type": "Standard Deviation of Normal Distribution in Random Number Incorrectly Written or Omitted",
        "description": "The 'seeding' should follow a normal distribution, and its standard deviation is set to 1, which is easy to be written incorrectly or omitted."
    },
    {
        "error_type": "Seed Value Error in Random Number",
        "description": "Theoretically, the 'seed' value should be 1000000000 times the 'seeding' value. In practice, it is easy to have extra or missing zeros, resulting in an incorrect order of magnitude."
    },
    {
        "error_type": "Critical Voltage Value Error in Neel - Brown Model",
        "description": "The critical voltage value in the Neel - Brown model is incorrect. For example, 'if (Vb < 0.8 * IcP * Rp)' is wrongly written as 'Vb < 0.6 * IcP * Rp'."
    },
    {
        "error_type": "Structure Missing",
        "description": "The 'analog begin' is omitted, resulting in an incomplete structure when defining the model."
    }

    
]


def preprocess_code(code):
    """更宽松的预处理保留代码结构"""
    processed = []
    for line in code.split('\n'):
        # 保留行结构仅移除尾随空格和注释
        line = re.sub(r'//.*', '', line).rstrip()
        if line.strip():
            # 保留行内基本结构，合并多余空格
            processed.append(re.sub(r'\s+', ' ', line))
    return processed


def validate_error_code(original_code, error_code):
    """智能验证修改位置"""
    original = preprocess_code(original_code)
    error = preprocess_code(error_code)

    # 场景1：完全相同的预处理结果
    if original == error:
        return False

    # 场景2：使用改进的差异块检测
    matcher = difflib.SequenceMatcher(None, original, error)
    change_groups = []

    for op in matcher.get_opcodes():
        if op[0] != 'equal':
            # 记录修改范围（原始行号）
            change_groups.append((op[1], op[2]))

    # 允许以下情况：
    # 1. 所有修改集中在连续3行内（处理多行表达式）
    # 2. 最多两个修改块（应对行拆分/合并）
    if len(change_groups) == 0:
        return False
    elif len(change_groups) == 1:
        return True
    else:
        # 检查修改块是否相邻
        merged = [change_groups[0]]
        for start, end in change_groups[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end + 1:  # 允许间隔1行
                merged[-1] = (last_start, end)
            else:
                merged.append((start, end))
        return len(merged) == 1


def call_deepseek_api(system_prompt, user_prompt):
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
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 4096
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"响应解析失败: {str(e)}")
        return None


def read_large_file(file_path):
    # 读取文件内容
    encodings = ['utf-8', 'gbk', 'latin-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"文件读取失败 [{encoding}]: {str(e)}")
            return None
    print(f"无法解码文件: {file_path}")
    return None


def generate_error_versions(correct_code_path, description_path):
    try:
        correct_code = read_large_file(correct_code_path)
        description = read_large_file(description_path)
    except IOError as e:
        print(f"文件读取错误: {str(e)}")
        return []

    error_packages = []
    for idx, error in enumerate(USER_ERRORS, 1):
        retries = 0
        valid = False
        last_error_code = ""  # 记录最后一次生成的代码

        while retries < MAX_RETRIES and not valid:
            # 强化版提示词
            system_prompt = f"""As a VerilogA expert, perform precise error injection:

            Original Code (strictly preserve formatting):
            {correct_code}

            Error Type: {error['error_type']}
            Error Description: {error['description']}

            Modification Requirements:
            1. Modify only 1 operator (e.g., &&→||, < → >, etc.)
            2. Keep the following unchanged:
               - Line numbers, indentation, whitespace
               - Comment content and position
               - Code structure and line breaks
            3. Modified lines must have exactly the same character count as original

            Output Format:
            ```verilog
            [Modified code with identical formatting to original]
            ```"""

            user_prompt = "Return ONLY the modified complete code without any explanation!"

            response = call_deepseek_api(system_prompt, user_prompt)
            raw_error_code = extract_code_content(response)
            error_code = postprocess_code(raw_error_code, correct_code)
            last_error_code = error_code  # 记录最后一次生成的代码

            # 强制输出生成的代码
            print(f"\n{'=' * 30} 尝试 {retries + 1} {'=' * 30}")
            # print(f"生成的错误代码：\n{error_code}")

            # 执行严格验证
            valid = validate_error_injection(correct_code, error_code, error['description'])

            if not valid:
                print(f"验证未通过，正在重试 ({retries + 1}/{MAX_RETRIES})")
                retries += 1
                time.sleep(1)
            else:
                print("验证通过！")

        if valid:
            error_packages.append((idx, error_code, error['description']))
        else:
            print(f"\n{'#' * 40}")
            print(f"错误类型 {error['error_type']} 生成失败")
            print("最后生成的代码：")
            print(last_error_code)
            print('#' * 40)

    return error_packages


def debug_diff(original, modified):
    """增强版差异分析"""
    orig_lines = original.split('\n')
    mod_lines = modified.split('\n')

    diff = difflib.unified_diff(orig_lines, mod_lines, n=3)
    diff_text = '\n'.join(diff)

    print("\n差异分析：")
    if not diff_text:
        print("无文本差异（可能格式不同）")
    else:
        print(diff_text)

    # 字符级差异检查
    for line_num, (ol, ml) in enumerate(zip(orig_lines, mod_lines)):
        if ol != ml:
            print(f"\n行 {line_num + 1} 字符级差异：")
            for col, (oc, mc) in enumerate(zip(ol, ml)):
                if oc != mc:
                    print(f" 列 {col + 1}: {repr(oc)} → {repr(mc)}")


def validate_error_injection(original, modified, error_desc):
    """终极验证函数"""
    # 逻辑内容比对（忽略注释和空格）
    orig_logic = [re.sub(r'\s+', '', line.split('//')[0]) for line in original.split('\n') if
                  line.split('//')[0].strip()]
    mod_logic = [re.sub(r'\s+', '', line.split('//')[0]) for line in modified.split('\n') if
                 line.split('//')[0].strip()]

    # 寻找差异点
    diff_count = 0
    for o, m in zip(orig_logic, mod_logic):
        if o != m:
            # 允许最多2个连续字符差异（如&&→||）
            if len(o) != len(m):
                return False
            mismatch = sum(1 for a, b in zip(o, m) if a != b)
            if mismatch > 30:
                return False
            diff_count += 1
    return diff_count == 1


def extract_location_reasoning(response):
    """提取模型的位置决策依据"""
    reasoning_pattern = r"1\. 定位分析：(.+?)\n2\. 修改方式"
    match = re.search(reasoning_pattern, response, re.DOTALL)
    return match.group(1).strip() if match else "未提供定位分析"


def extract_code_content(response):
    # 匹配更灵活的代码块格式
    code_pattern = r"```(?:verilog|va)?\s*\n(.*?)\n```"
    matches = re.findall(code_pattern, response['choices'][0]['message']['content'], re.DOTALL)

    if matches:
        # 取最后一个代码块（通常是最新的修改）
        clean_code = matches[-1].strip()
    else:
        # 保底处理：去除所有代码块标记
        raw_content = response['choices'][0]['message']['content']
        clean_code = re.sub(r"```.*", "", raw_content).strip()

    # 移除残留的错误标记注释
    clean_code = re.sub(r"//\s*ERROR.*", "", clean_code)
    # 恢复VerilogA格式要求
    clean_code = re.sub(r"(?<=\S)\s+(?=\/\/)", "\n    ", clean_code)  # 保持注释对齐
    return clean_code


def save_error_files(packages):
    """保存错误代码和描述文件"""
    for idx, code, desc in packages:
        # 保存错误代码
        code_filename = f"Error_{idx:03d}.va"
        code_path = os.path.join(INPUT_FOLDER, code_filename)
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code)

        # 保存错误描述
        desc_filename = f"Error_{idx:03d}_desc.txt"
        desc_path = os.path.join(INPUT_FOLDER, desc_filename)
        with open(desc_path, 'w', encoding='utf-8') as f:
            f.write(desc)

        print(f"已生成错误文件组：{code_filename} 和 {desc_filename}")


def analyze_error_code(error_code_path, description_path):
    # 错误代码分析
    try:
        error_code = read_large_file(error_code_path)
        description = read_large_file(description_path)
    except Exception as e:
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
    {description}

    [Code to be reviewed]
    {error_code}

    Please respond in the following format:
    1.Code Issue Analysis
    2.Modification Recommendations
    3.Complete Corrected Code"""

    response = call_deepseek_api(system_prompt, user_prompt)
    if response and 'choices' in response:
        return response['choices'][0]['message']['content']
    return None


def process_all_versions():
    # 生成错误版本
    error_packages = generate_error_versions(CORRECT_CODE_PATH, DESCRIPTION_PATH)
    save_error_files(error_packages)

    # 对每个错误版本进行分析
    for idx, _, _ in error_packages:
        error_code_path = os.path.join(INPUT_FOLDER, f"Error_{idx:03d}.va")

        # 调用分析函数
        analysis_result = analyze_error_code(error_code_path, DESCRIPTION_PATH)

        # 保存分析结果
        if analysis_result:
            result_path = os.path.join(INPUT_FOLDER, f"Error_{idx:03d}_fix.txt")
            with open(result_path, 'w', encoding='utf-8') as f:
                f.write(analysis_result)
            print(f"已保存修正结果: Error_{idx:03d}_fix.txt")


def postprocess_code(generated, original):
    """超严格对齐处理"""
    orig_lines = original.split('\n')
    gen_lines = generated.split('\n')

    processed = []
    for i in range(len(orig_lines)):
        if i < len(gen_lines):
            # 保留原始行的格式特征
            orig_indent = re.match(r'^\s*', orig_lines[i]).group()
            orig_comment = re.search(r'//.*', orig_lines[i]).group() if '//' in orig_lines[i] else ''

            # 提取生成代码的逻辑内容
            gen_line = gen_lines[i].split('//')[0].rstrip()
            new_line = f"{orig_indent}{gen_line}"
            if orig_comment:
                new_line += f" {orig_comment}"

            processed.append(new_line)
        else:
            processed.append(orig_lines[i])
    return '\n'.join(processed)


if __name__ == "__main__":
    process_all_versions()