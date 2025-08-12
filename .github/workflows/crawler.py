import os
import sys
import requests
from bs4 import BeautifulSoup
import tempfile
import shutil

# 配置爬取目标（URL: 输出文件路径）
TARGETS = {
    "https://unpkg.com/feather-icons": "files/feather.min.js", 
    "https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css": "files/katex.min.css", 
    "https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js": "files/katex.min.js", 
    "https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js": "files/auto-render.min.js", 
    "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/github-dark-dimmed.min.css": "files/github-dark-dimmed.min.css", 
    "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js": "files/highlight.min.js", 
    "https://cdn.jsdelivr.net/npm/marked/marked.min.js": "files/marked.min.js", 
    "https://cdn.jsdelivr.net/npm/marked-footnote/dist/index.umd.js": "files/index.umd.js"
    # 添加更多目标...
}

def crawl_content():
    """爬取所有目标内容并安全更新文件"""
    # 创建临时目录存放新内容
    temp_dir = tempfile.mkdtemp()
    success = True
    
    try:
        # 爬取每个目标
        for url, output_path in TARGETS.items():
            try:
                print(f"🕷️ 正在爬取: {url}")
                
                # 发送请求
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()  # 检查HTTP错误
                
                # 解析内容（根据实际需要修改）
                soup = BeautifulSoup(response.text, 'html.parser')
                content = str(soup.find('body'))  # 示例：获取body内容
                
                # 写入临时文件
                temp_file = os.path.join(temp_dir, os.path.basename(output_path))
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"✅ 成功爬取: {url}")
                
            except Exception as e:
                print(f"❌ 爬取失败 [{url}]: {str(e)}")
                success = False
        
        # 所有爬取成功时才更新文件
        if success:
            print("🔄 正在更新文件...")
            for url, output_path in TARGETS.items():
                temp_file = os.path.join(temp_dir, os.path.basename(output_path))
                if os.path.exists(temp_file):
                    # 确保目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    # 原子操作：移动文件
                    shutil.move(temp_file, output_path)
            print("🎉 所有文件更新完成!")
            return True
        else:
            print("⚠️ 部分爬取失败，保留原文件")
            return False
            
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    if crawl_content():
        sys.exit(0)  # 成功退出
    else:
        sys.exit(1)  # 失败退出
