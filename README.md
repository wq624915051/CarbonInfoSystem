# CarbonInfoSystem

## How To Use
```
# 克隆gitee仓库
git clone https://gitee.com/nancyyyyy/CarbonInfoSystem.git
# 进入CarbonInfoSystem目录
cd CarbonInfoSystem
# 构建docker镜像
docker build --pull --rm -f "Dockerfile" -t carbon_info_system "." 
# 运行docker容器
docker run -dp PORT:10086 -v PATH2FILE:/code carbon_info_system
```

## zjh看我
1. ssh连接远程服务器
2. 进入CarbonInfoSystem目录
`cd /home/CarbonInfoSystem`
3. 拉取最新代码
`git pull`
3. 查看docker容器
`docker ps` 或者 `docker ps -a`
4. 重启docker容器
`docker restart CONTAINER_ID`
5. 退出远程服务器

## 文档整理
1. pdf文件命名 （股票代码得是6位数字）
2. Excel的格式为.xls、以及每一列的内容
3. 指标的关键词的格式
4. 碳中和系统的“关键词+数字”手动

## TODO
- [x] DEBUG = True; ALLOWED_HOSTS = []
- [x] 日志记录
- [x] 异常处理
- [x] PDF分析 - [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [x] [配置Tesseract OCR](https://zhuanlan.zhihu.com/p/420259031)
- [x] [自动同步Github仓库到Gitee仓库](https://gyx8899.gitbook.io/blog/share/syncgithubtogitee)