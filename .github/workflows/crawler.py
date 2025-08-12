import os
import sys
import requests
import tempfile
import shutil
import mimetypes
from pathlib import Path

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

def download_file(url, output_path):
    """下载文件并保存到指定路径"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    # 获取文件内容
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    
    # 确定文件类型
    content_type = response.headers.get('Content-Type', '')
    file_extension = ''
    
    # 根据内容类型设置扩展名
    if 'javascript' in content_type or url.endswith('.js'):
        file_extension = '.js'
    elif 'css' in content_type or url.endswith('.css'):
        file_extension = '.css'
    elif 'font' in content_type or any(url.endswith(ext) for ext in ['.otf', '.ttf', '.woff', '.woff2']):
        # 从URL中提取字体扩展名
        file_extension = Path(url).suffix
    
    # 确保输出路径有正确的扩展名
    if file_extension and not output_path.endswith(file_extension):
        output_path += file_extension
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存文件
    if 'text' in content_type:
        # 文本文件（CSS/JS）
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
    else:
        # 二进制文件（字体等）
        with open(output_path, 'wb') as f:
            f.write(response.content)
    
    return output_path

def crawl_content():
    """爬取所有目标内容并安全更新文件"""
    # 创建临时目录存放新内容
    temp_dir = tempfile.mkdtemp()
    success = True
    downloaded_files = {}
    
    try:
        # 爬取每个目标
        for url, output_path in TARGETS.items():
            try:
                print(f"🕷️ 正在爬取: {url}")
                
                # 在临时目录创建文件
                temp_path = os.path.join(temp_dir, os.path.basename(output_path))
                final_path = download_file(url, temp_path)
                
                # 保存实际路径（可能添加了扩展名）
                downloaded_files[url] = (temp_path, final_path)
                print(f"✅ 成功爬取: {url} -> {final_path}")
                
            except Exception as e:
                print(f"❌ 爬取失败 [{url}]: {str(e)}")
                success = False
        
        # 所有爬取成功时才更新文件
        if success:
            print("🔄 正在更新文件...")
            for url, (temp_path, final_path) in downloaded_files.items():
                # 确保目标目录存在
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
                # 移动文件
                shutil.move(temp_path, final_path)
            print("🎉 所有文件更新完成!")
            return True
        else:
            print("⚠️ 部分爬取失败，保留原文件")
            return False
            
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_ok=True)

if __name__ == "__main__":
    if crawl_content():
        sys.exit(0)  # 成功退出
    else:
        sys.exit(1)  # 失败退出
