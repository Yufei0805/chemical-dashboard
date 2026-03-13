# 国内化工品现货价格看板

自动更新的化工品价格看板，数据来源：AkShare (生意社100ppi.com)

## 功能特点
- 📊 19个化工品实时价格
- 📈 多周期涨跌幅统计（当日/1周/1月/3月/6月/1年）
- 📉 近1年价格走势图
- 🔄 每天自动更新1次（19:00）

## 在线访问
网站将在部署后自动生成访问地址

## 技术栈
- Python + AkShare
- ECharts 5.4.3
- GitHub Actions 自动部署
- GitHub Pages 托管

## 本地运行
```bash
pip install akshare pandas
python generate_akshare_dashboard_fast.py
```

## 更新时间
- 每天北京时间 19:00


