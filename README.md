# Telegram 频道信息转发工具 (TG_ZF)

## ✨ 主要功能

### 🔄 消息转发
- **多账号支持**：支持配置多个 Telegram 账号，自动轮换使用
- **智能账号切换**：自动跳过无法访问频道的账号
- **断点续传**：支持中断后继续转发，不会重复处理
- **批量处理**：支持同时处理多个源频道

### 🛡️ 智能过滤
- **广告过滤**：基于关键词和正则模式识别并过滤广告内容
- **内容质量过滤**：过滤无意义、重复字符、表情符号过多的消息
- **媒体要求过滤**：可设置无意义消息必须有媒体内容才保留
- **服务消息过滤**：自动跳过系统服务消息

### 🔍 内容去重
- **媒体去重**：基于媒体文件特征进行去重，避免重复转发相同内容
- **相册去重**：智能处理相册组，以整个相册为单位进行去重
- **目标频道扫描**：预先扫描目标频道，避免转发已存在的内容
- **增量扫描**：支持增量扫描，只处理新增内容

### 📊 统计与监控
- **实时进度**：显示转发进度和统计信息
- **详细日志**：记录转发、过滤、去重的详细信息
- **历史记录**：保存转发历史，支持查看和恢复
- **账号统计**：显示各账号的使用情况

## 🚀 快速开始

### 环境要求
- Python 3.7+
- Telegram API 凭据

### 安装依赖
```bash
pip install telethon
pip install PySocks
```

