#!/usr/bin/env python3
"""
脚本用于打包已下载的模型文件，以便在离线服务器上使用。

使用方法:
    python package_models.py

这会将模型文件复制到 ./models/ 目录下，然后可以打包传输到其他服务器。
"""

import os
import shutil
from pathlib import Path
from huggingface_hub import snapshot_download

# 模型仓库ID
TURBO_REPO_ID = "ResembleAI/chatterbox-turbo"
MULTILINGUAL_REPO_ID = "ResembleAI/chatterbox"

# 输出目录
OUTPUT_DIR = Path("./models")
TURBO_DIR = OUTPUT_DIR / "chatterbox-turbo"
MULTILINGUAL_DIR = OUTPUT_DIR / "chatterbox"


def find_hf_cache_dir():
    """查找 Hugging Face 缓存目录"""
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    if cache_dir.exists():
        return cache_dir
    # 如果环境变量设置了缓存目录
    if os.getenv("HF_HOME"):
        return Path(os.getenv("HF_HOME")) / "hub"
    if os.getenv("HUGGINGFACE_HUB_CACHE"):
        return Path(os.getenv("HUGGINGFACE_HUB_CACHE"))
    return cache_dir


def find_model_in_cache(repo_id):
    """在缓存中查找模型目录"""
    cache_dir = find_hf_cache_dir()
    
    # Hugging Face 缓存目录结构: models--{org}--{repo}/snapshots/{hash}/
    repo_name = repo_id.replace("/", "--")
    
    # 查找所有可能的快照
    repo_cache_dir = cache_dir / f"models--{repo_name}"
    if not repo_cache_dir.exists():
        print(f"警告: 未找到缓存目录 {repo_cache_dir}")
        return None
    
    # 查找最新的快照
    snapshots_dir = repo_cache_dir / "snapshots"
    if not snapshots_dir.exists():
        print(f"警告: 未找到快照目录 {snapshots_dir}")
        return None
    
    # 获取所有快照，选择最新的
    snapshots = list(snapshots_dir.iterdir())
    if not snapshots:
        print(f"警告: 快照目录为空 {snapshots_dir}")
        return None
    
    # 按修改时间排序，选择最新的
    latest_snapshot = max(snapshots, key=lambda p: p.stat().st_mtime)
    print(f"找到模型缓存: {latest_snapshot}")
    return latest_snapshot


def copy_model_files(source_dir, target_dir):
    """复制模型文件到目标目录"""
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    source_dir = Path(source_dir)
    if not source_dir.exists():
        print(f"错误: 源目录不存在 {source_dir}")
        return False
    
    # 复制所有文件
    files_copied = 0
    for file_path in source_dir.iterdir():
        if file_path.is_file():
            target_file = target_dir / file_path.name
            print(f"复制: {file_path.name}")
            shutil.copy2(file_path, target_file)
            files_copied += 1
    
    print(f"已复制 {files_copied} 个文件到 {target_dir}")
    return True


def download_if_not_cached(repo_id, output_dir):
    """如果缓存中没有，则下载模型"""
    cache_dir = find_hf_cache_dir()
    repo_name = repo_id.replace("/", "--")
    repo_cache_dir = cache_dir / f"models--{repo_name}"
    
    if not repo_cache_dir.exists():
        print(f"缓存中未找到 {repo_id}，开始下载...")
        try:
            local_path = snapshot_download(
                repo_id=repo_id,
                token=os.getenv("HF_TOKEN") or False,
            )
            print(f"下载完成: {local_path}")
            return local_path
        except Exception as e:
            print(f"下载失败: {e}")
            return None
    
    # 从缓存复制
    snapshot_dir = find_model_in_cache(repo_id)
    if snapshot_dir:
        copy_model_files(snapshot_dir, output_dir)
        return str(output_dir)
    
    return None


def package_pkuseg_models():
    """打包 pkuseg 模型文件"""
    pkuseg_home = Path.home() / ".pkuseg"
    if not pkuseg_home.exists():
        print("警告: pkuseg 模型目录不存在，尝试预先下载...")
        try:
            from spacy_pkuseg import pkuseg
            # 初始化 pkuseg 会自动下载模型
            seg = pkuseg()
            print("pkuseg 模型下载完成")
        except Exception as e:
            print(f"警告: 无法下载 pkuseg 模型: {e}")
            return None
    
    # 复制 pkuseg 模型到输出目录
    pkuseg_output = OUTPUT_DIR / "pkuseg"
    if pkuseg_home.exists():
        print(f"复制 pkuseg 模型从 {pkuseg_home} 到 {pkuseg_output}...")
        shutil.copytree(pkuseg_home, pkuseg_output, dirs_exist_ok=True)
        print(f"pkuseg 模型已复制到: {pkuseg_output}")
        return pkuseg_output
    
    return None


def main():
    """主函数"""
    print("=" * 60)
    print("Chatterbox 模型打包工具")
    print("=" * 60)
    
    # 创建输出目录
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 处理 Turbo 模型
    print("\n[1/3] 处理 Turbo 模型 (chatterbox-turbo)...")
    turbo_snapshot = find_model_in_cache(TURBO_REPO_ID)
    if turbo_snapshot:
        copy_model_files(turbo_snapshot, TURBO_DIR)
    else:
        print("尝试下载 Turbo 模型...")
        download_if_not_cached(TURBO_REPO_ID, TURBO_DIR)
    
    # 处理多语言模型
    print("\n[2/3] 处理多语言模型 (chatterbox)...")
    multilingual_snapshot = find_model_in_cache(MULTILINGUAL_REPO_ID)
    if multilingual_snapshot:
        copy_model_files(multilingual_snapshot, MULTILINGUAL_DIR)
    else:
        print("尝试下载多语言模型...")
        download_if_not_cached(MULTILINGUAL_REPO_ID, MULTILINGUAL_DIR)
    
    # 处理 pkuseg 模型
    print("\n[3/3] 处理 pkuseg 模型（用于中文分词）...")
    pkuseg_output = package_pkuseg_models()
    if not pkuseg_output:
        print("警告: pkuseg 模型未找到，中文分词功能可能无法使用")
    
    print("\n" + "=" * 60)
    print("打包完成！")
    print(f"模型文件已保存到: {OUTPUT_DIR.absolute()}")
    print("\n目录结构:")
    print(f"  {OUTPUT_DIR}/")
    print(f"    ├── chatterbox-turbo/")
    print(f"    ├── chatterbox/")
    if pkuseg_output:
        print(f"    └── pkuseg/")
    print("\n下一步:")
    print(f"1. 将 {OUTPUT_DIR} 目录打包: tar -czf models.tar.gz {OUTPUT_DIR}")
    print("2. 将 models.tar.gz 传输到目标服务器")
    print("3. 在目标服务器上解压: tar -xzf models.tar.gz")
    print("4. 设置环境变量 PKUSEG_HOME 指向 models/pkuseg（如果需要）")
    print("5. 修改代码使用 from_local() 方法加载模型")
    print("=" * 60)


if __name__ == "__main__":
    main()

