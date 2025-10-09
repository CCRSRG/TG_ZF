# Telegram 频道信息转发工具 (TG_ZF)

一个功能强大的 Telegram 频道内容转发工具，支持多账号轮换、智能过滤、内容去重等高级功能。

## ✨ 主要功能

### 🔄 消息转发
- **多账号支持**：配置多个 Telegram 账号，自动轮换使用
- **智能账号切换**：自动跳过无法访问频道的账号
- **断点续传**：中断后继续转发，不会重复处理
- **批量处理**：同时处理多个源频道

### 🛡️ 智能过滤
- **广告过滤**：基于关键词和正则模式识别并过滤广告
- **内容质量过滤**：过滤无意义、重复字符、表情符号过多的消息
- **媒体要求过滤**：可设置无意义消息必须有媒体内容
- **服务消息过滤**：自动跳过系统服务消息

### 🔍 内容去重
- **媒体去重**：基于媒体文件特征去重，避免重复转发
- **相册去重**：智能处理相册组，以整个相册为单位去重
- **目标频道扫描**：预先扫描目标频道，避免转发已存在的内容
- **增量扫描**：只处理新增内容

### 📊 统计与监控
- **实时进度**：显示转发进度和统计信息
- **详细日志**：记录转发、过滤、去重的详细信息
- **历史记录**：保存转发历史，支持查看和恢复

---

## 🚀 快速开始