### 获取 API 凭据
1. 访问 [my.telegram.org](https://my.telegram.org)
2. 登录您的 Telegram 账号
3. 创建新应用获取 `api_id` 和 `api_hash`

### 配置代理
编辑 `TG_ZF.py` 文件中的代理配置：

```python
global_proxy = None  # 设置为 None 表示不使用代理
# 代理配置示例（取消注释并修改为您的代理信息）：
global_proxy = {
    "proxy_type": "socks5",  # 代理类型：socks5, socks4, http, mtproto
    "addr": "127.0.0.1",     # 代理服务器地址
    "port": 7890,            # 代理软件上设置的端口
    "username": "",          # 代理用户名（可选，留空表示无需认证）
    "password": ""           # 代理密码（可选，留空表示无需认证）
}
```

### 配置账号
编辑 `TG_ZF.py` 文件中的账号配置：

```python
accounts = [
    {
        "api_id": 你的API_ID,
        "api_hash": "你的API_HASH",
        "session_name": "forward_session_1",
        "enabled": True
    },
    # 可以添加更多账号
]
```

### 运行程序
```bash
# 正常转发模式
python TG_ZF.py
# 初次运行需要根据提示输入账号，+86后接空格
Please enter your phone (or bot token): +86 186xxxxxxxxxx
Please enter the code you received: 收到的验证码
# 初次运行会扫描目标频道的资源生成hash值用于去重，需要等待扫描完成
# 转发信息100条提示一次
📊 预计剩余待转发: 7367 条消息
📊 历史转发统计: 总计 487 条 (单条: 487, 相册: 0)
📈 进度: 100 条 | ✅ 转发:89 🚫 广告:2 🗑️ 内容:0 🔄 重复:1 📚 跳过相册:2 ❌ 错误:0
# 速度可以修改下面两个参数调整
delay_single = 2          # 单条消息延迟（秒）
delay_group = 4           # 相册延迟（秒）
# 仅导出账号频道信息
python TG_ZF.py export
# 违规信息清理
python TG_ZF.py clean
```

## ⚙️ 配置说明

### 账号配置
```python
# 账号轮换配置
enable_account_rotation = False  # 是否启用账号轮换
rotation_interval = 500          # 每转发多少条消息后轮换账号
account_delay = 5               # 账号切换延迟（秒）
enable_smart_account_switch = True  # 智能账号切换
```

### 频道配置
```python
# 信息转发：源频道----→目标频道
# 预设源频道（支持多种格式）- 留空表示使用手动选择
preset_source_channels = [
    -100xxxxxxxx,                      # 频道ID
    "@example_channel",                # 频道用户名
    "https://t.me/example_channel"     # 频道链接
]

# 预设目标频道，设为 None 表示使用手动选择
preset_target_channel = -100xxxxxxxx
```

### 过滤配置
```python
# 广告过滤
enable_ad_filter = True
ad_keywords = ["推广", "广告", "营销", "代理", "加盟", "招商"]
ad_patterns = [
    r'https?://[^\s]+',   # 链接
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱
]

# 内容质量过滤
enable_content_filter = True
meaningless_words = ["嗯", "哦", "啊", "哈哈", "呵呵"]
max_repeat_chars = 3         # 最大重复字符数
min_meaningful_length = 5    # 最小有意义内容长度
max_emoji_ratio = 0.5        # 最大表情符号比例
```

### 去重配置
```python
# 内容去重
enable_content_deduplication = True
dedup_history_file = "dedup_history.json"
target_channel_scan_limit = None  # 扫描范围，None表示全部
verbose_dedup_logging = False     # 详细去重日志
```

## 📁 文件说明

### 核心文件
- `TG_ZF.py` - 主程序文件
- `README.md` - 说明文档

### 数据文件
- `forward_history.json` - 转发历史记录（包含进度）
- `dedup_history.json` - 去重历史记录
- `channels_export.json` - 频道信息导出文件

### 会话文件
- `forward_session_*.session` - Telegram 会话文件
- `forward_session_*.session-journal` - 会话日志文件

## 🎯 使用场景

### 1. 频道内容聚合
将多个源频道的内容聚合到一个目标频道，实现内容统一管理。

### 2. 内容筛选转发
通过智能过滤功能，只转发高质量、有意义的内容，过滤广告和垃圾信息。

### 3. 多账号管理
使用多个账号进行转发，避免单账号限制，提高转发效率。

### 4. 内容去重
避免重复转发相同内容，保持目标频道的整洁。

## 🔧 高级功能

### 断点续传
程序支持中断后继续转发，所有进度都会保存到 `forward_history.json` 文件中。

### 智能账号切换
当检测到账号无法访问某个频道时，会自动切换到其他可用账号。

### 目标频道预扫描
在开始转发前，程序会扫描目标频道，建立去重数据库，避免转发重复内容。

### 批量进度显示
每处理一定数量的消息后显示批量统计，包括转发、过滤、去重的数量。

## 📊 统计信息

程序运行时会显示详细的统计信息：

```
📊 总体转发统计:
处理频道数: 3
总消息数: 1500
成功转发: 1200
广告过滤率: 15.2%
内容过滤率: 8.5%
重复过滤率: 5.3%
成功率: 80.0%
```

## ⚠️ 注意事项

1. **API 限制**：请遵守 Telegram API 的使用限制，避免频繁请求
2. **账号安全**：妥善保管 API 凭据和会话文件
3. **内容合规**：确保转发的内容符合相关法律法规
4. **网络稳定**：建议在稳定的网络环境下运行
5. **权限管理**：确保账号有访问源频道和写入目标频道的权限

## 🐛 常见问题

### Q: 程序提示"没有可用的账号"
A: 检查账号配置是否正确，确保 `api_id` 和 `api_hash` 有效。

### Q: 无法访问某个频道
A: 检查账号是否有该频道的访问权限，或尝试使用其他账号。

### Q: 转发速度很慢
A: 可以调整 `delay_single` 和 `delay_group` 参数，但要注意不要设置过小。

### Q: 重复转发相同内容
A: 确保启用了内容去重功能，并预先扫描目标频道。

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

---

**免责声明**：本工具仅供学习和研究使用，使用者需要遵守相关法律法规和 Telegram 的使用条款。作者不承担因使用本工具而产生的任何法律责任。
