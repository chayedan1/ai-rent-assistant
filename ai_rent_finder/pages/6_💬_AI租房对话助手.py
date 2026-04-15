# ============================================================
# Ollama + 简单关键词检索 RAG 系统
# AI 租房法律助手
# ============================================================
import streamlit as st
import os
import json
import time
import requests
from PyPDF2 import PdfReader

st.set_page_config(page_title="AI 租房法律助手", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
.page-title { font-size:28px; font-weight:700; color:#f8fafc; text-align:center; margin-bottom:4px; }
.page-subtitle { font-size:13px; color:#94a3b8; text-align:center; margin-bottom:20px; }
.msg-user { background:rgba(59,130,246,0.12); border-radius:12px; padding:14px 18px; margin:10px 0; border-left:3px solid #3b82f6; }
.msg-assistant { background:rgba(30,41,59,0.95); border-radius:12px; padding:14px 18px; margin:10px 0; border-left:3px solid #10b981; }
.msg-role { font-size:12px; font-weight:600; margin-bottom:6px; }
.msg-role.user { color:#60a5fa; }
.msg-role.assistant { color:#34d399; }
.msg-body { color:#e2e8f0; font-size:14.5px; line-height:1.8; white-space:pre-wrap; }
.source-panel { background:rgba(30,41,59,0.8); border-radius:12px; padding:12px; margin-top:15px; border-left:3px solid #f59e0b; }
.source-title { font-size:13px; font-weight:600; color:#fbbf24; margin-bottom:6px; }
.source-content { font-size:13px; color:#94a3b8; line-height:1.6; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 配置
# ============================================================
MODEL_NAME = "deepseek-r1:8b"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
SOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'source')
PDF_FILE = os.path.join(SOURCE_DIR, '租房rag.pdf')

# ============================================================
# 系统提示词（强制格式）
# ============================================================
SYSTEM_PROMPT = """你是专业级租房法律智能助手，基于《民法典》与本地租房法律知识库提供解答。

### 铁律约束
1. 只回答租房法律问题，非租房问题回复："此问题不属于租房法律范畴，我无法解答。"
2. 100% 基于下方【参考资料】回答，禁止编造
3. 参考资料无答案时："当前知识库未找到相关答案，请补充具体场景或咨询律师。"

### 回答格式（强制）
【问题类型】XXX（合同签订/押金退还/退租解约/维修责任/违约赔偿/纠纷维权/身份核实/交房验收/看房选房/综合避坑）
【法律结论】一句话精准结论
【法律依据】《民法典》第 XXX 条 + 具体条文内容
【实操步骤】
1. XXX
2. XXX
3. XXX
【维权路径】协商 → 街道调解 → 12345 投诉 → 法院起诉
【证据留存】聊天记录、合同、转账凭证、照片、录音等
【避坑提醒】1 条关键风险提示
【知识来源】PDF 文件名 + 页码

### 重要：请严格按照上述格式回答，不要输出 JSON 或其他格式！"""

# ============================================================
# PDF 知识库加载
# ============================================================
@st.cache_resource
def load_pdf_knowledge():
    if not os.path.exists(PDF_FILE):
        return None, None
    
    try:
        reader = PdfReader(PDF_FILE)
        texts = []
        page_sources = []
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                texts.append(text)
                page_sources.append(f"PDF: 租房rag.pdf | 页码: {i + 1}")
        
        if not texts:
            return None, None
        
        return texts, page_sources
        
    except Exception as e:
        st.error(f"❌ PDF 加载失败: {e}")
        return None, None

# ============================================================
# 简单关键词检索
# ============================================================
def simple_search(query, texts, page_sources, top_k=3):
    if not texts:
        return []
    
    keywords = [w for w in query if len(w) >= 2]
    
    results = []
    for i, text in enumerate(texts):
        text_lower = text.lower()
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            results.append((score, text, page_sources[i]))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]

# ============================================================
# Ollama 调用
# ============================================================
def call_ollama(user_question, context=None):
    try:
        if context:
            prompt = f"""参考资料：
{context}

用户问题：{user_question}

请严格按照以下格式回答：
【问题类型】XXX（合同签订/押金退还/退租解约/维修责任/违约赔偿/纠纷维权/身份核实/交房验收/看房选房/综合避坑）
【法律结论】一句话精准结论
【法律依据】《民法典》第 XXX 条 + 具体条文内容
【实操步骤】
1. XXX
2. XXX
3. XXX
【维权路径】协商 → 街道调解 → 12345 投诉 → 法院起诉
【证据留存】聊天记录、合同、转账凭证、照片、录音等
【避坑提醒】1 条关键风险提示
【知识来源】PDF 文件名 + 页码"""
        else:
            prompt = f"""用户问题：{user_question}

请根据《民法典》租房相关条款回答。

请严格按照以下格式回答：
【问题类型】XXX（合同签订/押金退还/退租解约/维修责任/违约赔偿/纠纷维权/身份核实/交房验收/看房选房/综合避坑）
【法律结论】一句话精准结论
【法律依据】《民法典》第 XXX 条 + 具体条文内容
【实操步骤】
1. XXX
2. XXX
3. XXX
【维权路径】协商 → 街道调解 → 12345 投诉 → 法院起诉
【证据留存】聊天记录、合同、转账凭证、照片、录音等
【避坑提醒】1 条关键风险提示
【知识来源】知识库未找到相关内容"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            timeout=120
        )
        result = response.json()
        return result.get('message', {}).get('content', '')
    except requests.exceptions.Timeout:
        return "调用超时，请检查 Ollama 服务是否正常运行"
    except requests.exceptions.ConnectionError:
        return "连接失败，请检查 Ollama 服务是否已启动 (http://localhost:11434)"
    except Exception as e:
        return f"调用失败: {e}"

# ============================================================
# 检查 Ollama 服务
# ============================================================
def check_ollama_service():
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]
            if MODEL_NAME in model_names:
                return True, f"✅ Ollama 服务正常，已加载模型: {MODEL_NAME}"
            else:
                return False, f"⚠️ Ollama 服务正常，但未找到模型 {MODEL_NAME}，请先下载"
        return False, "⚠️ Ollama 服务响应异常"
    except:
        return False, "❌ Ollama 服务未连接，请确保服务已启动 (http://localhost:11434)"

# ============================================================
# 主流程
# ============================================================
def main():
    st.markdown('<div class="page-title">⚖️ AI 租房法律助手</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">基于 Ollama deepseek-r1:8b · 本地知识库 · PDF 关键词检索</div>', unsafe_allow_html=True)
    
    ollama_status, ollama_msg = check_ollama_service()
    if not ollama_status:
        st.warning(ollama_msg)
    
    texts, page_sources = load_pdf_knowledge()
    
    if texts is None:
        st.error("❌ 知识库加载失败，请检查 source/租房rag.pdf")
        return
    
    if "msgs" not in st.session_state:
        st.session_state.msgs = []
    
    # 显示历史消息
    for msg in st.session_state.msgs:
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user"><div class="msg-role user">👤 您</div><div class="msg-body">{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="msg-assistant"><div class="msg-role assistant">⚖️ 助手</div><div class="msg-body">{msg["content"]}</div></div>', unsafe_allow_html=True)
    
    # 用户输入
    user_input = st.chat_input("输入你的租房法律问题...")
    
    if user_input:
        st.session_state.msgs.append({"role": "user", "content": user_input})
        
        # 检索相关文档
        with st.status("🔍 正在检索知识库...", expanded=True) as status:
            docs = simple_search(user_input, texts, page_sources, top_k=3)
            status.update(label="✅ 知识库检索完成", state="complete")
        
        # 构建上下文
        if docs:
            context = "\n\n".join([f"[来源 {i+1}] {doc[1][:500]}" for i, doc in enumerate(docs)])
            answer = call_ollama(user_input, context=context)
        else:
            answer = call_ollama(user_input, context=None)
        
        # 检查回答是否有效
        if not answer or "调用失败" in answer or "超时" in answer or "连接失败" in answer:
            with st.status("❌ 分析失败", state="error"):
                st.error(answer)
            st.session_state.msgs.append({"role": "assistant", "content": answer})
        else:
            with st.status("✅ 分析完成", state="complete"):
                pass
            st.session_state.msgs.append({"role": "assistant", "content": answer})
        
        # 显示知识来源
        if docs:
            st.markdown('<div class="source-panel"><div class="source-title">📚 知识来源</div>', unsafe_allow_html=True)
            for i, doc in enumerate(docs, 1):
                st.markdown(f'<div class="source-content"><strong>{i}.</strong> {doc[2]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="source-content">{doc[1][:300]}...</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.rerun()

if __name__ == "__main__":
    main()
