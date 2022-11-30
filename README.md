# CarbonInfoSystem

## How To Use
[Docker Image](https://hub.docker.com/repository/docker/bbkkbkk/carbon-info-system_v1.0)
docker build --pull --rm -f "Dockerfile" -t CarbonInfoSystem "." 
docker run -dp 10086:10086 CarbonInfoSystem --restart=always

## TODO
- [ ] PDF分析
- [ ] 异常处理
- [ ] 配置Tesseract OCR

[自动同步你的 Github 仓库到 Gitee 仓库](https://gyx8899.gitbook.io/blog/share/syncgithubtogitee)