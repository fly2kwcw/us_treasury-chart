#!/usr/bin/env python3
"""
自动更新美债收益率数据脚本
用法: python update_data.py
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime, timedelta
import subprocess

def update_data():
    print(f"[{datetime.now()}] 开始更新数据...")
    
    # 获取美债收益率数据
    df = ak.bond_zh_us_rate()
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 获取过去60天数据
    end_date = df['日期'].max()
    start_date = end_date - timedelta(days=70)
    df_filtered = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)].copy()
    df_filtered = df_filtered.sort_values('日期').tail(60)
    
    # 构建数据
    result = {
        '10y': {
            'dates': df_filtered['日期'].dt.strftime('%Y-%m-%d').tolist(),
            'yields': [round(x, 2) if pd.notna(x) else None for x in df_filtered['美国国债收益率10年'].tolist()]
        },
        '30y': {
            'dates': df_filtered['日期'].dt.strftime('%Y-%m-%d').tolist(),
            'yields': [round(x, 2) if pd.notna(x) else None for x in df_filtered['美国国债收益率30年'].tolist()]
        },
        'updated_at': datetime.now().isoformat()
    }
    
    # 保存到文件
    with open('data.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"数据已更新: {end_date.strftime('%Y-%m-%d')}")
    print(f"10年期最新: {result['10y']['yields'][-1]}%")
    print(f"30年期最新: {result['30y']['yields'][-1]}%")
    
    return True

def git_push():
    """推送到 GitHub"""
    try:
        subprocess.run(['git', 'add', 'data.json'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Update data: {datetime.now().strftime("%Y-%m-%d")}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("已推送到 GitHub")
    except subprocess.CalledProcessError as e:
        print(f"Git 操作失败: {e}")

if __name__ == '__main__':
    if update_data():
        # 如果有 git 仓库，自动推送
        try:
            git_push()
        except:
            print("Git 推送跳过（可能没有配置）")
