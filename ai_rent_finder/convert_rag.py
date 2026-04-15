import docx2txt
import json
import re

# 读取docx文件
text = docx2txt.process('d:/Work_Study/Trae_projects/AI租房/ai_rent_finder/source/租房rag.docx')

# 解析文档结构，提取各个章节
documents = []

# 按主要章节分割
main_sections = text.split('二、租赁合同核心条款详解')
part1 = main_sections[0] if len(main_sections) > 0 else ""
part2 = main_sections[1] if len(main_sections) > 1 else ""

# 处理第一部分：租房全流程避坑指南
if part1:
    part1 = part1.replace('一、租房全流程避坑指南', '').strip()
    sections = re.split(r'\n(?=\d+\.\s+)', part1)
    
    doc_id = 1
    for section in sections:
        section = section.strip()
        if not section or len(section) < 50:
            continue
        
        lines = section.split('\n')
        title = lines[0].strip() if lines else f'文档{doc_id}'
        content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else section
        
        key_points = []
        
        core_req_match = re.search(r'核心要求[:：](.*?)(?=\n\n|\n[^\n]*[:：]|法律依据|避坑提醒|$)', content, re.DOTALL)
        if core_req_match:
            key_points.append('核心要求：' + core_req_match.group(1).strip().replace('\n', ' '))
        
        warning_match = re.search(r'避坑提醒[:：](.*?)(?=\n\n|\n[^\n]*[:：]|$)', content, re.DOTALL)
        if warning_match:
            key_points.append('避坑提醒：' + warning_match.group(1).strip().replace('\n', ' '))
        
        law_match = re.search(r'法律依据[:：](.*?)(?=\n\n|\n[^\n]*[:：]|$)', content, re.DOTALL)
        if law_match:
            key_points.append('法律依据：' + law_match.group(1).strip().replace('\n', ' '))
        
        if not key_points and content:
            key_points.append(content[:300] + '...' if len(content) > 300 else content)
        
        category = '租房流程'
        if '合同' in title or '签约' in title:
            category = '合同签订'
        elif '押金' in title or '退租' in title:
            category = '押金退还'
        elif '维修' in title:
            category = '房屋维修'
        elif '费用' in title or '租金' in title:
            category = '费用相关'
        elif '看房' in title or '选房' in title:
            category = '看房选房'
        elif '交房' in title:
            category = '交房验收'
        elif '纠纷' in title or '争议' in title:
            category = '纠纷处理'
        elif '租赁期间' in title:
            category = '租赁期间'
        
        doc = {
            'id': f'doc_{doc_id:03d}',
            'category': category,
            'title': title,
            'content': content[:1500] + '...' if len(content) > 1500 else content,
            'key_points': key_points[:5],
            'source': '租房法律实务指南'
        }
        documents.append(doc)
        doc_id += 1

# 处理第二部分：租赁合同核心条款详解
if part2:
    sections = re.split(r'\n(?=\d+\.\s+)', part2)
    
    doc_id = len(documents) + 1
    for section in sections:
        section = section.strip()
        if not section or len(section) < 50:
            continue
        
        lines = section.split('\n')
        title = lines[0].strip() if lines else f'文档{doc_id}'
        content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else section
        
        key_points = []
        
        core_req_match = re.search(r'核心要求[:：](.*?)(?=\n\n|\n[^\n]*[:：]|法律依据|避坑提醒|$)', content, re.DOTALL)
        if core_req_match:
            key_points.append('核心要求：' + core_req_match.group(1).strip().replace('\n', ' '))
        
        warning_match = re.search(r'避坑提醒[:：](.*?)(?=\n\n|\n[^\n]*[:：]|$)', content, re.DOTALL)
        if warning_match:
            key_points.append('避坑提醒：' + warning_match.group(1).strip().replace('\n', ' '))
        
        law_match = re.search(r'法律依据[:：](.*?)(?=\n\n|\n[^\n]*[:：]|$)', content, re.DOTALL)
        if law_match:
            key_points.append('法律依据：' + law_match.group(1).strip().replace('\n', ' '))
        
        if not key_points and content:
            key_points.append(content[:300] + '...' if len(content) > 300 else content)
        
        doc = {
            'id': f'doc_{doc_id:03d}',
            'category': '合同条款',
            'title': title,
            'content': content[:1500] + '...' if len(content) > 1500 else content,
            'key_points': key_points[:5],
            'source': '租房法律实务指南'
        }
        documents.append(doc)
        doc_id += 1

# 创建知识库
knowledge_base = {
    'knowledge_base': {
        'description': '租房法律实务知识库 - 基于专业租房法律指南',
        'last_updated': '2024-01-15',
        'categories': list(set([d['category'] for d in documents])),
        'documents': documents
    }
}

# 保存为JSON
output_path = 'd:/Work_Study/Trae_projects/AI租房/ai_rent_finder/source/租房rag.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

print(f'成功创建知识库！')
print(f'文档数量：{len(documents)}')
print(f'类别：{knowledge_base["knowledge_base"]["categories"]}')
print('\n前10个文档：')
for doc in documents[:10]:
    print(f'  - {doc["title"]} ({doc["category"]})')
