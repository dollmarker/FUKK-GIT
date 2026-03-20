#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fukkgit - 简洁版
dollmarker哥哥的工具
"""

import subprocess
import os
import sys
import re
import argparse
import tempfile
import shutil

def run_command(cmd, cwd=None, timeout=30):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore',
            timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: Command timeout"
    except Exception as e:
        return f"Error: {e}"

def clone_git_repo(url, output_dir=None):
    """使用git-dumper下载远程Git仓库"""
    print(f"[*] 正在克隆远程仓库: {url}")
    
    if not output_dir:
        temp_dir = tempfile.mkdtemp(prefix="git_scan_")
        output_dir = temp_dir
    
    try:
        subprocess.run(["git-dumper", "--help"], capture_output=True, check=True)
        cmd = f"git-dumper {url} {output_dir}"
    except:
        cmd = f"git clone {url} {output_dir}"
    
    print(f"[*] 执行命令: {cmd}")
    output = run_command(cmd, timeout=300)
    
    if "Error" in output or "fatal" in output:
        print(f"[-] 克隆失败")
        if os.path.exists(output_dir) and output_dir.startswith(tempfile.gettempdir()):
            shutil.rmtree(output_dir, ignore_errors=True)
        return None
    
    print(f"[+] 仓库已下载到: {output_dir}")
    return output_dir

def find_git_dir(start_dir="."):
    """查找.git目录"""
    git_dir = os.path.abspath(start_dir)
    
    if os.path.basename(git_dir) == ".git" and os.path.isdir(git_dir):
        return git_dir
    
    for root, dirs, files in os.walk(start_dir):
        if ".git" in dirs:
            git_path = os.path.join(root, ".git")
            if os.path.isdir(git_path):
                return git_path
    
    if os.path.exists(os.path.join(git_dir, "HEAD")):
        return git_dir
    
    return None

def get_search_patterns(args_match):
    """获取搜索模式"""
    patterns = [
        r'flag\{[^}]*\}',
        r'FLAG\{[^}]*\}',
        r'ctf\{[^}]*\}',
        r'CTF\{[^}]*\}',
        r'key\{[^}]*\}',
    ]
    
    if args_match:
        patterns = args_match if isinstance(args_match, list) else [args_match]
        print(f"[*] 使用自定义搜索模式:")
    else:
        print(f"[*] 使用默认搜索模式:")
    
    for i, pattern in enumerate(patterns, 1):
        print(f"  {i}. {pattern}")
    
    if not args_match:
        print("\n是否添加自定义模式? (y/n): ", end="")
        if input().strip().lower() in ['y', 'yes']:
            print("输入自定义正则表达式 (输入'done'结束):")
            while True:
                pattern = input("> ").strip()
                if pattern.lower() == 'done':
                    break
                if pattern:
                    try:
                        re.compile(pattern)
                        patterns.append(pattern)
                        print(f"[+] 已添加: {pattern}")
                    except:
                        print("[!] 无效的正则表达式")
    
    return patterns

def red_text(text):
    """返回红色文本"""
    return f"\033[91m{text}\033[0m"

def search_in_git(git_dir, patterns):
    """在Git仓库中搜索"""
    all_flags = []
    
    search_locations = [
        ("stash", "git stash list"),
        ("commit_messages", "git log --all --oneline"),
        ("reflog", "git reflog"),
        ("current_files", r'git grep -i "flag\|ctf\|key" -- "*" 2>/dev/null'),
    ]
    
    for name, cmd in search_locations:
        print(f"[*] 搜索: {name}")
        output = run_command(cmd, git_dir)
        if output and "Error" not in output and "fatal" not in output:
            for pattern in patterns:
                matches = re.findall(pattern, output, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        for item in match:
                            if item and item.strip():
                                all_flags.append((item.strip(), pattern, name))
                    elif match and match.strip():
                        all_flags.append((match.strip(), pattern, name))
    
    print("[*] 深度搜索提交内容...")
    commits = run_command("git log --all --format=%H", git_dir)
    if commits:
        commit_list = commits.split('\n')
        for i, commit in enumerate(commit_list[:20], 1):
            if commit:
                print(f"\r[*] 进度: {i}/20", end="")
                content = run_command(f"git show {commit}", git_dir)
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if match and match.strip():
                            all_flags.append((match.strip(), pattern, f"commit_{commit[:8]}"))
        print()
    
    return all_flags

def display_results(flags, patterns, git_dir):
    """显示结果"""
    print(f"\n{'='*60}")
    print("扫描结果")
    print('='*60)
    
    if not flags:
        print("未找到匹配项")
        return
    
    unique_flags = []
    seen = set()
    for flag, pattern, source in flags:
        if flag not in seen:
            seen.add(flag)
            unique_flags.append((flag, pattern, source))
    
    print(f"找到 {len(unique_flags)} 个唯一匹配项:\n")
    
    from collections import defaultdict
    groups = defaultdict(list)
    for flag, pattern, source in unique_flags:
        groups[source].append((flag, pattern))
    
    for source, items in groups.items():
        print(f"来源: {source}")
        print("-"*40)
        for flag, pattern in items:
            print(f"  {red_text(flag)}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Git仓库Flag扫描工具')
    parser.add_argument('-d', '--dir', help='本地Git目录')
    parser.add_argument('-u', '--url', help='远程Git仓库URL')
    parser.add_argument('-m', '--match', action='append', help='搜索模式(正则表达式)，可多次使用')
    parser.add_argument('-f', '--file', help='从文件读取搜索模式')
    parser.add_argument('-q', '--quiet', action='store_true', help='安静模式')
    args = parser.parse_args()
    
    print(f"\033[92m{'='*60}")
    print("FUKK GIT改进版")
    print("dollmarker哥哥的工具")
    print('='*60 + '\033[0m')
    
    git_dir = None
    temp_dir = None
    
    try:
        if args.url:
            temp_dir = clone_git_repo(args.url)
            if not temp_dir:
                return
            git_dir = find_git_dir(temp_dir)
        elif args.dir:
            git_dir = find_git_dir(args.dir)
        else:
            git_dir = find_git_dir(".")
        
        if not git_dir:
            print("[!] 未找到Git仓库")
            return
        
        print(f"[+] Git目录: {git_dir}")
        
        if args.file:
            with open(args.file, 'r') as f:
                patterns = [line.strip() for line in f if line.strip()]
        else:
            patterns = get_search_patterns(args.match)
        
        repo_dir = os.path.dirname(git_dir) if git_dir.endswith('.git') else git_dir
        original_dir = os.getcwd()
        os.chdir(repo_dir)
        
        flags = search_in_git(git_dir, patterns)
        
        display_results(flags, patterns, git_dir)
        
        os.chdir(original_dir)
        
    finally:
        if temp_dir and os.path.exists(temp_dir) and temp_dir.startswith(tempfile.gettempdir()):
            try:
                shutil.rmtree(temp_dir)
                print(f"[*] 已清理临时目录")
            except:
                pass
    
    print(f"\n{'='*60}")
    print("[*] 扫描完成")
    print('='*60)

if __name__ == "__main__":
    main()