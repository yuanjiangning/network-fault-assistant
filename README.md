# 智能网络故障排查助手

基于智谱 GLM 大模型 API + Gradio 开发的网络运维问答助手。内置华为数通故障知识库，通过 System Prompt 约束模型严格基于知识库输出「可能原因 + 排查步骤 + VRP 配置命令」，支持多轮对话；对知识库未覆盖的问题明确拒答，避免模型幻觉。Gradio 自动生成网页聊天界面，零前端代码。

## 技术栈

Python 3、智谱 GLM-4-Flash API、Gradio、Prompt Engineering

## 功能

- 调用大模型 API 实现网络故障问答，支持多轮上下文对话
- 将私有故障知识库注入 System Prompt，限定回答范围与三段式输出结构
- 知识库未覆盖的问题（如闲聊、无关问题）明确拒答，回答可溯源
- 用 Gradio 自动生成 Web 对话界面，无需编写 HTML/CSS/JS

## 项目结构

```
network-fault-assistant/
├── app.py                    # 主程序（API 调用 + Gradio 界面）
├── knowledge/
│   └── network_faults.md     # 网络故障排查知识库
└── requirements.txt
```

## 快速开始

```bash
git clone <仓库地址>
cd network-fault-assistant
python -m venv .venv
# Windows 激活虚拟环境
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# 设置智谱 API Key（PowerShell；Linux/Mac 用 export）
$env:ZHIPU_API_KEY="你的APIKey"
python app.py
# 浏览器访问 http://127.0.0.1:7860
```

## 说明

- 需在[智谱开放平台](https://open.bigmodel.cn)申请 API Key，通过环境变量 `ZHIPU_API_KEY` 传入，未硬编码在代码中。
- 可在 `knowledge/network_faults.md` 中按既有格式持续扩充故障条目（OSPF、VRRP、VLAN、链路聚合、STP、NAT、DHCP、SSH 等）。
