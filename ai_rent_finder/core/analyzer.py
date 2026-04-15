
import json
import os
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

# 提示：请在您的环境中设置名为 'DASHSCOPE_API_KEY' 的环境变量，并填入您的通义千问API密钥。
# os.environ["DASHSCOPE_API_KEY"] = "您的API密钥"

# 1. 读取并解析JSON数据
def load_house_data(file_path="data/beike_sz.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"成功从 {file_path} 加载了 {len(data)} 条房源数据。")
        return data
    except FileNotFoundError:
        print(f"错误：找不到数据文件 {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 不是有效的JSON格式。")
        return []

def get_summary_suggestion(dataframe):
    """对筛选出的房源列表进行AI总结并给出初步建议"""
    if dataframe.empty:
        return "没有找到符合条件的房源，无法给出建议。"

    # 对数据进行汇总
    num_houses = len(dataframe)
    min_price = dataframe['price_num'].min()
    max_price = dataframe['price_num'].max()
    avg_price = dataframe['price_num'].mean()
    
    # 将部分数据转换为字符串，以便传递给LLM
    sample_data_str = dataframe.head(3).to_string()

    # 构建Prompt模板
    template = """
    请扮演一位专业的深圳房产分析师。
    我刚刚根据用户的筛选条件，找到了 {num_houses} 套房源。
    
    数据概览如下：
    - 价格范围: {min_price} - {max_price} 元/月
    - 平均价格: {avg_price:.0f} 元/月
    
    这里是前几套房源的样本数据：
    {sample_data}

    请根据以上概览和样本，为用户提供一份初步的租房建议。请从以下几个角度分析：
    1.  **市场概况**: 根据房源数量和价格范围，评价用户的预算在当前市场上的选择空间。
    2.  **机会与建议**: 指出是否存在明显的高性价比机会，或者建议用户可以如何调整筛选条件以获得更好的结果（例如，稍微提高预算、考虑邻近区域等）。
    3.  **总结**: 给出一个简短、清晰的最终建议。

    请以友好、鼓励的语气进行分析。
    """
    prompt = PromptTemplate(template=template, input_variables=["num_houses", "min_price", "max_price", "avg_price", "sample_data"])

    # 实例化LLM
    llm = Ollama(model="qwen3.5:9b")
    
    # 格式化Prompt并调用
    formatted_prompt = prompt.format(
        num_houses=num_houses,
        min_price=min_price,
        max_price=max_price,
        avg_price=avg_price,
        sample_data=sample_data_str
    )
    analysis_result = llm.invoke(formatted_prompt)
    
    return analysis_result
    # 构建Prompt模板
    template = """
    请扮演一位专业的深圳房产分析师。
    根据以下房源数据，请从地理位置、价格、户型和面积等角度，给出一个详细的性价比分析报告，并给出最终的租房建议。
    请以清晰、易于理解的格式呈现，包含优点和缺点。

    房源数据：
    标题: {title}
    价格: {price}
    描述: {description}
    链接: {link}
    
    分析报告：
    """
    prompt = PromptTemplate(template=template, input_variables=["title", "price", "description", "link"])

    # 实例化LLM
    llm = Tongyi(model_name="qwen-plus", temperature=0.7)
    
    # 格式化Prompt并调用
    formatted_prompt = prompt.format(**house_data)
    analysis_result = llm.invoke(formatted_prompt)
    
    return analysis_result

# 主程序入口（用于独立测试）
if __name__ == "__main__":
    # 检查API密钥是否设置
    if "DASHSCOPE_API_KEY" not in os.environ:
        print("错误：请先设置环境变量 DASHSCOPE_API_KEY。")
        exit()

    # 加载数据
    all_houses = load_house_data()

    if not all_houses:
        print("没有可供分析的房源数据，程序退出。")
    else:
        # 挑选第一套房源作为分析样本
        sample_house = all_houses[0]
        print("\n将对以下房源进行性价比分析：")
        print(json.dumps(sample_house, ensure_ascii=False, indent=4))
        
        print("\n正在调用大模型进行分析，请稍候...")
        
        # 调用分析函数
        analysis_result = analyze_house(sample_house)
        
        # 打印结果
        print("\n---------- AI分析报告 ----------")
        print(analysis_result)
        print("--------------------------------")

