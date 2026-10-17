# -*- coding: utf-8 -*-
import os
from openai import OpenAI
import gradio as gr

# 智谱 API Key：从环境变量 ZHIPU_API_KEY 读取
# 设置方法（PowerShell）：$env:ZHIPU_API_KEY="你的Key"
API_KEY = os.environ.get('ZHIPU_API_KEY', '')

client = OpenAI(
    api_key=API_KEY or '未配置',
    base_url='https://open.bigmodel.cn/api/paas/v4/'
)

def load_knowledge():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'knowledge', 'network_faults.md')
    with open(path, encoding='utf-8') as f:
        return f.read()

SYSTEM_PROMPT = '''你是一名华为数通网络运维专家。
必须严格依据下面的"参考知识库"回答；知识库没有覆盖时，明确回复"知识库暂未覆盖，建议补充信息"。
回答固定使用以下结构：
① 可能原因
② 排查步骤（编号列出）
③ 相关诊断与配置命令（华为 VRP 语法）
语言简洁专业。
参考知识库：
{knowledge}'''

def chat(message, history):
    if not API_KEY:
        return ('还没有配置智谱 API Key，网页能打开但无法对话。\n\n'
                '请先关闭本程序（在窗口按 Ctrl+C），然后在 PowerShell 执行：\n'
                '$env:ZHIPU_API_KEY="你的Key"\n'
                '再重新运行 python app.py')
    messages = [{'role': 'system',
                 'content': SYSTEM_PROMPT.format(knowledge=load_knowledge())}]
    # history 是 Gradio 传入的多轮对话记录（OpenAI messages 格式）
    for h in history:
        messages.append({'role': h['role'], 'content': h['content']})
    messages.append({'role': 'user', 'content': message})
    try:
        resp = client.chat.completions.create(
            model='glm-4-flash',     # 免费模型，名字以官网模型列表为准
            messages=messages,
            temperature=0.3
        )
        return resp.choices[0].message.content
    except Exception as e:
        return '调用大模型失败：' + str(e) + '\n\n请检查 API Key 是否正确、网络是否正常。'

demo = gr.ChatInterface(
    fn=chat,
    title='智能网络故障排查助手',
    description='输入故障现象（如：VRRP 双主、OSPF 邻居无法建立、VLAN 不通），获取排查步骤与华为配置命令'
)

if __name__ == '__main__':
    if not API_KEY:
        print('=' * 50)
        print('提示：未检测到 ZHIPU_API_KEY 环境变量。')
        print('网页可以打开，但还不能对话。请先在 PowerShell 执行：')
        print('  $env:ZHIPU_API_KEY="你的Key"')
        print('然后重新运行 python app.py')
        print('=' * 50)
    demo.launch()
