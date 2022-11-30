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
docker run -dp 10086:10086 -v PATH2FILE:/code carbon_info_system
```

## TODO
- [ ] PDF分析
- [ ] 异常处理
- [ ] 配置Tesseract OCR
- [ ] DEBUG = True; ALLOWED_HOSTS = []

[自动同步你的 Github 仓库到 Gitee 仓库](https://gyx8899.gitbook.io/blog/share/syncgithubtogitee)