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
from datetime import datetime, timedelta
import pandas as pd

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
            'price': round(float(current_price), 2),
            'change_daily': change_daily,
            'change_1w': change_1w,
            'change_1m': change_1m,
            'change_3m': change_3m,
            'change_6m': change_6m,
            'change_1y': change_1y,
            'chart_data': chart_data,
            'full_data': full_data,
            'update_time': latest_date
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
        f'const updateTime = "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}";'
    )

    # 保存静态HTML
    output_file = 'index.html'  # GitHub Actions部署时使用
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("\n" + "="*80)
    print(f"✓ AkShare版HTML已生成: {output_file}")
    print(f"✓ 化工品数量: {len(all_data)} 个")
    print(f"✓ 数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✓ 访问地址: http://192.168.77.12:8000/Chemical_Dashboard/chemical_dashboard_akshare.html")
    print("="*80)

if __name__ == "__main__":
    generate_akshare_html_fast()
