import json

class RefactorAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def apply_refactoring(self, original_code, refactoring_plan):
        plan_str = json.dumps(refactoring_plan, ensure_ascii=False, indent=2)
        prompt = f"""你是一个代码重构专家，请根据以下原始Python代码和重构计划，对代码进行重构。请直接返回重构后的完整Python代码，不要包含任何解释性文字。

原始代码：
```python
{original_code}
```

重构计划：
```json
{plan_str}
```

请直接返回重构后的完整Python代码：
"""
        response = self.llm_client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
