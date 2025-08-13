import os
import sys
import requests
import tempfile
import shutil
from pathlib import Path

# 配置爬取目标（URL: 输出文件路径）
TARGETS = {
    "https://unpkg.com/feather-icons": "files/feather.min.js", 
    "https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css": "files/katex.min.css", 
    "https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js": "files/katex.min.js", 
    "https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js": "files/auto-render.min.js", 
    "https://cdn.jsdelivr.net/npm/highlight.js/styles/github-dark-dimmed.min.css": "files/github-dark-dimmed.min.css", 
    "https://cdn.jsdelivr.net/npm/highlight.js/lib/index.min.js": "files/highlight.min.js", 
    "https://cdn.jsdelivr.net/npm/marked/marked.min.js": "files/marked.min.js", 
    "https://cdn.jsdelivr.net/npm/marked-footnote/dist/index.umd.js": "files/index.umd.js"
}

# 配置爬取目录（源目录URL: 目标目录路径）
TARGETS_DIR = {
    "https://cdn.jsdelivr.net/npm/katex@latest/dist/fonts/": "files/fonts/"
}

def get_file_list(source_url):
    """获取指定目录下的文件列表（使用新版 API）"""
    try:
        # 从 URL 中提取包名和路径
        if "npm/" in source_url:
            package_path = source_url.split("npm/")[1].rstrip('/')
            if "@" in package_path:
                package_name, version_path = package_path.split("@", 1)
                version, path = version_path.split("/", 1) if "/" in version_path else (version_path, "")
            else:
                package_name = package_path.split("/")[0]
                version = "latest"
                path = package_path[len(package_name)+1:]
        else:
            # 处理其他类型的 URL（如 unpkg）
            package_name = source_url.split("//")[1].split("/")[0]
            path = "/".join(source_url.split("//")[1].split("/")[1:])
            version = "latest"
        
        # 如果版本是 "latest"，获取实际的最新版本号
        if version == "latest":
            tags_api = f"https://data.jsdelivr.com/v1/package/npm/{package_name}"
            print(f"🔍 获取最新版本: {tags_api}")
            tags_response = requests.get(tags_api)
            tags_response.raise_for_status()
            tags_data = tags_response.json()
            version = tags_data["tags"]["latest"]
            print(f"✅ 最新版本: {version}")
        
        # 构建文件树 API URL
        tree_api = f"https://data.jsdelivr.com/v1/package/npm/{package_name}@{version}"
        print(f"🌳 获取文件树: {tree_api}")
        tree_response = requests.get(tree_api)
        tree_response.raise_for_status()
        tree_data = tree_response.json()
        
        # 查找目标路径下的文件
        target_files = []
        
        def traverse_files(files, current_path):
            """递归遍历文件树"""
            for item in files:
                item_path = os.path.join(current_path, item["name"])
                
                # 如果当前路径匹配目标路径
                if path and item_path.startswith(path.rstrip('/') + '/') or (not path and current_path == ""):
                    if item["type"] == "file":
                        # 获取相对于目标路径的文件名
                        rel_path = os.path.relpath(item_path, path) if path else item_path
                        target_files.append(rel_path)
                
                # 如果是目录，递归遍历
                if item["type"] == "directory" and "files" in item:
                    traverse_files(item["files"], item_path)
        
        # 开始遍历文件树
        traverse_files(tree_data["files"], "")
        
        print(f"📋 找到 {len(target_files)} 个文件")
        return target_files
        
    except Exception as e:
        print(f"❌ 获取文件列表失败: {str(e)}")
        return []