### 1. 环境要求
- Python 3.7+
- Telegram API 凭据（[如何获取](#获取-api-凭据)）

### 2. 安装依赖
```bash
pip install telethon pyyaml PySocks
```

### 3. 获取 API 凭据
1. 访问 [my.telegram.org](https://my.telegram.org)
2. 登录您的 Telegram 账号
3. 点击 "API development tools"
4. 创建新应用获取 `api_id` 和 `api_hash`

### 4. 配置文件

编辑 `config.yaml` 文件：

```yaml
# ============ 代理配置 ============
proxy:
  enabled: true                    # 是否启用代理
  proxy_type: http                 # 代理类型: http, socks5, socks4
  addr: 127.0.0.1
  port: 7890

# ============ 账号配置 ============
accounts:
  - api_id: 你的API_ID            # 替换为你的 API ID
    api_hash: "你的API_Hash"       # 替换为你的 API Hash   可使用默认配置
    session_name: forward_session_1
    enabled: true

# ============ 频道配置 ============
channels:
  # 源频道列表（留空表示手动选择）
  preset_source_channels: [
    -1001234567890,                # 频道 ID
    "@example_channel",            # 频道用户名
    "https://t.me/channel"         # 频道链接
  ]
  # 目标频道（null 表示手动选择）
  preset_target_channel: -1001234567890
```

> **📝 注意**：YAML 格式支持注释，可以用 `#` 添加说明。详细配置说明见文末。

### 5. 运行程序

```bash
# 正常转发模式
python TG_ZF.py

# 首次运行需要验证
# Please enter your phone (or bot token): +86 186xxxxxxxx
# Please enter the code you received: 12345

# 仅导出频道信息
python TG_ZF.py export

# 清理违规消息
python TG_ZF.py clean
```

### 6. 运行效果

```
🔍 扫描目标频道...
📊 预计剩余待转发: 7367 条消息
📊 历史转发统计: 总计 487 条 (单条: 487, 相册: 0)
📈 进度: 100 条 | ✅ 转发:89 🚫 广告:2 🗑️ 内容:0 🔄 重复:1 📚 相册:8 ❌ 错误:0
```

---

## ⚙️ 配置说明

### 账号轮换配置
```yaml
account_rotation:
  enable_account_rotation: true    # 是否启用账号轮换
  rotation_interval: 500           # 每转发多少条消息后轮换账号
  account_delay: 5                 # 账号切换延迟（秒）
  enable_smart_account_switch: true # 智能账号切换
```

### 转发速度配置
```yaml
forward:
  delay_single: 2                  # 单条消息延迟（秒）
  delay_group: 2                   # 相册延迟（秒）
  max_messages: null               # 最大转发数量（null=全部）
```

### 广告过滤配置
```yaml
ad_filter:
  enable_ad_filter: true
  ad_keywords: [推广, 广告, 营销, 代理, 加盟, 招商, 投资]
  ad_patterns:
    - 'https?://[^\s]+'            # 过滤链接
    - '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # 过滤邮箱
  min_message_length: 10           # 最小消息长度
  max_links_per_message: 3         # 每条消息最大链接数
```

### 内容质量过滤
```yaml
content_filter:
  enable_content_filter: true
  enable_media_required_filter: true  # 无意义消息必须有媒体
  meaningless_words: [嗯, 哦, 啊, 哈哈, 顶, 赞, 👍, 沙发, 路过]
  max_repeat_chars: 3              # 最大重复字符数（如"哈哈哈"）
  min_meaningful_length: 5         # 最小有意义内容长度
  max_emoji_ratio: 0.5             # 最大表情符号比例
```

### 内容去重配置
```yaml
deduplication:
  enable_content_deduplication: true
  dedup_history_file: dedup_history.json
  target_channel_scan_limit: null  # 扫描范围（null=全部）
  verbose_dedup_logging: false     # 是否显示详细去重日志
```

### 关联频道支持
```yaml
linked_channel:
  enable_linked_channel_support: true     # 启用关联频道支持
  force_forward_linked_channels: true     # 强制转发关联频道内容
```

---

## 📁 文件说明

### 核心文件
- `TG_ZF.py` - 主程序
- `config.yaml` - 配置文件（支持注释）
- `README.md` - 说明文档

### 数据文件（自动生成）
- `forward_history.json` - 转发历史记录（包含进度）
- `dedup_history.json` - 去重历史记录
- `channels_export.json` - 频道信息导出文件

### 会话文件（自动生成）
- `forward_session_*.session` - Telegram 会话文件
- `forward_session_*.session-journal` - 会话日志

---

## 🎯 使用场景

### 1. 频道内容聚合
将多个源频道的内容聚合到一个目标频道，实现内容统一管理。

### 2. 内容筛选转发
通过智能过滤，只转发高质量、有意义的内容，过滤广告和垃圾信息。

### 3. 多账号管理
使用多个账号进行转发，避免单账号限制，提高转发效率。

### 4. 内容去重
避免重复转发相同内容，保持目标频道整洁。

---

## 🔧 高级功能

### 断点续传
程序支持中断后继续转发，所有进度保存在 `forward_history.json` 中。

### 智能账号切换
检测到账号无法访问频道时，自动切换到其他可用账号。

### 目标频道预扫描
在开始转发前扫描目标频道，建立去重数据库，避免重复内容。

### 批量进度显示
每处理一定数量消息后显示统计信息：
```
📈 进度: 100 条 | ✅ 转发:89 🚫 广告:2 🗑️ 内容:0 🔄 重复:1
```

---

## 📊 统计信息示例

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

---

## ⚠️ 注意事项

1. **API 限制**：遵守 Telegram API 使用限制，避免频繁请求
2. **账号安全**：妥善保管 API 凭据和会话文件
3. **内容合规**：确保转发内容符合相关法律法规
4. **网络稳定**：建议在稳定的网络环境下运行
5. **权限管理**：确保账号有访问源频道和写入目标频道的权限

---

## 🐛 常见问题

### Q: 程序提示"配置文件不存在"
**A**: 需要先创建配置文件：
```bash
# 如果有 config.yaml，直接使用
# 如果没有，创建一个新的配置文件并填入你的账号信息
```

### Q: 程序提示"没有可用的账号"
**A**: 检查 `config.yaml` 中的账号配置：
- 确保 `api_id` 和 `api_hash` 正确
- 确保 `enabled: true`
- 首次运行需要验证手机号

### Q: 无法访问某个频道
**A**: 
- 检查账号是否已加入该频道
- 启用智能账号切换，自动使用其他账号
- 检查频道 ID 是否正确

### Q: 转发速度太慢
**A**: 修改配置文件中的延迟参数：
```yaml
forward:
  delay_single: 1  # 降低延迟（不建议低于 1 秒）
  delay_group: 1
```

### Q: 重复转发相同内容
**A**: 
- 确保启用了内容去重：`enable_content_deduplication: true`
- 首次运行会扫描目标频道建立去重数据库
- 删除 `dedup_history.json` 可重新扫描

### Q: 如何添加更多过滤关键词
**A**: 编辑 `config.yaml`：
```yaml
ad_filter:
  ad_keywords: [推广, 广告, 你的关键词1, 你的关键词2]
```

---

## 💡 配置文件格式

本工具支持 **YAML** 和 **JSON** 两种配置格式：

### YAML 格式（推荐）✅
- ✅ 支持注释（用 `#`）
- ✅ 格式更清晰易读
- ✅ 容错性好
- ✅ 列表可以横排或竖排

### JSON 格式（兼容）
- ❌ 不支持注释
- ⚠️ 格式严格（需要注意逗号、引号）

**文件优先级**：`config.yaml` > `config.yml` > `config.json`

---

## 📄 许可证

本项目仅供学习和研究使用。

**免责声明**：使用本工具需遵守相关法律法规和 Telegram 使用条款。作者不承担因使用本工具产生的任何法律责任。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**⭐ 如果这个项目对您有帮助，请给一个 Star！**
