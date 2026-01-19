# Telegram 消息转发与频道群组导出备份工具 (TG_ZF)

一个功能强大的 Telegram 工具，支持**频道消息转发**（多账号轮换、智能过滤、内容去重）和**对话信息导出**（频道、群组、机器人、私聊等）。

## ✨ 主要功能

### 📤 对话信息导出
- **多类型导出**：支持导出频道、群组、机器人、私聊等所有对话类型
- **多账号导出**：自动遍历所有配置的账号并导出各自的对话
- **完整信息**：导出对话ID、名称、链接等详细信息
- **JSON格式**：输出为结构化的JSON文件，便于后续处理

### 🔄 消息转发
- **多账号支持**：配置多个 Telegram 账号，自动轮换使用
- **智能账号切换**：自动跳过无法访问频道的账号
- **断点续传**：中断后继续转发，不会重复处理
- **批量处理**：同时处理多个源频道

### 🛡️ 智能过滤
- **广告过滤**：基于关键词和正则模式识别并过滤广告
- **内容质量过滤**：过滤无意义、重复字符、表情符号过多的消息
- **白名单过滤**：只转发包含指定关键词的消息，精确控制转发内容
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
- Telegram API 凭据（[如何获取](#3-获取-api-凭据)）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install telethon>=1.28.0 pyyaml>=6.0 PySocks>=1.7.1
```

### 3. 获取 API 凭据
1. 访问 [my.telegram.org](https://my.telegram.org)
2. 登录您的 Telegram 账号
3. 点击 "API development tools"
4. 创建新应用获取 `api_id` 和 `api_hash`

### 4. 配置文件

复制示例配置文件并修改：

```bash
cp config.yaml.example config.yaml
```

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
  # 账号 1（必填）
  - api_id: 你的API_ID            # 替换为你的 API ID
    api_hash: "你的API_Hash"       # 替换为你的 API Hash
    session_name: forward_session_1
    enabled: true
  
  # 账号 2（可选，用于轮换）
  # - api_id: 第二个API_ID
  #   api_hash: "第二个API_Hash"
  #   session_name: forward_session_2
  #   enabled: true

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

# 导出对话信息（频道、群组、机器人、私聊等）
python TG_ZF.py export

# 清理违规消息
python TG_ZF.py clean

# 导出后的对话信息保存在 dialogs_export.json 中
```

### 6. 运行效果

```
🔍 扫描目标频道...
📊 预计剩余待转发: 7367 条消息
📊 历史转发统计: 总计 487 条 (单条: 487, 相册: 0)
📈 进度: 100 条 | ✅ 转发:89 🚫 广告:2 🗑️ 内容:0 🔄 重复:1 🎯 白名单:5 📚 相册:8 ❌ 错误:0
```

---

## 📁 项目结构

```
TG_ZF/
├── TG_ZF.py                  # 主程序
├── config.yaml.example       # 配置文件模板
├── config.yaml               # 配置文件（需自行删除config.yaml.example后缀）
├── requirements.txt          # Python 依赖
├── README.md                 # 说明文档
├── .gitignore                # Git 忽略文件
│
├── forward_history.json      # [自动生成] 转发历史记录（包含进度）
├── dedup_history.json        # [自动生成] 去重历史记录
├── dialogs_export.json       # [自动生成] 对话信息导出（含频道/群组/机器人/私聊）
├── channels_export.json      # [自动生成] 频道信息导出（仅频道）
└── forward_session_*.session # [自动生成] Telegram 会话文件
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

### 白名单过滤配置
```yaml
whitelist_filter:
  enable_whitelist_filter: false   # 是否启用白名单过滤
  whitelist_keywords: [           # 白名单关键词列表，消息必须包含其中至少一个关键词才会被转发
    "aaaa",                       # 示例关键词
    "重要",                       # 可以添加多个关键词
    "新闻"
  ]
  case_sensitive: false           # 是否区分大小写
  match_media_messages: true       # 是否对纯媒体消息也应用白名单过滤
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

### 清理配置
```yaml
clean:
  auto_clean_violations: false     # 设置为 true 时，自动清理违规消息
  scan_limit: null                 # 清理扫描范围（条消息），null 表示全部
  batch_size: 100                  # 每次扫描的消息数量
  delay: 1                         # 删除消息的延迟（秒）
```

### 对话导出配置
```yaml
export:
  auto_export_channels: false     # 设置为 true 时，程序启动时自动导出对话信息
```

#### 导出文件格式说明

运行 `python TG_ZF.py export` 后，会生成 `dialogs_export.json` 文件，格式如下：

```json
{
  "账号名称": {
    "序号/总数 [类型] 对话名称": "对话ID-对话链接"
  }
}
```

**对话类型：**
- `[频道]` - Telegram 频道
- `[群组]` - Telegram 群组
- `[机器人]` - Bot 机器人
- `[私聊]` - 私人聊天
- `[其他]` - 其他类型

**示例：**
```json
{
  "forward_session_1": {
    "1/80 [频道] C***组": "-1002143008111-https://t.me/example_channel",
    "2/80 [群组] 中***索": "-1001739922930-https://t.me/example_group",
    "3/80 [机器人] B***r": "93372553-https://t.me/BotFather",
    "4/80 [私聊] 用户名": "123456789-对话ID: 123456789"
  }
}
```

---

## 🎯 使用场景

### 1. 频道内容聚合
将多个源频道的内容聚合到一个目标频道，实现内容统一管理。

### 2. 内容筛选转发
通过智能过滤，只转发高质量、有意义的内容，过滤广告和垃圾信息。支持白名单过滤，精确控制转发内容。

### 3. 多账号管理
使用多个账号进行转发，避免单账号限制，提高转发效率。

### 4. 内容去重
避免重复转发相同内容，保持目标频道整洁。

### 5. 对话信息备份
使用导出功能快速备份所有账号的对话列表，包含频道、群组、机器人、私聊等完整信息，便于管理和查阅。

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
📈 进度: 100 条 | ✅ 转发:89 🚫 广告:2 🗑️ 内容:0 🔄 重复:1 🎯 白名单:5
```

### 清理违规消息
使用 `python TG_ZF.py clean` 命令可以：
- 扫描目标频道的历史消息
- 根据当前过滤规则识别违规内容
- 自动删除不符合规则的消息

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
白名单过滤率: 12.0%
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
cp config.yaml.example config.yaml
# 然后编辑 config.yaml 填入你的账号信息
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

### Q: 如何使用白名单过滤
**A**: 在 `config.yaml` 中配置白名单过滤：
```yaml
whitelist_filter:
  enable_whitelist_filter: true   # 启用白名单过滤
  whitelist_keywords: [           # 只转发包含这些关键词的消息
    "重要",
    "新闻",
    "技术"
  ]
  case_sensitive: false           # 不区分大小写
  match_media_messages: true       # 对纯媒体消息也应用过滤
```

### Q: 白名单过滤和广告过滤的区别
**A**: 
- **广告过滤**：过滤掉包含广告关键词的消息（黑名单模式）
- **白名单过滤**：只转发包含指定关键词的消息（白名单模式）
- 两种过滤可以同时使用，消息需要同时通过两种过滤才会被转发

### Q: 如何清理目标频道的违规消息
**A**: 运行清理命令：
```bash
python TG_ZF.py clean
```
程序会根据当前配置的过滤规则，扫描并删除目标频道中不符合规则的历史消息。

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