def download_file(url, output_path, is_binary=False):
    """下载文件并保存到指定路径"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        # 获取文件内容
        print(f"⬇️ 正在下载: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        content = response.text
        
        # 特殊处理：为 highlight.js 添加 UMD 包装
        if "highlight.js/lib/index.min.js" in url:
            print(f"⬇️ 正在处理: {url}")
            content = (
                "(function(f){if(typeof exports==='object'&&typeof module!=='undefined')"
                "{module.exports=f()}else if(typeof define==='function'&&define.amd)"
                "{define([],f)}else{var g;if(typeof window!=='undefined'){g=window}"
                "else if(typeof global!=='undefined'){g=global}else if(typeof self!=='undefined')"
                "{g=self}else{g=this}g.hljs = f()}})(function(){"
                f"{content}"
                "return hljs;});"
            )
            print(f"✅ 处理完成: {url}")
        
        # 保存文件
        if is_binary or not response.headers.get('Content-Type', '').startswith('text'):
            # 二进制文件（字体等）
            with open(output_path, 'wb') as f:
                f.write(content)
        else:
            # 文本文件（CSS/JS）
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✅ 成功下载: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 下载失败 [{url}]: {str(e)}")
        return False

def clear_target_directory(target_dir):
    """完全删除目标目录（而不仅仅是清空内容）"""
    target_path = Path(target_dir)
    if target_path.exists():
        print(f"🗑️ 完全删除目录: {target_dir}")
        shutil.rmtree(target_path)
    # 确保父目录存在（为后续创建做准备）
    target_path.parent.mkdir(parents=True, exist_ok=True)

def update_files(targets, temp_dir):
    """更新单个文件列表"""
    success = True
    updated_files = {}
    
    for url, output_path in targets.items():
        # 在临时目录创建文件
        temp_path = os.path.join(temp_dir, os.path.basename(output_path))
        file_success = download_file(url, temp_path)
        
        if file_success:
            updated_files[url] = (temp_path, output_path)
        else:
            success = False
    
    return success, updated_files

def update_directory(source_url, target_dir, temp_dir):
    """更新整个目录（先删除目标目录再重建）"""
    # 获取文件列表
    file_list = get_file_list(source_url)
    if not file_list:
        print("⚠️ 未获取到文件列表，跳过目录更新")
        return False, {}
    
    print(f"📋 目录包含 {len(file_list)} 个文件")
    
    # 完全删除目标目录
    clear_target_directory(target_dir)
    
    success = True
    updated_files = {}
    
    # 下载所有文件
    for filename in file_list:
        file_url = f"{source_url}{filename}"
        temp_path = os.path.join(temp_dir, filename)
        final_path = os.path.join(target_dir, filename)
        
        # 直接下载到最终位置（因为目录已被删除）
        file_success = download_file(file_url, final_path, is_binary=True)
        
        if file_success:
            updated_files[filename] = (None, final_path)  # 不需要移动，所以temp_path为None
        else:
            success = False
    
    return success, updated_files

def apply_updates(updated_files):
    """应用所有更新到目标位置（修改为跳过已直接下载的文件）"""
    for _, (temp_path, final_path) in updated_files.items():
        if temp_path is None:  # 目录文件已直接下载到目标位置
            continue
        # 确保目标目录存在
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        # 移动文件
        shutil.move(temp_path, final_path)
        print(f"➡️ 已移动: {final_path}")

def clear_target_directory(target_dir):
    """清空目标目录"""
    target_path = Path(target_dir)
    if target_path.exists():
        print(f"🧹 清空目标目录: {target_dir}")
        for item in target_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

def main():
    """主更新函数"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    overall_success = True
    all_updated_files = {}
    
    try:
        # 更新单个文件
        if TARGETS:
            print("\n" + "="*50)
            print("🚀 开始更新单个文件")
            print("="*50)
            files_success, files_updated = update_files(TARGETS, temp_dir)
            all_updated_files.update(files_updated)
            if not files_success:
                overall_success = False
        else:
            print("ℹ️ 没有配置单个文件更新")
            files_success = True
        
        # 更新目录
        if TARGETS_DIR:
            for source_url, target_dir in TARGETS_DIR.items():
                print("\n" + "="*50)
                print(f"🚀 开始更新目录: {source_url} -> {target_dir}")
                print("="*50)
                
                # 清空目标目录（准备更新）
                clear_target_directory(target_dir)
                
                dir_success, dir_updated = update_directory(source_url, target_dir, temp_dir)
                all_updated_files.update(dir_updated)
                
                if not dir_success:
                    overall_success = False
        else:
            print("ℹ️ 没有配置目录更新")
            dir_success = True
        
        # 应用所有更新（只有所有操作都成功时才更新）
        if overall_success and all_updated_files:
            print("\n" + "="*50)
            print("🔄 正在应用所有更新...")
            apply_updates(all_updated_files)
            print("🎉 所有更新完成!")
        elif not overall_success:
            print("\n" + "="*50)
            print("⚠️ 部分更新失败，保留原文件")
        
        return overall_success
        
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
            print("🧹 临时目录已清理")
        except Exception as e:
            print(f"⚠️ 清理临时目录时出错: {str(e)}")

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 脚本执行失败: {str(e)}")
        sys.exit(1)
