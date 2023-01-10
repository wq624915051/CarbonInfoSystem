# 重命名PDF文件
把PDF重命名成 股票代码_公司名_年份.pdf

# 批量测试各个PDF文件
1. 将[在线文档](https://www.kdocs.cn/l/cd9u5wqfI48p)保存到本地
2. 保留B、C、D列，并另存为csv格式文件pno_all.csv
3. 每次从pno_all.csv中复制几行到pno.csv，并删除原先的内容
4. 在tmux中运行`python3 spider.py`

# 从downlods中获取生成的EXCEL [TODO]