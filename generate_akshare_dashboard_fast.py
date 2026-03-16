#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用AkShare生成化工品价格看板（快速版）
使用 futures_spot_price_daily 一次性获取所有历史数据
数据来源：生意社(100ppi.com)
优势：无API限流，数据稳定，速度快
"""

import akshare as ak
import json
from datetime import datetime, timedelta, timezone
import pandas as pd
import baostock as bs
import chinese_calendar as cc

# 设置北京时区
BEIJING_TZ = timezone(timedelta(hours=8))

def is_workday():
    """检查今天是否是工作日（排除周末和中国法定节假日）"""
    today = datetime.now(BEIJING_TZ).date()
    return cc.is_workday(today)

def calculate_period_change(df, symbol, days):
    """计算指定周期的涨跌幅（按日历天数）"""
    symbol_data = df[df['symbol'] == symbol].copy()
    if len(symbol_data) == 0:
        return None

    symbol_data = symbol_data.sort_values('date')
    symbol_data['date_dt'] = pd.to_datetime(symbol_data['date'])

    current_price = symbol_data['spot_price'].iloc[-1]
    current_date = symbol_data['date_dt'].iloc[-1]

    # 计算目标日期（日历天数）
    target_date = current_date - timedelta(days=days)

    # 找到目标日期之前最近的交易日数据
    past_data = symbol_data[symbol_data['date_dt'] <= target_date]

    if len(past_data) == 0:
        return None

    past_price = past_data['spot_price'].iloc[-1]
    change = (current_price / past_price - 1) * 100

    return round(change, 2)

def calculate_daily_change(df, symbol):
    """计算当日涨跌幅"""
    symbol_data = df[df['symbol'] == symbol].copy()
    if len(symbol_data) < 2:
        return None

    symbol_data = symbol_data.sort_values('date')
    current_price = symbol_data['spot_price'].iloc[-1]
    previous_price = symbol_data['spot_price'].iloc[-2]
    change = (current_price / previous_price - 1) * 100

    return round(change, 2)

def generate_akshare_html_fast():
    """生成AkShare版本的HTML（快速版）"""
    # 检查是否是工作日
    if not is_workday():
        print("今天不是工作日，跳过更新")
        return

    print("="*80)
    print("开始生成AkShare化工品价格看板（快速版）")
    print("="*80)

    # 化工品配置（19个）
    chemicals = {
        # 塑料树脂类
        'L': '聚乙烯',
        'V': 'PVC',
        'PP': '聚丙烯',
        # 芳烃烯烃类
        'EB': '苯乙烯',
        'PX': 'PX',
        'EG': '乙二醇',
        'TA': 'PTA',
        # 醇类气体
        'MA': '甲醇',
        'PG': '液化石油气',
        # 橡胶类
        'RU': '天然橡胶',
        'BR': '丁二烯橡胶',
        # 纤维纺织
        'PF': '短纤',
        'SP': '纸浆',
        # 化肥无机
        'UR': '尿素',
        'SA': '纯碱',
        # 能源化工
        'FU': '燃料油',
        'BU': '沥青',
        # 其他化工
        'SS': '不锈钢',
        'FG': '玻璃',
    }

    # 化工品分类映射
    chemical_categories = {
        '聚乙烯': '塑料树脂',
        'PVC': '塑料树脂',
        '聚丙烯': '塑料树脂',
        '苯乙烯': '芳烃烯烃',
        'PX': '芳烃烯烃',
        '乙二醇': '芳烃烯烃',
        'PTA': '芳烃烯烃',
        '甲醇': '醇类气体',
        '液化石油气': '醇类气体',
        '天然橡胶': '橡胶类',
        '丁二烯橡胶': '橡胶类',
        '短纤': '纤维纺织',
        '纸浆': '纤维纺织',
        '尿素': '化肥无机',
        '纯碱': '化肥无机',
        '燃料油': '能源化工',
        '沥青': '能源化工',
        '不锈钢': '其他',
        '玻璃': '其他',
    }

    # 化工品相关股票映射
    chemical_stocks = {
        '聚乙烯': [
            {'name': '中国石化', 'code': '600028'},
            {'name': '中国石油', 'code': '601857'},
            {'name': '恒力石化', 'code': '600346'},
            {'name': '荣盛石化', 'code': '002493'},
            {'name': '东方盛虹', 'code': '000301'},
            {'name': '卫星化学', 'code': '002648'},
            {'name': '宝丰能源', 'code': '600989'}
        ],
        'PVC': [
            {'name': '中泰化学', 'code': '002092'},
            {'name': '北元集团', 'code': '601568'},
            {'name': '新疆天业', 'code': '600075'},
            {'name': '华塑股份', 'code': '600935'},
            {'name': '天原股份', 'code': '002388'},
            {'name': '英力特', 'code': '000635'}
        ],
        '聚丙烯': [
            {'name': '中国石化', 'code': '600028'},
            {'name': '中国石油', 'code': '601857'},
            {'name': '恒力石化', 'code': '600346'},
            {'name': '荣盛石化', 'code': '002493'},
            {'name': '东方盛虹', 'code': '000301'},
            {'name': '宝丰能源', 'code': '600989'},
            {'name': '卫星化学', 'code': '002648'}
        ],
        '苯乙烯': [
            {'name': '华锦股份', 'code': '000059'},
            {'name': '双良节能', 'code': '600481'},
            {'name': '双环科技', 'code': '000707'},
            {'name': '卫星化学', 'code': '002648'},
            {'name': '天原股份', 'code': '002388'}
        ],
        'PX': [
            {'name': '荣盛石化', 'code': '002493'},
            {'name': '恒力石化', 'code': '600346'},
            {'name': '东方盛虹', 'code': '000301'},
            {'name': '中国石化', 'code': '600028'},
            {'name': '上海石化', 'code': '600688'}
        ],
        '乙二醇': [
            {'name': '荣盛石化', 'code': '002493'},
            {'name': '恒力石化', 'code': '600346'},
            {'name': '东方盛虹', 'code': '000301'},
            {'name': '卫星化学', 'code': '002648'},
            {'name': '万凯新材', 'code': '301216'},
            {'name': '新凤鸣', 'code': '603225'}
        ],
        'PTA': [
            {'name': '荣盛石化', 'code': '002493'},
            {'name': '恒力石化', 'code': '600346'},
            {'name': '东方盛虹', 'code': '000301'},
            {'name': '恒逸石化', 'code': '000703'},
            {'name': '新凤鸣', 'code': '603225'},
            {'name': '三房巷', 'code': '600375'}
        ],
        '甲醇': [
            {'name': '宝丰能源', 'code': '600989'},
            {'name': '兖矿能源', 'code': '600188'},
            {'name': '中煤能源', 'code': '601898'},
            {'name': '华鲁恒升', 'code': '600426'},
            {'name': '新奥股份', 'code': '600803'},
            {'name': '九丰能源', 'code': '605090'}
        ],
        '液化石油气': [
            {'name': '九丰能源', 'code': '605090'},
            {'name': '东华能源', 'code': '002221'},
            {'name': '广汇能源', 'code': '600256'},
            {'name': '新奥股份', 'code': '600803'},
            {'name': '卫星化学', 'code': '002648'}
        ],
        '天然橡胶': [
            {'name': '海南橡胶', 'code': '601118'},
            {'name': '中化国际', 'code': '600500'}
        ],
        '丁二烯橡胶': [
            {'name': '齐翔腾达', 'code': '002408'},
            {'name': '华锦股份', 'code': '000059'},
            {'name': '中国石化', 'code': '600028'},
            {'name': '中国石油', 'code': '601857'}
        ],
        '短纤': [
            {'name': '三友化工', 'code': '600409'},
            {'name': '澳洋健康', 'code': '002172'},
            {'name': '南京化纤', 'code': '600880'},
            {'name': '新乡化纤', 'code': '000949'},
            {'name': '吉林化纤', 'code': '000420'},
            {'name': '江南高纤', 'code': '600527'},
            {'name': '新凤鸣', 'code': '603225'},
            {'name': '恒逸石化', 'code': '000703'}
        ],
        '纸浆': [
            {'name': '太阳纸业', 'code': '002078'},
            {'name': '晨鸣纸业', 'code': '000488'},
            {'name': '山鹰国际', 'code': '600567'}
        ],
        '尿素': [
            {'name': '华鲁恒升', 'code': '600426'},
            {'name': '云天化', 'code': '600096'},
            {'name': '湖北宜化', 'code': '000422'},
            {'name': '中煤能源', 'code': '601898'},
            {'name': '四川美丰', 'code': '000735'}
        ],
        '纯碱': [
            {'name': '远兴能源', 'code': '000683'},
            {'name': '山东海化', 'code': '000822'},
            {'name': '三友化工', 'code': '600409'},
            {'name': '金晶科技', 'code': '600586'},
            {'name': '双环科技', 'code': '000707'}
        ],
        '燃料油': [
            {'name': '中国石化', 'code': '600028'},
            {'name': '中国石油', 'code': '601857'},
            {'name': '上海石化', 'code': '600688'},
            {'name': '博汇股份', 'code': '300839'},
            {'name': '龙宇燃油', 'code': '603003'},
            {'name': '荣盛石化', 'code': '002493'}
        ],
        '沥青': [
            {'name': '宝利国际', 'code': '300135'},
            {'name': '国创高新', 'code': '002377'},
            {'name': '中国石化', 'code': '600028'},
            {'name': '中国石油', 'code': '601857'},
            {'name': '华锦股份', 'code': '000059'}
        ],
        '不锈钢': [
            {'name': '太钢不锈', 'code': '000825'},
            {'name': '甬金股份', 'code': '603995'},
            {'name': '永兴材料', 'code': '002756'},
            {'name': '酒钢宏兴', 'code': '600307'}
        ],
        '玻璃': [
            {'name': '旗滨集团', 'code': '601636'},
            {'name': '福莱特', 'code': '601865'},
            {'name': '南玻A', 'code': '000012'},
            {'name': '福耀玻璃', 'code': '600660'},
            {'name': '金晶科技', 'code': '600586'}
        ]
    }

    # 一次性获取所有品种近1年的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=400)  # 多取一些天数确保有足够数据

    print(f"\n正在获取 {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')} 的数据...")
    print("这可能需要1-2分钟，请稍候...\n")

    try:
        # 一次性获取所有品种的历史数据
        df_all = ak.futures_spot_price_daily(
            start_day=start_date.strftime('%Y%m%d'),
            end_day=end_date.strftime('%Y%m%d'),
            vars_list=list(chemicals.keys())
        )

        print(f"✓ 数据获取成功！共 {len(df_all)} 条记录")
        print(f"✓ 包含品种: {df_all['symbol'].unique().tolist()}\n")

    except Exception as e:
        print(f"✗ 数据获取失败: {e}")
        return

    # 获取股票最新交易日涨跌幅（使用baostock + AkShare双重数据源）
    print("正在获取股票最新交易日涨跌幅...")
    stock_changes = {}

    # 收集所有需要查询的股票代码（排除港股）
    all_stock_codes = set()
    hk_stock_codes = set()
    for stocks in chemical_stocks.values():
        for stock in stocks:
            code = stock['code']
            if '.HK' in code:
                hk_stock_codes.add(code)
            else:
                all_stock_codes.add(code)

    print(f"需要查询 {len(all_stock_codes)} 只A股，跳过 {len(hk_stock_codes)} 只港股")

    # 登录baostock
    lg = bs.login()
    if lg.error_code != '0':
        print(f"✗ baostock登录失败: {lg.error_msg}")
        print("将跳过股票涨跌幅获取\n")
    else:
        print("✓ baostock登录成功")

        # 获取最近交易日日期
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

        success_count = 0
        failed_stocks = []
        for i, code in enumerate(all_stock_codes, 1):
            try:
                # baostock需要带市场前缀的代码
                if code.startswith('6'):
                    bs_code = f'sh.{code}'
                else:
                    bs_code = f'sz.{code}'

                # 查询历史K线数据
                rs = bs.query_history_k_data_plus(
                    bs_code,
                    "date,close",
                    start_date=start_date,
                    end_date=end_date,
                    frequency="d",
                    adjustflag="3"
                )

                if rs.error_code == '0':
                    data_list = []
                    while (rs.error_code == '0') & rs.next():
                        data_list.append(rs.get_row_data())

                    if len(data_list) >= 2:
                        # 取最后两个交易日
                        latest_close = float(data_list[-1][1])
                        prev_close = float(data_list[-2][1])
                        change_pct = (latest_close - prev_close) / prev_close * 100
                        stock_changes[code] = round(change_pct, 2)
                        success_count += 1
                    else:
                        failed_stocks.append(f"{code}(数据不足{len(data_list)}条)")
                else:
                    failed_stocks.append(f"{code}(查询错误:{rs.error_msg})")

                if i % 20 == 0:
                    print(f"  已完成 {i}/{len(all_stock_codes)}")

            except Exception as e:
                failed_stocks.append(f"{code}(异常:{str(e)})")
                continue

        bs.logout()
        print(f"✓ 成功获取 {success_count}/{len(all_stock_codes)} 只股票涨跌幅")

        # 对于baostock失败的股票，用AkShare再试一次
        if failed_stocks:
            print(f"正在用AkShare重试失败的股票...")
            retry_count = 0
            for failed_info in failed_stocks[:]:
                code = failed_info.split('(')[0]
                try:
                    df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="")
                    if len(df) >= 2:
                        latest = df.iloc[-1]
                        prev = df.iloc[-2]
                        change_pct = (latest['收盘'] - prev['收盘']) / prev['收盘'] * 100
                        stock_changes[code] = round(change_pct, 2)
                        success_count += 1
                        retry_count += 1
                        failed_stocks.remove(failed_info)
                except:
                    pass
            if retry_count > 0:
                print(f"✓ AkShare重试成功 {retry_count} 只")

        if failed_stocks:
            print(f"✗ 最终失败股票: {', '.join(failed_stocks)}")
        print()

    # 为股票添加涨跌幅
    for name, stocks in chemical_stocks.items():
        for stock in stocks:
            stock['change'] = stock_changes.get(stock['code'], None)

    all_data = []

    # 处理每个化工品
    for symbol, name in chemicals.items():
        print(f"正在处理 {name} ({symbol})...")

        symbol_data = df_all[df_all['symbol'] == symbol].copy()

        if len(symbol_data) == 0:
            print(f"✗ {name}: 无数据")
            continue

        symbol_data = symbol_data.sort_values('date')
        current_price = symbol_data['spot_price'].iloc[-1]
        latest_date = symbol_data['date'].iloc[-1]

        # 计算涨跌幅
        change_daily = calculate_daily_change(df_all, symbol)
        change_1w = calculate_period_change(df_all, symbol, 7)
        change_1m = calculate_period_change(df_all, symbol, 30)
        change_3m = calculate_period_change(df_all, symbol, 90)
        change_6m = calculate_period_change(df_all, symbol, 180)
        change_1y = calculate_period_change(df_all, symbol, 365)

        # 准备图表数据（最近1年）
        one_year_ago = pd.to_datetime(latest_date) - timedelta(days=365)
        chart_data_df = symbol_data[pd.to_datetime(symbol_data['date']) >= one_year_ago]

        chart_data = [
            {
                'date': row['date'],
                'price': float(row['spot_price'])
            }
            for _, row in chart_data_df.iterrows()
        ]

        # 完整历史数据
        full_data = [
            {
                'date': row['date'],
                'price': float(row['spot_price'])
            }
            for _, row in symbol_data.iterrows()
        ]

        all_data.append({
            'name': name,
            'category': chemical_categories.get(name, '其他'),
            'price': round(float(current_price), 2),
            'change_daily': change_daily,
            'change_1w': change_1w,
            'change_1m': change_1m,
            'change_3m': change_3m,
            'change_6m': change_6m,
            'change_1y': change_1y,
            'chart_data': chart_data,
            'full_data': full_data,
            'update_time': latest_date,
            'related_stocks': chemical_stocks.get(name, [])
        })

        print(f"✓ {name}: {current_price:.2f} 元/吨，历史数据 {len(full_data)} 条，图表数据 {len(chart_data)} 条")

    # 读取HTML模板
    template_path = 'chemical_dashboard_template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()

    # 标题保持不变（不添加AkShare版标识）

    # 修改数据提供方
    html_template = html_template.replace(
        '数据提供: 同花顺iFinD经济数据库',
        '数据提供: AkShare'
    )

    # 替换数据
    html_content = html_template.replace(
        '/* DATA_PLACEHOLDER */',
        f'const chemicalData = {json.dumps(all_data, ensure_ascii=False, indent=2)};'
    )

    html_content = html_content.replace(
        '/* UPDATE_TIME_PLACEHOLDER */',
        f'const updateTime = "{datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")}";'
    )

    # 保存静态HTML
    output_file = 'index.html'  # GitHub Actions部署时使用
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("\n" + "="*80)
    print(f"✓ AkShare版HTML已生成: {output_file}")
    print(f"✓ 化工品数量: {len(all_data)} 个")
    print(f"✓ 数据更新时间: {datetime.now(BEIJING_TZ).strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
    print(f"✓ 访问地址: http://192.168.77.12:8000/Chemical_Dashboard/chemical_dashboard_akshare.html")
    print("="*80)

if __name__ == "__main__":
    generate_akshare_html_fast()
