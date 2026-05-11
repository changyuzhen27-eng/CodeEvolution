import json

class ReviewAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def review_code(self, original_code, refactored_code, refactoring_plan):
        plan_str = json.dumps(refactoring_plan, ensure_ascii=False, indent=2)
        prompt = f"""你是一个代码审查专家，请对比原始代码和重构后的代码，并结合重构计划，评估重构的质量。请从以下几个方面进行评估：
1. 重构是否成功解决了“坏味道”？
2. 是否引入了新的问题或Bug？
3. 代码可读性、可维护性是否有提升？
4. 是否严格遵循了重构计划？

请以JSON格式返回评估结果，包含'overall_score'（1-10分），'feedback'（详细反馈），'issues_found'（发现的问题列表）。

原始代码：
```python
{original_code}
```

重构后的代码：
```python
{refactored_code}
```

重构计划：
```json
{plan_str}
```

示例输出：
{{
    "overall_score": 8,
    "feedback": "重构基本成功，解决了大部分坏味道，但仍有小部分可优化空间。",
    "issues_found": [
        {{"type": "Minor Issue", "description": "函数命名可以更清晰"}}
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
                print("ReviewAgent: LLM返回的不是有效的JSON格式，尝试直接返回文本。")
                return {"error": "Invalid JSON from LLM", "raw_response": response.choices[0].message.content}
