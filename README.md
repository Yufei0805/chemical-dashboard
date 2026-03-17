# 国内化工品现货价格看板

自动更新的化工品价格看板，数据来源：AkShare (生意社100ppi.com)

## 功能特点
- 📊 19个化工品实时价格
- 📈 多周期涨跌幅统计（当日/1周/1月/3月/6月/1年）
- 📉 近1年价格走势图
- 🔄 工作日自动更新（18:50）
- ⚡ 增量更新机制，执行时间仅需30-60秒
- 📦 50+相关股票实时涨跌幅

## 在线访问
网站将在部署后自动生成访问地址

## 技术栈
- Python + AkShare + baostock
- ECharts 5.4.3
- GitHub Actions 自动部署
- GitHub Pages 托管

## 本地运行
```bash
pip install akshare pandas baostock chinese-calendar
python generate_akshare_dashboard_fast.py
```

## 更新时间
- 工作日（周一至周五）北京时间 18:50 自动更新
- 首次运行获取400天完整历史数据（约8-10分钟）
- 后续运行增量更新（约30-60秒）

## 性能优化
- ✅ 实现数据持久化和增量更新机制
- ✅ 执行时间从8-10分钟降至30-60秒（提升12-20倍）
- ✅ API请求数减少99.5%
- ✅ 显著降低连接超时风险
