import os
from openai import OpenAI
from architect_agent import ArchitectAgent
from refactor_agent import RefactorAgent
from review_agent import ReviewAgent

# 确保 OPENAI_API_KEY 环境变量已设置
# 如果没有，请替换为您的实际 API 密钥
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

# 初始化 OpenAI 客户端
# 注意：这里使用了兼容 OpenAI API 的 Gemini 模型，因此 base_url 保持默认
client = OpenAI()

def run_code_evolution(code_snippet):
    print("\n--- CodeEvolution 启动 ---")

    # 1. Architect Agent: 分析代码并生成重构计划
    print("\n[Architect Agent] 正在分析代码中的坏味道并制定重构计划...")
    architect_agent = ArchitectAgent(client)
    analysis_result = architect_agent.analyze_code(code_snippet)
    if "error" in analysis_result:
        print(f"[Architect Agent] 错误: {analysis_result['error']}")
        print(f"[Architect Agent] 原始LLM响应: {analysis_result['raw_response']}")
        return
    
    print("\n[Architect Agent] 分析结果：")
    print(f"  坏味道: {[s['type'] for s in analysis_result['smells']]}")
    print(f"  重构计划: {[p['description'] for p in analysis_result['refactoring_plan']]}")

    # 2. Refactor Agent: 根据计划重构代码
    print("\n[Refactor Agent] 正在根据重构计划重构代码...")
    refactor_agent = RefactorAgent(client)
    refactored_code = refactor_agent.apply_refactoring(code_snippet, analysis_result['refactoring_plan'])
    print("\n[Refactor Agent] 重构后的代码：")
    print(refactored_code)

    # 3. Review Agent: 审查重构后的代码
    print("\n[Review Agent] 正在审查重构后的代码...")
    review_agent = ReviewAgent(client)
    review_result = review_agent.review_code(code_snippet, refactored_code, analysis_result['refactoring_plan'])
    if "error" in review_result:
        print(f"[Review Agent] 错误: {review_result['error']}")
        print(f"[Review Agent] 原始LLM响应: {review_result['raw_response']}")
        return

    print("\n[Review Agent] 审查结果：")
    print(f"  总评分: {review_result['overall_score']}/10")
    print(f"  反馈: {review_result['feedback']}")
    print(f"  发现的问题: {[i['description'] for i in review_result['issues_found']]}")

    print("\n--- CodeEvolution 运行结束 ---")

if __name__ == "__main__":
    # 示例代码片段，包含一些“坏味道”
    example_code = """
def calculate_total_price(price, quantity, discount_rate):
    # 计算总价，包含折扣
    if quantity > 10:
        total = price * quantity * (1 - discount_rate)
    else:
        total = price * quantity

    # 打印结果
    print(f"Total price: {total}")
    return total

def apply_discount(price, discount_rate):
    return price * (1 - discount_rate)

def calculate_order_total(item_price, item_quantity, customer_discount):
    # 这是一个重复的逻辑，应该被重构
    if item_quantity > 10:
        order_total = item_price * item_quantity * (1 - customer_discount)
    else:
        order_total = item_price * item_quantity
    return order_total

result = calculate_total_price(100, 12, 0.1)
print(f"Final result: {result}")
"""
    run_code_evolution(example_code)
