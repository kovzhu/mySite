# Scripts 文件夹

这个文件夹包含各种工具和辅助脚本。

## 数据库管理工具

- **`init_db.py`** - 初始化数据库（首次设置时使用）
- **`create_admin.py`** - 创建管理员账户
- **`update_admin_credentials.py`** - 更新管理员凭证
- **`create_sample_data.py`** - 创建示例数据（测试用）
- **`test_db.py`** - 测试数据库连接

## 内容导入工具

- **`import_wechat_posts.py`** - 批量导入微信公众号文章
- **`posts_example.csv`** - CSV格式示例文件

## 使用方法

所有脚本都需要在 `mySite` 目录下运行：

```bash
cd /path/to/mySite
python scripts/脚本名.py
```

例如：
```bash
python scripts/create_admin.py
python scripts/import_wechat_posts.py
```
