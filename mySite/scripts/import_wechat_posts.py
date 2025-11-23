#!/usr/bin/env python3
"""
批量导入微信公众号文章到博客数据库

支持两种格式：
1. CSV文件 (推荐) - posts.csv
2. JSON文件 - posts.json

CSV格式示例：
title,content,created_at
"文章标题1","文章内容...",2024-01-15
"文章标题2","文章内容...",2024-01-20

JSON格式示例：
[
    {
        "title": "文章标题1",
        "content": "文章内容...",
        "created_at": "2024-01-15"
    }
]
"""

import os
import sys
import csv
import json
from datetime import datetime
from app import app, db, Post

def import_from_csv(csv_file):
    """从CSV文件导入文章"""
    imported = 0
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 解析日期
            if 'created_at' in row and row['created_at']:
                try:
                    created_at = datetime.strptime(row['created_at'], '%Y-%m-%d')
                except:
                    created_at = datetime.utcnow()
            else:
                created_at = datetime.utcnow()
            
            # 创建文章
            post = Post(
                title=row['title'],
                content=row['content'],
                created_at=created_at
            )
            db.session.add(post)
            imported += 1
            print(f"✓ 导入: {post.title}")
    
    db.session.commit()
    return imported

def import_from_json(json_file):
    """从JSON文件导入文章"""
    imported = 0
    with open(json_file, 'r', encoding='utf-8') as f:
        posts_data = json.load(f)
    
    for item in posts_data:
        # 解析日期
        if 'created_at' in item and item['created_at']:
            try:
                created_at = datetime.strptime(item['created_at'], '%Y-%m-%d')
            except:
                created_at = datetime.utcnow()
        else:
            created_at = datetime.utcnow()
        
        # 创建文章
        post = Post(
            title=item['title'],
            content=item['content'],
            created_at=created_at
        )
        db.session.add(post)
        imported += 1
        print(f"✓ 导入: {post.title}")
    
    db.session.commit()
    return imported

def clear_all_posts():
    """清空所有现有文章 - 谨慎使用！"""
    confirm = input("⚠️  确定要删除所有现有文章吗？(输入 'YES' 确认): ")
    if confirm == 'YES':
        count = Post.query.count()
        Post.query.delete()
        db.session.commit()
        print(f"✓ 已删除 {count} 篇文章")
        return True
    else:
        print("取消删除")
        return False

def main():
    print("=" * 50)
    print("微信公众号文章导入工具")
    print("=" * 50)
    
    # 检查文件
    csv_exists = os.path.exists('posts.csv')
    json_exists = os.path.exists('posts.json')
    
    if not csv_exists and not json_exists:
        print("\n❌ 错误: 找不到 posts.csv 或 posts.json 文件")
        print("\n请创建以下格式的文件：")
        print("\n1. CSV格式 (posts.csv):")
        print("title,content,created_at")
        print('"文章标题","文章内容...","2024-01-15"')
        print("\n2. JSON格式 (posts.json):")
        print('[{"title": "文章标题", "content": "文章内容...", "created_at": "2024-01-15"}]')
        return
    
    # 询问是否清空现有文章
    print("\n选项:")
    print("1. 清空现有文章后导入 (替换)")
    print("2. 追加到现有文章 (不删除)")
    choice = input("\n请选择 (1/2): ").strip()
    
    with app.app_context():
        if choice == '1':
            if not clear_all_posts():
                return
        
        # 导入
        imported = 0
        if csv_exists:
            print(f"\n开始从 posts.csv 导入...")
            imported = import_from_csv('posts.csv')
        elif json_exists:
            print(f"\n开始从 posts.json 导入...")
            imported = import_from_json('posts.json')
        
        print(f"\n✓ 成功导入 {imported} 篇文章！")

if __name__ == '__main__':
    main()
