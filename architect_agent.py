import json

class ArchitectAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def analyze_code(self, code_snippet):
        prompt = f"""你是一个资深架构师，请分析以下Python代码片段，识别其中的“坏味道”（code smells），并提出具体的重构建议。请以JSON格式返回结果，包含'smells'（坏味道列表）和'refactoring_plan'（重构计划）。

代码片段：
```python
{code_snippet}
```

示例输出：
{{
    "smells": [
        {{"type": "Long Method", "description": "函数过长，职责不单一"}},
        {{"type": "Duplicate Code", "description": "存在重复代码块"}}
    ],
    "refactoring_plan": [
        {{"step": 1, "description": "将长函数拆分为多个小函数"}},
        {{"step": 2, "description": "提取重复代码为公共函数"}}
    ]
}}"""
        response = self.llm_client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        try:
            # 尝试直接解析LLM的响应内容
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试清理字符串（例如，移除Markdown代码块的标记）再解析
            cleaned_content = response.choices[0].message.content.strip()
            if cleaned_content.startswith("```json") and cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[len("```json"):-len("```")].strip()
            try:
                return json.loads(cleaned_content)
            except json.JSONDecodeError:
                print("ArchitectAgent: LLM返回的不是有效的JSON格式，尝试直接返回文本。")
                return {"error": "Invalid JSON from LLM", "raw_response": response.choices[0].message.content}

