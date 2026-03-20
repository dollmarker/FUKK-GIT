# FUKK GIT 使用说明

## 工具简介

**FUKK GIT** - 一个简洁高效的Git仓库敏感信息扫描工具，专门为CTF比赛设计

**作者：dollmarker哥哥**

## 功能特性

- ✅ 支持本地Git仓库扫描
- ✅ 支持远程Git仓库自动下载
- ✅ 正则表达式匹配敏感信息
- ✅ 结果红色高亮显示
- ✅ 无文件保存，直接终端输出
- ✅ 自动清理临时文件



## 使用方法：



### (1)安装依赖

```
# 必需依赖
pip install colorama

# 可选依赖（增强远程克隆功能）
pip install git-dumper
```

### (2)基本命令

```
# 扫描当前目录Git仓库
python fukkgit.py

# 扫描指定目录
python fukkgit.py -d /path/to/repo

# 下载并扫描远程Git仓库
python fukkgit.py -u http://target.com/.git/
```

### (3)匹配字段

```
# 使用单个匹配模式
python fukkgit.py -m "ctfhub{.*}"

# 使用多个匹配模式
python fukkgit.py -m "flag{.*}" -m "ctf{.*}" -m "key{.*}"

# 组合使用
python fukkgit.py -u http://target.com/.git/ -m "flag{.*}"
```

### (4)从文件读取模式

```
# 从文件读取多个匹配模式
python fukkgit.py -f patterns.txt
```

`patterns.txt`文件格式：

```
flag\{.*\}
ctf\{.*\}
key\{.*\}
secret_[A-Za-z0-9_]+
```



## 参数说明

| 参数          | 说明               | 示例                          |
| ------------- | ------------------ | ----------------------------- |
| `-d, --dir`   | 本地Git目录        | `-d ./repo`                   |
| `-u, --url`   | 远程Git仓库URL     | `-u http://example.com/.git/` |
| `-m, --match` | 正则表达式匹配模式 | `-m "flag{.*}"`               |
| `-f, --file`  | 从文件读取模式     | `-f patterns.txt`             |
| `-q, --quiet` | 安静模式（不交互） | `-q`                          |

## 注意事项

1. 确保已安装Git命令行工具
2. 扫描远程仓库需要网络连接
3. 结果会自动去重
4. 临时目录会自动清理
5. 红色高亮在支持ANSI颜色的终端中显示



### 参考脚本如下：

```


#!/bin/bash

echo "[*] Git Repository Flag Hunter"
echo "================================"

1. Stash检查

echo -e "\n[+] Checking stashes..."
git stash list
for i in {0..10}; do
    git stash show -p stash@{$i} 2>/dev/null | grep -i "flag\|ctf"
done

2. 提交历史检查

echo -e "\n[+] Checking commit history..."
git log --all --oneline | grep -i "flag\|add\|remove\|delete"

3. Reflog检查

echo -e "\n[+] Checking reflog..."
git reflog | head -20

4. 遍历所有提交查找flag

echo -e "\n[+] Searching in all commits..."
for commit in $(git log --all --format=%H); do
    git show $commit | grep -iE "flag\{|ctf\{|flag:" && echo "Found in: $commit"
done

5. 检查所有分支

echo -e "\n[+] Checking all branches..."
git branch -a

6. 检查未引用对象

echo -e "\n[+] Checking unreachable objects..."
git fsck --unreachable

7. 搜索所有对象

echo -e "\n[+] Searching in all objects..."
find .git/objects -type f | while read obj; do
    hash=$(echo $obj | sed 's/\.git\/objects\///g' | tr -d '/')
    git cat-file -p $hash 2>/dev/null | grep -iE "flag\{|ctf\{" && echo "Found in object: $hash"
done

echo -e "\n[*] Scan complete!"
```





