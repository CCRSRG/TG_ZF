import asyncio
import json
import os
import re
import hashlib
from telethon import TelegramClient, errors

# ============ 配置 ============
# 全局代理配置（可选）
# 设置为 None 表示不使用代理
# 所有账号都会使用此代理配置
global_proxy = None  # 设置为 None 表示不使用代理

# 代理配置示例（取消注释并修改为您的代理信息）：
# global_proxy = {
#     "proxy_type": "socks5",  # 代理类型：socks5, socks4, http, mtproto
#     "addr": "127.0.0.1",     # 代理服务器地址
#     "port": 1080,            # 代理端口
#     "username": "",          # 代理用户名（可选，留空表示无需认证）
#     "password": ""           # 代理密码（可选，留空表示无需认证）
# }

# 多账号配置
accounts = [
    {
        "api_id": 21722171,
        "api_hash": "6dc06adcb5961d617c347d7776d2ec76",
        "session_name": "forward_session_1",
        "enabled": True
    },
    # 添加更多账号配置
    # {
    #     "api_id": 2XXXX,
    #     "api_hash": "7XXXX",
    #     "session_name": "forward_session_2",
    #     "enabled": True
    # },
    # {
    #     "api_id": 你的第三个账号ID,
    #     "api_hash": "你的第三个账号Hash", 
    #     "session_name": "forward_session_3",
    #     "enabled": True
    # }
]

# ============ 频道配置 ============
# - 留空或设为 None 表示使用手动选择
# 资源频道：# -100XXXXXXXX, 频道ID  # "@example_channel",频道用户名  # "https://t.me/example_channel",频道链接
preset_source_channels = []
#转发信息目标频道
preset_target_channel = -100XXXXXXXX

# 自动导出配置，仅使用导出功能：python TG_ZF.py export
auto_export_channels = False  # 设置为 True 时，程序启动时自动导出频道信息

# 账号轮换配置
enable_account_rotation = True  # 是否启用账号轮换
rotation_interval = 500  # 每转发多少条消息后轮换账号
account_delay = 5  # 账号切换延迟（秒）
enable_smart_account_switch = True  # 是否启用智能账号切换（自动跳过无法访问频道的账号）

max_messages = None  # None 表示全部消息
delay_single = 2  # 单条消息延迟（秒）
delay_group = 4  # 相册延迟（秒）
forward_history_file = "forward_history.json"  # 转发历史记录文件（包含进度）
batch_progress_interval = 100  # 批量进度显示间隔（条消息）

# ============ 广告过滤配置 ============
enable_ad_filter = True  # 是否启用广告过滤
ad_keywords = [  # 广告关键词
    "推广", "广告", "营销", "代理", "加盟", "招商", "投资", "理财",
    "店铺", "注册", "官方", "佣金", "汇旺", "官网注册", "返水",
    "入款", "出款", "返水", "彩金", "资金保障", "提款"
]

ad_patterns = [  # 广告正则模式
    r'https?://[^\s]+',  # 链接
    # r'@\w+',             # @用户名
    # r'#\w+',             # #话题标签
    r'\d{4,}',  # 长数字（可能是QQ号、微信号等）
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # 邮箱
    r'1[3-9]\d{9}',  # 手机号
    # r'[A-Za-z0-9]{6,}',  # 长字母数字组合（可能是邀请码等）
]

min_message_length = 10  # 最小消息长度（过短可能是广告）
max_links_per_message = 3  # 每条消息最大链接数

# ============ 内容质量过滤配置 ============
enable_content_filter = True  # 是否启用内容质量过滤
enable_media_required_filter = True  # 是否要求无意义消息必须有媒体内容

meaningless_words = [  # 无意义词汇
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "Cy",
    "嗯", "哦", "啊", "额", "呃", "哈", "呵", "嘿", "嗨", "cy",
    "好的", "ok", "okay", "yes", "no", "是", "不是", "对", "不对",
    "哈哈", "呵呵", "嘿嘿", "嘻嘻", "嘿嘿嘿", "哈哈哈", "插眼",
    "顶", "赞", "👍", "👌", "😊", "😄", "😂", "😅",
    "沙发", "板凳", "地板", "地下室", "前排", "后排",
    "路过", "看看", "瞧瞧", "围观", "吃瓜", "打卡",
    "签到", "报到", "冒泡", "潜水", "灌水", "水贴"
]

max_repeat_chars = 3  # 最大重复字符数（如"哈哈哈"超过3个字符）
min_meaningful_length = 5  # 最小有意义内容长度
max_emoji_ratio = 0.5  # 最大表情符号比例

# ============ 内容去重配置 ============
enable_content_deduplication = True  # 是否启用内容去重
dedup_history_file = "dedup_history.json"  # 去重历史记录文件
target_channel_scan_limit = None  # 目标频道扫描范围（条消息），None表示扫描所有
verbose_dedup_logging = False  # 是否显示详细的去重日志（True=显示每个重复相册，False=只在批量统计时显示）
# 去重策略：相册以整个相册组作为hash值判断，单条消息基于媒体文件进行判断
# ==========================================

# ============ 常量定义 ============
PROTECTED_CHAT_REASON = "受保护的聊天"
# ==========================================

# 初始化客户端列表
clients = []
for account in accounts:
    if account["enabled"]:
        # 使用全局代理配置
        proxy = global_proxy
        client = TelegramClient(account["session_name"], account["api_id"], account["api_hash"], proxy=proxy)
        clients.append({
            "client": client,
            "account": account,
            "forward_count": 0,
            "last_used": 0,
            "enabled": True
        })

# 当前使用的客户端索引
current_client_index = 0

# 账号频道访问权限缓存
account_channel_access = {}


# ---------- 公共工具函数 ----------
def get_channel_key(src_id, dst_id):
    """生成标准化的频道键"""
    normalized_src_id = normalize_channel_id(src_id)
    normalized_dst_id = normalize_channel_id(dst_id)
    return f"{normalized_src_id}_to_{normalized_dst_id}"


def init_forward_history_entry(history, channel_key):
    """初始化转发历史记录条目"""
    if channel_key not in history:
        history[channel_key] = {
            "forwarded_messages": [],
            "filtered_messages": [],
            "duplicate_messages": [],
            "total_count": 0,
            "filtered_count": 0,
            "duplicate_count": 0,
            "last_message_id": 0,
            "last_update": ""
        }


def handle_forward_error(e, msg_id, account_name, msg_type="消息"):
    """统一的转发错误处理"""
    error_msg = str(e)
    if "protected chat" in error_msg.lower() or "can't forward messages from a protected chat" in error_msg.lower():
        print(f"🚫 无法转发{msg_type} {msg_id} ({account_name}): 受保护的聊天")
        return False, "protected_chat"
    elif "chat not found" in error_msg.lower():
        print(f"🚫 无法转发{msg_type} {msg_id} ({account_name}): 聊天不存在")
        return False, "chat_not_found"
    elif "access denied" in error_msg.lower():
        print(f"🚫 无法转发{msg_type} {msg_id} ({account_name}): 访问被拒绝")
        return False, "access_denied"
    elif "chat write forbidden" in error_msg.lower():
        print(f"🚫 无法转发{msg_type} {msg_id} ({account_name}): 目标频道禁止写入")
        return False, "chat_write_forbidden"
    else:
        print(f"❌ 跳过{msg_type} {msg_id} 错误 ({account_name}): {e}")
        return False, "unknown_error"


def should_filter_with_media_check(has_media, default_filter=True):
    """统一的媒体过滤逻辑判断"""
    if enable_media_required_filter and not has_media:
        return True  # 没有媒体且要求媒体，则过滤
    elif enable_media_required_filter and has_media:
        return False  # 有媒体且要求媒体，则不过滤
    else:
        return default_filter  # 其他情况使用默认逻辑


def get_char_counts(text):
    """获取字符计数统计"""
    char_counts = {}
    for char in text:
        char_counts[char] = char_counts.get(char, 0) + 1
    return char_counts


def get_emoji_count(text):
    """计算表情符号数量"""
    return len([c for c in text if ord(c) > 127 and c not in '，。！？；：""''（）【】《》'])


def get_meaningful_chars_count(text):
    """计算有意义字符数量"""
    return len([c for c in text if c.isalnum() or c in '，。！？；：""''（）【】《》'])


def create_result(src_dialog, status, reason="", total_messages=0, forwarded_count=0,
                  ad_filtered_count=0, content_filtered_count=0, duplicate_filtered_count=0,
                  duplicate_albums_skipped=0, error_count=0):
    """创建统一的结果格式"""
    return {
        "source_name": get_channel_name(src_dialog),
        "source_id": src_dialog.id,
        "status": status,
        "reason": reason,
        "total_messages": total_messages,
        "forwarded_count": forwarded_count,
        "ad_filtered_count": ad_filtered_count,
        "content_filtered_count": content_filtered_count,
        "duplicate_filtered_count": duplicate_filtered_count,
        "duplicate_albums_skipped": duplicate_albums_skipped,
        "error_count": error_count
    }


def create_skipped_result(src_dialog, reason, total_messages=0, forwarded_count=0,
                          ad_filtered_count=0, content_filtered_count=0,
                          duplicate_filtered_count=0, error_count=0):
    """创建跳过结果的标准格式"""
    return create_result(src_dialog, "skipped", reason, total_messages, forwarded_count,
                         ad_filtered_count, content_filtered_count, duplicate_filtered_count,
                         0, error_count)


def create_completed_result(src_dialog, total_messages, forwarded_count,
                            ad_filtered_count, content_filtered_count,
                            duplicate_filtered_count, duplicate_albums_skipped, error_count):
    """创建完成结果的标准格式"""
    return create_result(src_dialog, "completed", "", total_messages, forwarded_count,
                         ad_filtered_count, content_filtered_count, duplicate_filtered_count,
                         duplicate_albums_skipped, error_count)


def generate_media_hash_content(msg):
    """为消息生成媒体哈希内容"""
    hash_content = ""

    if msg.media:
        if hasattr(msg.media, 'photo'):
            hash_content += f"photo:{msg.media.photo.id}:{msg.media.photo.date}"
        elif hasattr(msg.media, 'document'):
            hash_content += f"doc:{msg.media.document.id}:{msg.media.document.size}"
        elif hasattr(msg.media, 'video'):
            hash_content += f"video:{msg.media.video.id}:{msg.media.video.size}"
        elif hasattr(msg.media, 'audio'):
            hash_content += f"audio:{msg.media.audio.id}:{msg.media.audio.size}"
        elif hasattr(msg.media, 'sticker'):
            hash_content += f"sticker:{msg.media.sticker.id}"
        elif hasattr(msg.media, 'gif'):
            hash_content += f"gif:{msg.media.document.id}:{msg.media.document.size}"
        else:
            hash_content += f"media:{type(msg.media).__name__}"
    else:
        if msg.message:
            normalized_text = re.sub(r'\s+', ' ', msg.message.strip().lower())
            hash_content += f"text:{normalized_text}"
        else:
            hash_content += f"empty:{msg.id}"

    return hash_content


async def process_album_group(group_buffer, src_dialog, dst_dialog):
    """处理相册组的统一函数"""
    if not group_buffer:
        return 0, 0, 0

    # 智能相册处理：过滤重复图片
    unique_messages = filter_duplicate_messages_from_album(group_buffer)

    if not unique_messages:
        if verbose_dedup_logging:
            pass  # 相册中所有图片都是重复的
        return 0, 0, 1  # 返回跳过计数

    # 只转发不重复的图片
    success, error_type = await forward_group_safe(dst_dialog, unique_messages)

    if success:
        # 记录转发历史
        for msg_item in unique_messages:
            add_forward_record(src_dialog.id, dst_dialog.id, msg_item.id, "group")
        return len(unique_messages), 0, 0
    else:
        return 0, len(unique_messages), 0


# ---------- 账号管理函数 ----------
def get_current_client():
    """获取当前使用的客户端"""
    if not clients:
        raise Exception("没有可用的账号！请检查账号配置。")
    return clients[current_client_index]["client"]


def get_current_account_info():
    """获取当前账号信息"""
    if not clients:
        return None
    return clients[current_client_index]["account"]


def switch_to_next_account():
    """切换到下一个账号"""
    global current_client_index
    if not enable_account_rotation or len(clients) <= 1:
        return False

    old_index = current_client_index
    current_client_index = (current_client_index + 1) % len(clients)

    old_account = clients[old_index]["account"]["session_name"]
    new_account = clients[current_client_index]["account"]["session_name"]

    print(f"🔄 切换账号: {old_account} → {new_account}")
    return True


async def switch_to_accessible_account(src_dialog, dst_dialog):
    """切换到可访问指定频道的账号"""
    global current_client_index
    if not enable_account_rotation or len(clients) <= 1:
        return False

    # 如果未启用智能账号切换，使用原来的简单切换
    if not enable_smart_account_switch:
        return switch_to_next_account()

    current_account = get_current_account_info()["session_name"]
    original_index = current_client_index

    # 尝试所有账号，找到可访问的账号
    for i in range(len(clients)):
        test_index = (current_client_index + 1) % len(clients)
        test_account = clients[test_index]["account"]["session_name"]

        # 检查这个账号是否可访问源频道
        is_accessible, reason = await check_channel_accessibility(src_dialog, dst_dialog, test_account)
        if is_accessible:
            current_client_index = test_index
            print(f"🔄 切换到可访问账号: {current_account} → {test_account}")
            return True
        else:
            print(f"⚠️ 账号 {test_account} 无法访问频道: {reason}")
            # 继续尝试下一个账号
            current_client_index = test_index

    # 如果所有账号都无法访问，回到原账号
    current_client_index = original_index
    print(f"⚠️ 所有账号都无法访问频道，保持使用账号: {current_account}")
    return False


def get_account_channel_access_key(account_name, channel_id):
    """生成账号频道访问权限缓存键"""
    return f"{account_name}_{channel_id}"


def is_channel_accessible_for_account(account_name, channel_id):
    """检查账号是否可访问指定频道"""
    key = get_account_channel_access_key(account_name, channel_id)
    return account_channel_access.get(key, None)


def set_channel_access_for_account(account_name, channel_id, accessible, reason=""):
    """设置账号对频道的访问权限"""
    key = get_account_channel_access_key(account_name, channel_id)
    account_channel_access[key] = {
        "accessible": accessible,
        "reason": reason
    }


def clear_account_channel_access_cache():
    """清空账号频道访问权限缓存"""
    global account_channel_access
    account_channel_access.clear()


def should_rotate_account():
    """判断是否应该轮换账号"""
    if not enable_account_rotation or len(clients) <= 1:
        return False

    current_client_data = clients[current_client_index]
    return current_client_data["forward_count"] >= rotation_interval


def reset_account_counter():
    """重置当前账号的转发计数"""
    clients[current_client_index]["forward_count"] = 0


def increment_account_counter():
    """增加当前账号的转发计数"""
    clients[current_client_index]["forward_count"] += 1


def get_account_stats():
    """获取所有账号的统计信息"""
    stats = []
    for i, client_data in enumerate(clients):
        account = client_data["account"]
        stats.append({
            "index": i,
            "session_name": account["session_name"],
            "forward_count": client_data["forward_count"],
            "is_current": i == current_client_index
        })
    return stats


# ---------- 频道ID标准化函数 ----------
def normalize_channel_id(channel_id):
    """标准化频道ID格式，确保使用完整的-100格式"""
    if channel_id is None:
        return None

    # 转换为字符串
    channel_str = str(channel_id)

    # 如果已经是完整的频道ID格式，直接返回
    if channel_str.startswith('-100'):
        return channel_str

    # 如果是正数ID，转换为完整的频道ID格式
    try:
        if int(channel_str) > 0:
            return f"-100{channel_str}"
    except ValueError:
        pass

    # 其他情况直接返回原字符串
    return channel_str


# ---------- 进度存取（合并到转发历史文件） ----------
def load_progress():
    """从转发历史文件中加载进度信息"""
    history = load_forward_history()
    progress = {}
    for channel_key, data in history.items():
        progress[channel_key] = data.get("last_message_id", 0)
    return progress


def save_progress(src_id, dst_id, last_id):
    """将进度信息保存到转发历史文件中"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)
    init_forward_history_entry(history, channel_key)

    history[channel_key]["last_message_id"] = last_id
    history[channel_key]["last_update"] = str(asyncio.get_event_loop().time())

    save_forward_history(history)


def get_progress_for_channels(src_id, dst_id):
    """获取特定频道组合的进度"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)

    if channel_key not in history:
        return 0

    return history[channel_key].get("last_message_id", 0)


# ---------- 转发历史记录 ----------
def load_forward_history():
    """加载转发历史记录"""
    if os.path.exists(forward_history_file):
        try:
            with open(forward_history_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ 转发历史文件格式错误，将重新创建: {e}")
            backup_file = f"{forward_history_file}.backup"
            if os.path.exists(forward_history_file):
                os.rename(forward_history_file, backup_file)
                print(f"📁 已备份损坏文件到: {backup_file}")
            return {}
    return {}


def recover_forward_history():
    """尝试恢复转发历史记录"""
    backup_file = f"{forward_history_file}.backup"
    if os.path.exists(backup_file):
        try:
            with open(backup_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
                    print(f"🔄 发现备份文件，正在恢复转发历史...")
                    save_forward_history(history)
                    print(f"✅ 转发历史已从备份恢复")
                    return True
        except Exception as e:
            print(f"⚠️ 恢复备份文件失败: {e}")

    # 检查是否有临时文件
    temp_file = f"{forward_history_file}.tmp"
    if os.path.exists(temp_file):
        try:
            with open(temp_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
                    print(f"🔄 发现临时文件，正在恢复转发历史...")
                    save_forward_history(history)
                    print(f"✅ 转发历史已从临时文件恢复")
                    return True
        except Exception as e:
            print(f"⚠️ 恢复临时文件失败: {e}")

    return False


def save_forward_history(history):
    """保存转发历史记录（安全写入）"""
    # 先写入临时文件，然后重命名，确保原子性操作
    temp_file = f"{forward_history_file}.tmp"

    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            # 使用标准格式化，但通过自定义方式让数组紧凑
            json_str = json.dumps(history, indent=2, ensure_ascii=False)

            # 将数组格式化为紧凑形式（移除数组内的换行和缩进）
            import re
            # 匹配数组内容并移除换行和缩进
            def compact_arrays(match):
                array_content = match.group(1)
                # 移除换行和多余空格，保持逗号后的单个空格
                compact_content = re.sub(r'\s+', ' ', array_content.strip())
                return f'[{compact_content}]'

            # 处理数组：匹配 [ 到 ] 之间的内容
            compact_json = re.sub(r'\[\s*([^\]]*?)\s*\]', compact_arrays, json_str, flags=re.DOTALL)

            f.write(compact_json)
            f.flush()  # 确保数据写入磁盘
            os.fsync(f.fileno())  # 强制同步到磁盘

        # 原子性重命名
        if os.path.exists(forward_history_file):
            backup_file = f"{forward_history_file}.backup"
            os.rename(forward_history_file, backup_file)

        os.rename(temp_file, forward_history_file)

        # 删除备份文件（如果存在）
        backup_file = f"{forward_history_file}.backup"
        if os.path.exists(backup_file):
            os.remove(backup_file)

    except Exception as e:
        print(f"⚠️ 保存转发历史时发生错误: {e}")
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise


def add_forward_record(src_id, dst_id, msg_id, msg_type="single"):
    """添加转发记录"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)
    init_forward_history_entry(history, channel_key)

    # 只记录ID
    history[channel_key]["forwarded_messages"].append(msg_id)

    history[channel_key]["total_count"] += 1
    history[channel_key]["last_update"] = str(asyncio.get_event_loop().time())

    save_forward_history(history)


def add_filtered_record(src_id, dst_id, msg_id, filter_reason, filter_type="ad"):
    """添加过滤记录"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)
    init_forward_history_entry(history, channel_key)

    # 简化格式：ID-type
    record = f"{msg_id}-{filter_type}"
    history[channel_key]["filtered_messages"].append(record)

    history[channel_key]["filtered_count"] += 1
    history[channel_key]["last_update"] = str(asyncio.get_event_loop().time())

    save_forward_history(history)


def add_duplicate_record(src_id, dst_id, msg_id, msg_hash, source_info):
    """添加重复内容记录"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)
    init_forward_history_entry(history, channel_key)

    # 记录重复消息
    record = f"{msg_id}-duplicate-{msg_hash[:8]}"
    history[channel_key]["duplicate_messages"].append(record)

    history[channel_key]["duplicate_count"] = history[channel_key].get("duplicate_count", 0) + 1
    history[channel_key]["last_update"] = str(asyncio.get_event_loop().time())

    save_forward_history(history)


def is_already_forwarded(src_id, dst_id, msg_id):
    """检查消息是否已经转发过"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)

    if channel_key not in history:
        return False

    # 直接检查ID
    return msg_id in history[channel_key]["forwarded_messages"]


def get_forward_stats(src_id, dst_id):
    """获取转发统计信息"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)

    if channel_key not in history:
        return {"total": 0, "messages": 0, "groups": 0, "filtered": 0, "duplicates": 0}

    data = history[channel_key]

    return {
        "total": data["total_count"],
        "messages": len(data["forwarded_messages"]),  # 不再区分单条和相册
        "groups": 0,  # 不再统计相册
        "filtered": data.get("filtered_count", 0),
        "duplicates": data.get("duplicate_count", 0)
    }


def get_filtered_stats(src_id, dst_id):
    """获取过滤统计信息"""
    history = load_forward_history()
    channel_key = get_channel_key(src_id, dst_id)

    if channel_key not in history:
        return {"ad_filtered": 0, "content_filtered": 0, "service_filtered": 0, "duplicate_filtered": 0}

    data = history[channel_key]
    filtered_messages = data.get("filtered_messages", [])
    duplicate_messages = data.get("duplicate_messages", [])

    stats = {"ad_filtered": 0, "content_filtered": 0, "service_filtered": 0,
             "duplicate_filtered": len(duplicate_messages)}
    for record in filtered_messages:
        if record.endswith("-ad"):
            stats["ad_filtered"] += 1
        elif record.endswith("-content"):
            stats["content_filtered"] += 1
        elif record.endswith("-service"):
            stats["service_filtered"] += 1

    return stats


# ---------- 广告检测函数 ----------
def is_ad_message(text, has_media=False):
    """检测消息是否为广告"""
    if not enable_ad_filter or not text:
        return False

    text_lower = text.lower()

    # 1. 检查关键词
    for keyword in ad_keywords:
        if keyword in text_lower:
            return True

    # 2. 检查正则模式
    link_count = 0
    for pattern in ad_patterns:
        matches = re.findall(pattern, text)
        if pattern == r'https?://[^\s]+':  # 链接计数
            link_count += len(matches)
        elif matches:  # 其他模式有匹配就认为是广告
            return True

    # 3. 检查链接数量
    if link_count > max_links_per_message:
        return True

    # 4. 检查消息长度（如果有媒体内容，则放宽长度限制）
    if len(text.strip()) < min_message_length:
        # 如果有媒体内容，则不过滤短消息
        if has_media:
            return False
        return True

    return False


def get_ad_reason(text, has_media=False):
    """获取被识别为广告的原因"""
    if not text:
        return "无文本内容"

    text_lower = text.lower()
    reasons = []

    # 检查关键词
    for keyword in ad_keywords:
        if keyword in text_lower:
            reasons.append(f"包含关键词: {keyword}")

    # 检查链接数量
    links = re.findall(r'https?://[^\s]+', text)
    if len(links) > max_links_per_message:
        reasons.append(f"链接过多: {len(links)}个")

    # 检查消息长度
    if len(text.strip()) < min_message_length:
        if has_media:
            reasons.append(f"消息过短但有媒体: {len(text.strip())}字符")
        else:
            reasons.append(f"消息过短: {len(text.strip())}字符")

    # 检查其他模式
    for pattern in ad_patterns:
        if pattern != r'https?://[^\s]+':  # 链接已单独处理
            matches = re.findall(pattern, text)
            if matches:
                reasons.append(f"匹配模式: {pattern}")

    return "; ".join(reasons) if reasons else "未知原因"


# ---------- 内容质量检测函数 ----------
def is_meaningless_message(text, has_media=False):
    """检测消息是否为无意义内容"""
    if not enable_content_filter or not text:
        return False

    text = text.strip()

    # 1. 检查是否为无意义词汇
    if text.lower() in [word.lower() for word in meaningless_words]:
        return should_filter_with_media_check(has_media, True)

    # 2. 检查重复字符（如"哈哈哈"、"1111"等）
    if len(text) > 1:
        char_counts = get_char_counts(text)
        max_char_count = max(char_counts.values())
        if max_char_count > max_repeat_chars and max_char_count / len(text) > 0.6:
            return should_filter_with_media_check(has_media, not has_media)

    # 3. 检查表情符号比例
    emoji_count = get_emoji_count(text)
    if len(text) > 0 and emoji_count / len(text) > max_emoji_ratio:
        return should_filter_with_media_check(has_media, not has_media)

    # 4. 检查是否只包含数字、标点或空格
    meaningful_chars = get_meaningful_chars_count(text)
    if meaningful_chars < min_meaningful_length:
        return should_filter_with_media_check(has_media, not has_media)

    # 5. 检查是否只包含单个字符重复
    if len(set(text.replace(' ', ''))) <= 1 and len(text) > 1:
        return should_filter_with_media_check(has_media, not has_media)

    return False


def get_content_filter_reason(text, has_media=False):
    """获取内容被过滤的原因"""
    if not text:
        return "无文本内容"

    text = text.strip()
    reasons = []

    # 检查无意义词汇
    if text.lower() in [word.lower() for word in meaningless_words]:
        if enable_media_required_filter and not has_media:
            reasons.append(f"无意义词汇且无媒体: {text}")
        else:
            reasons.append(f"无意义词汇: {text}")

    # 检查重复字符
    if len(text) > 1:
        char_counts = get_char_counts(text)
        max_char_count = max(char_counts.values())
        if max_char_count > max_repeat_chars and max_char_count / len(text) > 0.6:
            if enable_media_required_filter and not has_media:
                reasons.append(f"重复字符过多且无媒体: {max_char_count}个")
            else:
                reasons.append(f"重复字符过多: {max_char_count}个")

    # 检查表情符号比例
    emoji_count = get_emoji_count(text)
    if len(text) > 0 and emoji_count / len(text) > max_emoji_ratio:
        if enable_media_required_filter and not has_media:
            reasons.append(f"表情符号过多且无媒体: {emoji_count}/{len(text)}")
        else:
            reasons.append(f"表情符号过多: {emoji_count}/{len(text)}")

    # 检查有意义内容长度
    meaningful_chars = get_meaningful_chars_count(text)
    if meaningful_chars < min_meaningful_length:
        if enable_media_required_filter and not has_media:
            reasons.append(f"有意义内容过少且无媒体: {meaningful_chars}字符")
        else:
            reasons.append(f"有意义内容过少: {meaningful_chars}字符")

    # 检查单字符重复
    if len(set(text.replace(' ', ''))) <= 1 and len(text) > 1:
        if enable_media_required_filter and not has_media:
            reasons.append("单字符重复且无媒体")
        else:
            reasons.append("单字符重复")

    return "; ".join(reasons) if reasons else "未知原因"


# ---------- 内容去重函数 ----------
def generate_message_hash(msg):
    """为消息生成唯一哈希值（仅基于媒体文件）"""
    hash_content = generate_media_hash_content(msg)
    return hashlib.md5(hash_content.encode('utf-8')).hexdigest()


def generate_album_hash(album_messages):
    """为整个相册生成唯一哈希值（基于相册中所有媒体文件）"""
    if not album_messages:
        return ""

    # 收集相册中所有媒体文件的哈希信息
    media_hashes = []

    for msg in album_messages:
        media_hashes.append(generate_media_hash_content(msg))

    # 按顺序排序，确保相同内容的相册生成相同的哈希
    media_hashes.sort()

    # 组合所有媒体信息
    combined_content = "|".join(media_hashes)

    # 生成MD5哈希
    return hashlib.md5(combined_content.encode('utf-8')).hexdigest()


def filter_duplicate_messages_from_album(album_messages):
    """从相册中过滤掉重复的消息，返回不重复的消息列表"""
    if not enable_content_deduplication or not album_messages:
        return album_messages

    # 使用新的相册哈希逻辑：以整个相册组作为hash值判断
    album_hash = generate_album_hash(album_messages)

    if is_duplicate_content(album_hash):
        # 整个相册都是重复的，返回空列表
        if verbose_dedup_logging:
            # print(f"  📊 相册去重: 整个相册重复，跳过 {len(album_messages)} 张图片")
            pass
        return []
    else:
        # 相册不重复，返回所有消息
        # 添加到去重历史（add_to_dedup_history内部已检查重复）
        source_info = f"相册处理"
        add_to_dedup_history(album_hash, source_info)

        if verbose_dedup_logging:
            # print(f"  📊 相册去重: 相册不重复，保留 {len(album_messages)} 张图片")
            pass
        return album_messages


async def scan_target_channel(dst_dialog, scan_limit=None, force_rescan=False):
    """扫描目标频道，预加载去重历史（支持断点续传）"""
    if not enable_content_deduplication:
        return 0

    client = get_current_client()
    account_info = get_current_account_info()

    # 检查是否有之前的扫描进度
    last_message_id, previous_scanned = get_scan_progress(dst_dialog.id)

    print(f"\n🔍 正在扫描目标频道: {get_channel_name(dst_dialog)}")

    # 获取频道总消息数
    try:
        total_messages = await client.get_messages(dst_dialog, limit=1)
        if total_messages:
            # 获取第一条消息的ID作为总数估算
            first_msg = total_messages[0]
            estimated_total = first_msg.id if first_msg.id else 0
            print(f"📈 频道总消息数（估算）: {estimated_total} 条")
        else:
            print("📈 频道总消息数: 0 条")
            estimated_total = 0
    except Exception as e:
        print(f"⚠️ 无法获取频道消息总数: {e}")
        estimated_total = 0

    # 如果强制重新扫描，忽略之前的进度
    if force_rescan:
        print(f"🔄 强制重新扫描模式")
        last_message_id = None
        previous_scanned = 0

    if last_message_id:
        print(f"📊 从消息 ID {last_message_id} 继续扫描（已扫描 {previous_scanned} 条）")
        if estimated_total > 0:
            remaining_estimate = estimated_total - last_message_id
            print(f"📊 预计剩余待扫描: {remaining_estimate} 条消息")
    else:
        if scan_limit:
            print(f"📊 扫描范围: 最近 {scan_limit} 条消息")
        else:
            print(f"📊 扫描范围: 所有消息")
            if estimated_total > 0:
                print(f"📊 预计扫描总数: {estimated_total} 条消息")

    scanned_count = previous_scanned
    media_count = 0
    group_count = 0
    last_group = None
    group_buffer = []
    last_processed_id = last_message_id
    new_hash_count = 0  # 新增hash计数

    try:
        # 修改扫描逻辑：不使用offset_id，而是从最新消息开始扫描
        # 这样可以确保扫描到所有新消息（包括手动转发的）
        if scan_limit:
            message_iter = client.iter_messages(dst_dialog, limit=scan_limit)
        else:
            message_iter = client.iter_messages(dst_dialog)

        async for msg in message_iter:
            # 处理消息ID为None的情况
            if msg.id is None:
                continue

            # 如果设置了last_message_id，跳过已经扫描过的消息
            if last_message_id is not None and msg.id <= last_message_id:
                continue

            scanned_count += 1
            last_processed_id = msg.id

            # 处理相册
            if msg.grouped_id:
                if last_group is None:
                    last_group = msg.grouped_id
                if msg.grouped_id == last_group:
                    group_buffer.append(msg)
                    continue
                else:
                    if group_buffer:
                        # 处理完整的相册 - 使用相册哈希
                        album_hash = generate_album_hash(group_buffer)
                        if album_hash:
                            source_info = f"目标频道:{get_channel_name(dst_dialog)}({dst_dialog.id})"
                            # 检查是否是新hash，避免重复添加
                            if not is_duplicate_content(album_hash):
                                add_to_dedup_history(album_hash, source_info)
                                new_hash_count += 1
                            media_count += len(group_buffer)
                        group_count += 1
                    group_buffer = [msg]
                    last_group = msg.grouped_id
            else:
                if group_buffer:
                    # 处理剩余的相册 - 使用相册哈希
                    album_hash = generate_album_hash(group_buffer)
                    if album_hash:
                        source_info = f"目标频道:{get_channel_name(dst_dialog)}({dst_dialog.id})"
                        # 检查是否是新hash，避免重复添加
                        if not is_duplicate_content(album_hash):
                            add_to_dedup_history(album_hash, source_info)
                            new_hash_count += 1
                        media_count += len(group_buffer)
                    group_count += 1
                    group_buffer = []

                # 处理单条消息
                if msg.media or msg.message:
                    msg_hash = generate_message_hash(msg)
                    if msg_hash:
                        source_info = f"目标频道:{get_channel_name(dst_dialog)}({dst_dialog.id})"
                        # 检查是否是新hash，避免重复添加
                        if not is_duplicate_content(msg_hash):
                            add_to_dedup_history(msg_hash, source_info)
                            new_hash_count += 1
                        media_count += 1

            # 每100条消息更新一次进度
            if scanned_count % 100 == 0:
                if estimated_total > 0 and last_message_id:
                    # 计算进度百分比
                    total_to_scan = estimated_total - last_message_id
                    if total_to_scan > 0:
                        progress_percent = (scanned_count - previous_scanned) / total_to_scan * 100
                        print(f"  📈 已扫描: {scanned_count} 条消息 (进度: {progress_percent:.1f}%)")
                    else:
                        print(f"  📈 已扫描: {scanned_count} 条消息")
                else:
                    print(f"  📈 已扫描: {scanned_count} 条消息")
                if last_processed_id is not None:
                    update_scan_progress(dst_dialog.id, last_processed_id, scanned_count)

        # 处理最后的相册 - 使用相册哈希
        if group_buffer:
            album_hash = generate_album_hash(group_buffer)
            if album_hash:
                source_info = f"目标频道:{get_channel_name(dst_dialog)}({dst_dialog.id})"
                # 检查是否是新hash，避免重复添加
                if not is_duplicate_content(album_hash):
                    add_to_dedup_history(album_hash, source_info)
                    new_hash_count += 1
                media_count += len(group_buffer)
            group_count += 1

        # 更新最终进度
        if last_processed_id is not None:
            update_scan_progress(dst_dialog.id, last_processed_id, scanned_count)

        print(f"✅ 目标频道扫描完成:")
        print(f"  📝 总扫描消息: {scanned_count} 条")
        if last_message_id and previous_scanned > 0:
            new_scanned = scanned_count - previous_scanned
            print(f"  🆕 本次新增扫描: {new_scanned} 条")
        print(f"  🖼️ 媒体内容: {media_count} 条")
        print(f"  📚 相册组: {group_count} 组")
        print(f"  🆕 新增hash: {new_hash_count} 条")
        print(f"  🔄 已预加载到去重历史")

        if estimated_total > 0:
            coverage_percent = (scanned_count / estimated_total) * 100
            print(f"  📊 扫描覆盖率: {coverage_percent:.1f}% ({scanned_count}/{estimated_total})")

        return scanned_count

    except Exception as e:
        print(f"⚠️ 扫描目标频道时发生错误: {e}")
        # 保存当前进度，方便下次继续
        if last_processed_id is not None:
            update_scan_progress(dst_dialog.id, last_processed_id, scanned_count)
            print(f"💾 已保存扫描进度，下次可以从消息 ID {last_processed_id} 继续")
        return scanned_count


def load_dedup_history():
    """加载去重历史记录"""
    if os.path.exists(dedup_history_file):
        try:
            with open(dedup_history_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ 去重历史文件格式错误，将重新创建: {e}")
            backup_file = f"{dedup_history_file}.backup"
            if os.path.exists(dedup_history_file):
                os.rename(dedup_history_file, backup_file)
                print(f"📁 已备份损坏文件到: {backup_file}")
            return {}
    return {}


def save_dedup_history(history):
    """保存去重历史记录（安全写入）"""
    # 先写入临时文件，然后重命名，确保原子性操作
    temp_file = f"{dedup_history_file}.tmp"

    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            f.flush()  # 确保数据写入磁盘
            os.fsync(f.fileno())  # 强制同步到磁盘

        # 原子性重命名
        if os.path.exists(dedup_history_file):
            backup_file = f"{dedup_history_file}.backup"
            os.rename(dedup_history_file, backup_file)

        os.rename(temp_file, dedup_history_file)

        # 删除备份文件（如果存在）
        backup_file = f"{dedup_history_file}.backup"
        if os.path.exists(backup_file):
            os.remove(backup_file)

    except Exception as e:
        print(f"⚠️ 保存去重历史时发生错误: {e}")
        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
        raise


def is_duplicate_content(msg_hash):
    """检查内容是否重复"""
    if not enable_content_deduplication:
        return False

    history = load_dedup_history()
    return msg_hash in history


def add_to_dedup_history(msg_hash, source_info):
    """添加内容到去重历史（只保存hash）"""
    if not enable_content_deduplication:
        return

    history = load_dedup_history()
    # 检查hash是否已存在，避免重复添加
    if msg_hash not in history:
        history[msg_hash] = True
        save_dedup_history(history)


def set_target_channel_info(channel_name, channel_id):
    """设置目标频道信息（只在文件开头显示一次）"""
    if not enable_content_deduplication:
        return

    history = load_dedup_history()
    # 在文件开头记录目标频道信息
    history["_target_channel"] = f"{channel_name}({channel_id})"
    save_dedup_history(history)


def update_scan_progress(channel_id, last_message_id, total_scanned):
    """更新扫描进度"""
    if not enable_content_deduplication:
        return

    history = load_dedup_history()
    if "_scan_progress" not in history:
        history["_scan_progress"] = {}

    # 确保使用完整的频道ID格式作为键
    normalized_id = str(channel_id)
    if not normalized_id.startswith('-100') and int(normalized_id) > 0:
        # 如果是正数ID，转换为完整的频道ID格式
        normalized_id = f"-100{normalized_id}"

    history["_scan_progress"][normalized_id] = {
        "last_message_id": last_message_id,
        "total_scanned": total_scanned,
        "last_update": str(asyncio.get_event_loop().time())
    }
    save_dedup_history(history)


def get_scan_progress(channel_id):
    """获取扫描进度"""
    if not enable_content_deduplication:
        return None, 0

    history = load_dedup_history()
    if "_scan_progress" not in history:
        return None, 0

    # 尝试多种ID格式
    possible_ids = [str(channel_id)]

    # 如果是完整ID，也尝试短ID
    if str(channel_id).startswith('-100'):
        short_id = str(channel_id)[4:]  # 移除-100前缀
        possible_ids.append(short_id)
    # 如果是短ID，也尝试完整ID
    elif not str(channel_id).startswith('-') and int(str(channel_id)) > 0:
        full_id = f"-100{str(channel_id)}"
        possible_ids.append(full_id)

    # 按优先级查找进度记录
    for channel_key in possible_ids:
        progress = history["_scan_progress"].get(channel_key)
        if progress:
            return progress.get("last_message_id"), progress.get("total_scanned", 0)

    return None, 0


def get_dedup_stats():
    """获取去重统计信息"""
    if not enable_content_deduplication:
        return {"total_unique": 0, "target_channel": None}

    history = load_dedup_history()

    # 统计总数（排除系统字段）
    total_unique = 0
    target_channel = history.get("_target_channel")

    for key, value in history.items():
        if key.startswith("_"):  # 跳过系统字段
            continue

        if isinstance(value, bool) and value:  # 只统计hash记录
            total_unique += 1

    return {
        "total_unique": total_unique,
        "target_channel": target_channel
    }


# ---------- 频道解析和验证函数 ----------
def get_channel_name(entity):
    """安全地获取频道/群组名称"""
    return getattr(entity, 'title', None) or getattr(entity, 'name', None) or "未知频道"


def parse_channel_identifier(channel_id):
    """解析频道标识符，支持多种格式"""
    if isinstance(channel_id, int):
        return channel_id
    elif isinstance(channel_id, str):
        # 处理频道链接
        if channel_id.startswith("https://t.me/"):
            username = channel_id.replace("https://t.me/", "").strip()
            return username
        # 处理@用户名
        elif channel_id.startswith("@"):
            return channel_id[1:]  # 移除@符号
        # 处理纯用户名
        else:
            return channel_id
    return None


async def get_channel_by_identifier(client, channel_id):
    """根据标识符获取频道对象"""
    try:
        parsed_id = parse_channel_identifier(channel_id)
        if parsed_id is None:
            print(f"⚠️ 无法解析频道标识符: {channel_id}")
            return None

        # 尝试获取频道
        entity = await client.get_entity(parsed_id)

        # 验证频道类型
        if hasattr(entity, 'megagroup') or hasattr(entity, 'broadcast'):
            return entity
        else:
            print(f"⚠️ 对象不是频道或群组: {channel_id} (类型: {type(entity).__name__})")
            return None

    except Exception as e:
        # print(f"⚠️ 无法获取频道 {channel_id}: {e}")
        return None


async def validate_preset_channels(client, source_channels, target_channel):
    """验证预设频道是否存在且可访问"""
    validated_sources = []
    validated_target = None

    # 验证源频道
    if source_channels:
        for i, channel_id in enumerate(source_channels, 1):
            print(f"  {i}. 验证频道: {channel_id}")
            entity = await get_channel_by_identifier(client, channel_id)
            if entity:
                validated_sources.append(entity)
                # 获取频道名称
                entity_name = get_channel_name(entity)
            else:
                print(f"     ❌ 失败: 无法访问频道 {channel_id}")

    # 验证目标频道
    if target_channel:
        entity = await get_channel_by_identifier(client, target_channel)
        if entity:
            validated_target = entity
            # 获取频道名称
            entity_name = get_channel_name(entity)
        else:
            print(f"     ❌ 失败: 无法访问目标频道 {target_channel}")

    return validated_sources, validated_target


# ---------- 频道信息导出函数 ----------
async def export_channels_to_json(client, account_name):
    """导出指定账号的所有频道信息为JSON格式"""
    try:
        print(f"🔍 正在获取账号 {account_name} 的频道信息...")

        # 获取所有对话
        dialogs = await client.get_dialogs()

        # 过滤出频道和群组
        channels = []
        for dialog in dialogs:
            # 检查是否为频道或群组
            if hasattr(dialog.entity, 'megagroup') or hasattr(dialog.entity, 'broadcast'):
                channels.append(dialog)

        # 构建频道信息字典
        channel_info = {}

        for dialog in channels:
            try:
                entity = dialog.entity
                original_name = entity.title if hasattr(entity, 'title') else "未知频道"
                # 使用与手动选择相同的ID格式
                channel_id = dialog.id

                # 处理频道名字：只显示第一个字和最后一个字，中间用***代替
                if len(original_name) <= 2:
                    # 如果名字只有1-2个字符，直接显示
                    channel_name = original_name
                else:
                    # 显示第一个字 + *** + 最后一个字
                    channel_name = original_name[0] + "***" + original_name[-1]

                # 获取完整的频道ID（保持原始格式）
                full_channel_id = channel_id

                # 尝试获取频道链接
                channel_link = None
                if hasattr(entity, 'username') and entity.username:
                    # 有用户名的频道，使用用户名链接
                    channel_link = f"https://t.me/{entity.username}"
                else:
                    # 没有用户名的频道，尝试获取邀请链接
                    try:
                        # 尝试通过API获取邀请链接
                        try:
                            # 先获取实体，再访问邀请链接属性
                            entity_obj = await client.get_entity(entity)
                            if hasattr(entity_obj, 'invite_link') and entity_obj.invite_link:
                                channel_link = entity_obj.invite_link
                            else:
                                # 尝试生成邀请链接
                                invite_link = await client.export_chat_invite_link(entity)
                                if invite_link:
                                    channel_link = invite_link
                                else:
                                    # 没有邀请链接，尝试获取频道中任意一条消息的链接
                                    try:
                                        # 获取频道中的一条消息
                                        messages = await client.get_messages(entity, limit=1)
                                        if messages and messages[0].id:
                                            # 生成消息链接
                                            if str(full_channel_id).startswith('-100'):
                                                short_id = str(full_channel_id)[4:]  # 移除-100前缀
                                            else:
                                                short_id = str(full_channel_id)
                                            channel_link = f"https://t.me/c/{short_id}/{messages[0].id}"
                                        else:
                                            channel_link = f"频道ID: {full_channel_id}"
                                    except:
                                        channel_link = f"频道ID: {full_channel_id}"
                        except:
                            # 如果无法获取邀请链接，尝试获取消息链接
                            try:
                                messages = await client.get_messages(entity, limit=1)
                                if messages and messages[0].id:
                                    if str(full_channel_id).startswith('-100'):
                                        short_id = str(full_channel_id)[4:]
                                    else:
                                        short_id = str(full_channel_id)
                                    channel_link = f"https://t.me/c/{short_id}/{messages[0].id}"
                                else:
                                    channel_link = f"频道ID: {full_channel_id}"
                            except:
                                channel_link = f"频道ID: {full_channel_id}"
                    except:
                        # 备用方案：尝试获取消息链接
                        try:
                            messages = await client.get_messages(entity, limit=1)
                            if messages and messages[0].id:
                                if str(full_channel_id).startswith('-100'):
                                    short_id = str(full_channel_id)[4:]
                                else:
                                    short_id = str(full_channel_id)
                                channel_link = f"https://t.me/c/{short_id}/{messages[0].id}"
                            else:
                                channel_link = f"频道ID: {full_channel_id}"
                        except:
                            channel_link = f"频道ID: {full_channel_id}"

                # 格式：频道名字：频道id-频道链接
                # 确保频道ID包含完整的-100前缀
                channel_info[channel_name] = f"{full_channel_id}-{channel_link}"

            except Exception as e:
                print(f"⚠️ 处理频道 {get_channel_name(dialog)} 时出错: {e}")
                continue

        return channel_info

    except Exception as e:
        print(f"❌ 导出频道信息时发生错误: {e}")
        return {}


async def export_all_accounts_channels():
    """导出所有账号的频道信息"""
    if not clients:
        print("❌ 没有可用的账号！")
        return

    print("🚀 开始导出所有账号的频道信息...")

    all_accounts_channels = {}

    for i, client_data in enumerate(clients):
        if not client_data["enabled"]:
            continue

        account_name = client_data["account"]["session_name"]
        client = client_data["client"]

        try:
            # 启动客户端
            await client.start()
            print(f"✅ 账号 {account_name} 启动成功")

            # 导出频道信息
            channel_info = await export_channels_to_json(client, account_name)
            all_accounts_channels[account_name] = channel_info

            print(f"📋 账号 {account_name} 导出完成: {len(channel_info)} 个频道")

        except Exception as e:
            print(f"❌ 账号 {account_name} 导出失败: {e}")
            all_accounts_channels[account_name] = {}

    # 保存到JSON文件
    output_file = "channels_export.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_accounts_channels, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 频道信息已导出到: {output_file}")
        print(f"📊 导出统计:")

        total_channels = 0
        for account_name, channels in all_accounts_channels.items():
            channel_count = len(channels)
            total_channels += channel_count
            print(f"  {account_name}: {channel_count} 个频道")

        print(f"  总计: {total_channels} 个频道")

    except Exception as e:
        print(f"❌ 保存导出文件时发生错误: {e}")


# ---------- 命令行选择 ----------
async def choose_dialog(title: str):
    client = get_current_client()
    account_info = get_current_account_info()
    dialogs = await client.get_dialogs()
    print(f"\n=== 请选择 {title} ===")
    print(f"📱 当前账号: {account_info['session_name']}")
    for i, dialog in enumerate(dialogs, 1):
        name = get_channel_name(dialog)
        print(f"{i}. {name} ({dialog.id})")

    while True:
        try:
            idx = int(input(f"请输入序号选择 {title}: "))
            if 1 <= idx <= len(dialogs):
                return dialogs[idx - 1]
        except Exception:
            pass
        print("❌ 输入无效，请重新选择。")


async def choose_multiple_dialogs(title: str):
    """选择多个频道/群组"""
    client = get_current_client()
    account_info = get_current_account_info()
    dialogs = await client.get_dialogs()
    print(f"\n=== 请选择多个 {title} ===")
    print(f"📱 当前账号: {account_info['session_name']}")
    for i, dialog in enumerate(dialogs, 1):
        name = get_channel_name(dialog)
        print(f"{i}. {name} ({dialog.id})")

    print(f"\n💡 提示：")
    print(f"   - 输入单个数字选择单个频道")
    print(f"   - 输入多个数字用逗号分隔，如：1,3,5")
    print(f"   - 输入范围用连字符，如：1-5")
    print(f"   - 输入 'all' 选择所有频道")
    print(f"   - 输入 'q' 或 'quit' 退出")

    while True:
        try:
            choice = input(f"请输入选择 {title}: ").strip()

            if choice.lower() in ['q', 'quit']:
                return []

            if choice.lower() == 'all':
                return dialogs

            selected_dialogs = []

            # 处理逗号分隔的选择
            if ',' in choice:
                parts = choice.split(',')
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        # 处理范围
                        start, end = map(int, part.split('-'))
                        for i in range(start, end + 1):
                            if 1 <= i <= len(dialogs):
                                selected_dialogs.append(dialogs[i - 1])
                    else:
                        # 处理单个数字
                        idx = int(part)
                        if 1 <= idx <= len(dialogs):
                            selected_dialogs.append(dialogs[idx - 1])
            elif '-' in choice:
                # 处理范围选择
                start, end = map(int, choice.split('-'))
                for i in range(start, end + 1):
                    if 1 <= i <= len(dialogs):
                        selected_dialogs.append(dialogs[i - 1])
            else:
                # 处理单个数字
                idx = int(choice)
                if 1 <= idx <= len(dialogs):
                    selected_dialogs.append(dialogs[idx - 1])

            if selected_dialogs:
                print(f"\n✅ 已选择 {len(selected_dialogs)} 个 {title}:")
                for i, dialog in enumerate(selected_dialogs, 1):
                    name = get_channel_name(dialog)
                    print(f"  {i}. {name} ({dialog.id})")
                return selected_dialogs
            else:
                print("❌ 没有选择任何有效的频道，请重新输入。")

        except Exception as e:
            print(f"❌ 输入无效，请重新选择。错误: {e}")


# ---------- 转发函数（处理 FloodWait 和多账号） ----------
async def forward_message_safe(dst, msg):
    client = get_current_client()
    account_info = get_current_account_info()

    while True:
        try:
            await client.forward_messages(dst, msg)
            increment_account_counter()
            return True, None
        except errors.FloodWaitError as e:
            print(f"⏸ FloodWait ({account_info['session_name']})，需要等待 {e.seconds} 秒")
            await asyncio.sleep(e.seconds + 5)
        except errors.ChatWriteForbiddenError:
            print(f"🚫 无法转发消息 {msg.id} ({account_info['session_name']}): 目标频道禁止写入")
            return False, "chat_write_forbidden"
        except errors.ChatAdminRequiredError:
            print(f"🚫 无法转发消息 {msg.id} ({account_info['session_name']}): 需要管理员权限")
            return False, "admin_required"
        except errors.InputUserDeactivatedError:
            print(f"🚫 无法转发消息 {msg.id} ({account_info['session_name']}): 用户已停用")
            return False, "user_deactivated"
        except errors.UserBannedInChannelError:
            print(f"🚫 无法转发消息 {msg.id} ({account_info['session_name']}): 用户被频道封禁")
            return False, "user_banned"
        except Exception as e:
            return handle_forward_error(e, msg.id, account_info['session_name'], "消息")


async def forward_group_safe(dst, msgs):
    client = get_current_client()
    account_info = get_current_account_info()

    while True:
        try:
            await client.forward_messages(dst, msgs)
            increment_account_counter()
            return True, None
        except errors.FloodWaitError as e:
            print(f"⏸ FloodWait ({account_info['session_name']})，需要等待 {e.seconds} 秒")
            await asyncio.sleep(e.seconds + 5)
        except errors.ChatWriteForbiddenError:
            print(f"🚫 无法转发相册 {msgs[0].grouped_id if msgs else 'unknown'} ({account_info['session_name']}): 目标频道禁止写入")
            return False, "chat_write_forbidden"
        except errors.ChatAdminRequiredError:
            print(f"🚫 无法转发相册 {msgs[0].grouped_id if msgs else 'unknown'} ({account_info['session_name']}): 需要管理员权限")
            return False, "admin_required"
        except errors.InputUserDeactivatedError:
            print(f"🚫 无法转发相册 {msgs[0].grouped_id if msgs else 'unknown'} ({account_info['session_name']}): 用户已停用")
            return False, "user_deactivated"
        except errors.UserBannedInChannelError:
            print(f"🚫 无法转发相册 {msgs[0].grouped_id if msgs else 'unknown'} ({account_info['session_name']}): 用户被频道封禁")
            return False, "user_banned"
        except Exception as e:
            msg_id = msgs[0].grouped_id if msgs else 'unknown'
            return handle_forward_error(e, msg_id, account_info['session_name'], "相册")


async def check_channel_accessibility(src_dialog, dst_dialog, account_name=None):
    """检查源频道是否可以被访问和转发"""
    client = get_current_client()
    account_info = get_current_account_info()

    # 如果指定了账号名称，使用指定的账号；否则使用当前账号
    if account_name:
        # 查找指定账号的客户端
        target_client = None
        for client_data in clients:
            if client_data["account"]["session_name"] == account_name:
                target_client = client_data["client"]
                break
        if not target_client:
            return False, f"账号 {account_name} 不存在"
        client = target_client
    else:
        account_name = account_info["session_name"]

    # 检查缓存
    cached_access = is_channel_accessible_for_account(account_name, src_dialog.id)
    if cached_access is not None:
        return cached_access["accessible"], cached_access["reason"]

    try:
        # 尝试获取频道信息
        entity = await client.get_entity(src_dialog.id)

        # 尝试获取一条消息来测试访问权限
        test_msg = None
        try:
            # 使用频道实体而不是dialog对象
            async for msg in client.iter_messages(entity, limit=1):
                test_msg = msg
                break
        except Exception as msg_e:
            print(f"⚠️ 账号 {account_name} 无法获取频道消息: {msg_e}")
            # 备用方案：使用dialog对象
            async for msg in client.iter_messages(src_dialog, limit=1):
                test_msg = msg
                break

        if test_msg is None:
            result = True, "可访问（无消息）"
            set_channel_access_for_account(account_name, src_dialog.id, True, "可访问（无消息）")
            return result

        # 尝试转发一条测试消息来检测受保护聊天
        try:
            await client.forward_messages(dst_dialog, test_msg)
            # 如果转发成功，立即删除转发的消息（避免污染目标频道）
            try:
                async for forwarded_msg in client.iter_messages(dst_dialog, limit=1):
                    if forwarded_msg.id:
                        await client.delete_messages(dst_dialog, forwarded_msg.id)
                        break
            except:
                pass  # 忽略删除失败
            result = True, "可访问"
            set_channel_access_for_account(account_name, src_dialog.id, True, "可访问")
            return result
        except errors.FloodWaitError as e:
            # FloodWait 不是访问问题，等待后重试
            await asyncio.sleep(e.seconds + 5)
            result = True, "可访问（FloodWait）"
            set_channel_access_for_account(account_name, src_dialog.id, True, "可访问（FloodWait）")
            return result
        except Exception as e:
            error_msg = str(e)
            if "protected chat" in error_msg.lower() or "can't forward messages from a protected chat" in error_msg.lower():
                result = False, PROTECTED_CHAT_REASON
                set_channel_access_for_account(account_name, src_dialog.id, False, PROTECTED_CHAT_REASON)
                return result
            elif "chat not found" in error_msg.lower():
                result = False, "聊天不存在"
                set_channel_access_for_account(account_name, src_dialog.id, False, "聊天不存在")
                return result
            elif "access denied" in error_msg.lower():
                result = False, "访问被拒绝"
                set_channel_access_for_account(account_name, src_dialog.id, False, "访问被拒绝")
                return result
            elif "chat write forbidden" in error_msg.lower():
                result = False, "目标频道禁止写入"
                set_channel_access_for_account(account_name, src_dialog.id, False, "目标频道禁止写入")
                return result
            else:
                # 其他错误可能是临时的，返回可访问
                result = True, f"可访问（警告: {error_msg[:50]}...）"
                set_channel_access_for_account(account_name, src_dialog.id, True, f"可访问（警告: {error_msg[:50]}...）")
                return result

    except errors.ChannelPrivateError as e:
        print(f"🔍 账号 {account_name} 频道可访问性检查失败: ChannelPrivateError - {e}")
        result = False, "频道是私有的"
        set_channel_access_for_account(account_name, src_dialog.id, False, "频道是私有的")
        return result
    except errors.ChannelInvalidError as e:
        print(f"🔍 账号 {account_name} 频道可访问性检查失败: ChannelInvalidError - {e}")
        result = False, "频道无效"
        set_channel_access_for_account(account_name, src_dialog.id, False, "频道无效")
        return result
    except errors.ChatAdminRequiredError as e:
        print(f"🔍 账号 {account_name} 频道可访问性检查失败: ChatAdminRequiredError - {e}")
        result = False, "需要管理员权限"
        set_channel_access_for_account(account_name, src_dialog.id, False, "需要管理员权限")
        return result
    except errors.UserBannedInChannelError as e:
        print(f"🔍 账号 {account_name} 频道可访问性检查失败: UserBannedInChannelError - {e}")
        result = False, "用户被频道封禁"
        set_channel_access_for_account(account_name, src_dialog.id, False, "用户被频道封禁")
        return result
    except errors.InputUserDeactivatedError as e:
        print(f"🔍 账号 {account_name} 频道可访问性检查失败: InputUserDeactivatedError - {e}")
        result = False, "用户已停用"
        set_channel_access_for_account(account_name, src_dialog.id, False, "用户已停用")
        return result
    except Exception as e:
        error_msg = str(e)
        print(f"🔍 账号 {account_name} 频道可访问性检查失败: {type(e).__name__} - {e}")
        if "invalid channel object" in error_msg.lower():
            result = False, "频道对象无效"
            set_channel_access_for_account(account_name, src_dialog.id, False, "频道对象无效")
            return result
        elif "protected chat" in error_msg.lower():
            result = False, PROTECTED_CHAT_REASON
            set_channel_access_for_account(account_name, src_dialog.id, False, PROTECTED_CHAT_REASON)
            return result
        elif "chat not found" in error_msg.lower():
            result = False, "聊天不存在"
            set_channel_access_for_account(account_name, src_dialog.id, False, "聊天不存在")
            return result
        elif "access denied" in error_msg.lower():
            result = False, "访问被拒绝"
            set_channel_access_for_account(account_name, src_dialog.id, False, "访问被拒绝")
            return result
        else:
            result = False, f"未知错误: {e}"
            set_channel_access_for_account(account_name, src_dialog.id, False, f"未知错误: {e}")
            return result


async def forward_from_single_source(src_dialog, dst_dialog):
    """从单个源频道转发消息到目标频道"""
    client = get_current_client()
    account_info = get_current_account_info()

    print(f"\n🔄 开始处理源频道: {get_channel_name(src_dialog)} ({normalize_channel_id(src_dialog.id)})")

    # 获取源频道总消息数
    try:
        # 先尝试获取频道信息
        try:
            channel_info = await client.get_entity(src_dialog.id)
        except Exception as info_e:
            print(f"⚠️ 无法获取频道信息: {info_e}")

        # 使用频道实体而不是dialog对象
        try:
            channel_entity = await client.get_entity(src_dialog.id)
            total_messages = await client.get_messages(channel_entity, limit=1)
        except Exception as entity_e:
            print(f"⚠️ 无法获取频道实体: {entity_e}")
            # 备用方案：直接使用dialog
            total_messages = await client.get_messages(src_dialog, limit=1)
        if total_messages:
            # 获取第一条消息的ID作为总数估算
            first_msg = total_messages[0]
            estimated_total = first_msg.id if first_msg.id else 0
            print(f"📈 源频道总消息数（估算）: {estimated_total} 条")
        else:
            print("📈 源频道总消息数: 0 条")
            estimated_total = 0
    except Exception as e:
        print(f"⚠️ 无法获取源频道消息总数: {e}")
        print(f"🔍 错误详情: 频道ID={src_dialog.id}, 错误类型={type(e).__name__}")
        estimated_total = 0

    # 检查频道可访问性
    is_accessible, reason = await check_channel_accessibility(src_dialog, dst_dialog)
    if not is_accessible:
        print(f"⚠️ 跳过频道 {get_channel_name(src_dialog)}: {reason}")
        return create_skipped_result(src_dialog, reason)

    last_forwarded_id = get_progress_for_channels(src_dialog.id, dst_dialog.id)
    if last_forwarded_id > 0:
        print(f"▶ 从消息 ID {last_forwarded_id} 之后继续转发")
        if estimated_total > 0:
            remaining_estimate = estimated_total - last_forwarded_id
            print(f"📊 预计剩余待转发: {remaining_estimate} 条消息")
    else:
        print("▶ 开始新的转发任务")
        if estimated_total > 0:
            print(f"📊 预计转发总数: {estimated_total} 条消息")

    # 显示历史转发统计
    stats = get_forward_stats(src_dialog.id, dst_dialog.id)
    if stats["total"] > 0:
        print(f"📊 历史转发统计: 总计 {stats['total']} 条 (单条: {stats['messages']}, 相册: {stats['groups']})")

    last_group = None
    group_buffer = []

    # 统计变量
    total_messages = 0
    forwarded_count = 0
    ad_filtered_count = 0
    content_filtered_count = 0
    duplicate_filtered_count = 0
    duplicate_albums_skipped = 0  # 完全重复的相册数量
    error_count = 0

    # 批量统计变量
    batch_size = batch_progress_interval  # 使用配置的间隔

    try:
        # 获取频道实体用于消息迭代
        try:
            channel_entity = await client.get_entity(src_dialog.id)
            message_iter = client.iter_messages(channel_entity, reverse=True, offset_id=last_forwarded_id,
                                                limit=max_messages)
        except Exception as entity_e:
            print(f"⚠️ 无法获取频道实体，使用dialog对象: {entity_e}")
            message_iter = client.iter_messages(src_dialog, reverse=True, offset_id=last_forwarded_id,
                                                limit=max_messages)

        async for msg in message_iter:
            total_messages += 1

            # 每处理一定数量的消息后显示批量统计
            if total_messages % batch_size == 0:
                print(
                    f"📈 进度: {total_messages} 条 | ✅ 转发:{forwarded_count} 🚫 广告:{ad_filtered_count} 🗑️ 内容:{content_filtered_count} 🔄 重复:{duplicate_filtered_count} 📚 跳过相册:{duplicate_albums_skipped} ❌ 错误:{error_count}")

            # 跳过服务消息
            if msg.message is None and not msg.media:
                # print(f"⚠️ 跳过服务消息: {msg.id}")
                add_filtered_record(src_dialog.id, dst_dialog.id, msg.id, "服务消息", "service")
                continue

            # 检查是否已经转发过
            if is_already_forwarded(src_dialog.id, dst_dialog.id, msg.id):
                # print(f"⏭️ 跳过已转发消息: {msg.id}")
                continue

            # 内容去重检查（基于媒体文件）
            if enable_content_deduplication:
                msg_hash = generate_message_hash(msg)
                if is_duplicate_content(msg_hash):
                    # 不再显示每条重复内容的详细信息
                    duplicate_filtered_count += 1
                    # 记录重复内容
                    source_info = f"{get_channel_name(src_dialog)}({src_dialog.id})"
                    add_duplicate_record(src_dialog.id, dst_dialog.id, msg.id, msg_hash, source_info)
                    # 仍然保存进度，避免重复检查
                    save_progress(src_dialog.id, dst_dialog.id, msg.id)
                    continue
                else:
                    # 添加到去重历史
                    source_info = f"{get_channel_name(src_dialog)}({src_dialog.id})"
                    add_to_dedup_history(msg_hash, source_info)

            # 内容过滤检查
            if msg.message:
                has_media = msg.media is not None

                # 广告过滤
                if enable_ad_filter and is_ad_message(msg.message, has_media):
                    reason = get_ad_reason(msg.message, has_media)
                    media_info = "有媒体" if has_media else "无媒体"
                    # print(f"🚫 过滤广告: {msg.id} ({media_info}) - {reason}")
                    ad_filtered_count += 1
                    # 记录过滤原因
                    add_filtered_record(src_dialog.id, dst_dialog.id, msg.id, reason, "ad")
                    # 仍然保存进度，避免重复检查
                    save_progress(src_dialog.id, dst_dialog.id, msg.id)
                    continue

                # 内容质量过滤
                if enable_content_filter and is_meaningless_message(msg.message, has_media):
                    reason = get_content_filter_reason(msg.message, has_media)
                    media_info = "有媒体" if has_media else "无媒体"
                    # print(f"🗑️ 过滤无意义内容: {msg.id} ({media_info}) - {reason}")
                    content_filtered_count += 1
                    # 记录过滤原因
                    add_filtered_record(src_dialog.id, dst_dialog.id, msg.id, reason, "content")
                    # 仍然保存进度，避免重复检查
                    save_progress(src_dialog.id, dst_dialog.id, msg.id)
                    continue

            # 处理相册
            if msg.grouped_id:
                if last_group is None:
                    last_group = msg.grouped_id
                if msg.grouped_id == last_group:
                    group_buffer.append(msg)
                    continue
                else:
                    if group_buffer:
                        # 使用统一的相册处理函数
                        forwarded, errors, skipped = await process_album_group(group_buffer, src_dialog, dst_dialog)
                        forwarded_count += forwarded
                        error_count += errors
                        duplicate_albums_skipped += skipped

                        if forwarded > 0:
                            save_progress(src_dialog.id, dst_dialog.id, group_buffer[-1].id)

                            # 检查是否需要轮换账号
                            if should_rotate_account():
                                if await switch_to_accessible_account(src_dialog, dst_dialog):
                                    await asyncio.sleep(account_delay)
                                reset_account_counter()

                            await asyncio.sleep(delay_group)
                        elif errors > 0:
                            # 检查是否是受保护聊天错误，如果是则立即跳过频道
                            print(f"🚫 检测到受保护的聊天，跳过频道 {get_channel_name(src_dialog)}")
                            return create_skipped_result(src_dialog, PROTECTED_CHAT_REASON, total_messages,
                                                         forwarded_count, ad_filtered_count, content_filtered_count,
                                                         duplicate_filtered_count, error_count)
                        else:
                            save_progress(src_dialog.id, dst_dialog.id, group_buffer[-1].id)
                    group_buffer = [msg]
                    last_group = msg.grouped_id
            else:
                if group_buffer:
                    # 使用统一的相册处理函数
                    forwarded, errors, skipped = await process_album_group(group_buffer, src_dialog, dst_dialog)
                    forwarded_count += forwarded
                    error_count += errors
                    duplicate_albums_skipped += skipped

                    if forwarded > 0:
                        save_progress(src_dialog.id, dst_dialog.id, group_buffer[-1].id)

                        # 检查是否需要轮换账号
                        if should_rotate_account():
                            if await switch_to_accessible_account(src_dialog, dst_dialog):
                                await asyncio.sleep(account_delay)
                            reset_account_counter()

                        await asyncio.sleep(delay_group)
                    elif errors > 0:
                        # 检查是否是受保护聊天错误，如果是则立即跳过频道
                        print(f"🚫 检测到受保护的聊天，跳过频道 {get_channel_name(src_dialog)}")
                        return create_skipped_result(src_dialog, PROTECTED_CHAT_REASON, total_messages, forwarded_count,
                                                     ad_filtered_count, content_filtered_count,
                                                     duplicate_filtered_count, error_count)
                    else:
                        save_progress(src_dialog.id, dst_dialog.id, group_buffer[-1].id)
                    group_buffer = []

                success, error_type = await forward_message_safe(dst_dialog, msg)
                if success:
                    # 只在批量统计时显示成功信息，减少冗余日志
                    if total_messages % batch_size == 0:
                        print(f"✅ 转发成功: {msg.id}")
                    save_progress(src_dialog.id, dst_dialog.id, msg.id)
                    # 记录转发历史
                    add_forward_record(src_dialog.id, dst_dialog.id, msg.id, "single")
                    forwarded_count += 1

                    # 检查是否需要轮换账号
                    if should_rotate_account():
                        if await switch_to_accessible_account(src_dialog, dst_dialog):
                            await asyncio.sleep(account_delay)
                        reset_account_counter()

                    await asyncio.sleep(delay_single)
                else:
                    error_count += 1
                    # 检查是否是受保护聊天错误，如果是则立即跳过频道
                    if error_type == "protected_chat":
                        print(f"🚫 检测到受保护的聊天，跳过频道 {get_channel_name(src_dialog)}")
                        return create_skipped_result(src_dialog, PROTECTED_CHAT_REASON, total_messages, forwarded_count,
                                                     ad_filtered_count, content_filtered_count,
                                                     duplicate_filtered_count, error_count)

        # 收尾
        if group_buffer:
            # 使用统一的相册处理函数
            forwarded, errors, skipped = await process_album_group(group_buffer, src_dialog, dst_dialog)
            forwarded_count += forwarded
            error_count += errors
            duplicate_albums_skipped += skipped

            if forwarded > 0:
                save_progress(src_dialog.id, dst_dialog.id, group_buffer[-1].id)
            elif errors > 0:
                # 检查是否是受保护聊天错误，如果是则立即跳过频道
                print(f"🚫 检测到受保护的聊天，跳过频道 {get_channel_name(src_dialog)}")
                return create_skipped_result(src_dialog, "受保护的聊天", total_messages, forwarded_count, ad_filtered_count,
                                             content_filtered_count, duplicate_filtered_count, error_count)
            else:
                save_progress(src_dialog.id, dst_dialog.id, group_buffer[-1].id)

    except Exception as e:
        print(f"❌ 处理频道 {get_channel_name(src_dialog)} 时发生错误: {e}")
        error_count += 1

    return create_completed_result(src_dialog, total_messages, forwarded_count,
                                   ad_filtered_count, content_filtered_count,
                                   duplicate_filtered_count, duplicate_albums_skipped, error_count)


# ---------- 主逻辑 ----------
async def main():
    global clients

    if recover_forward_history():
        pass
    else:
        pass

    # 清空账号频道访问权限缓存
    clear_account_channel_access_cache()

    # 检查账号配置
    if not clients:
        print("❌ 没有可用的账号！请检查账号配置。")
        return

    # 启动所有客户端
    print(f"🚀 启动 {len(clients)} 个账号...")
    for client_data in clients:
        try:
            await client_data["client"].start()
            print(f"✅ {client_data['account']['session_name']} 启动成功")
        except Exception as e:
            print(f"❌ {client_data['account']['session_name']} 启动失败: {e}")
            client_data["enabled"] = False

    # 过滤掉启动失败的账号
    clients = [c for c in clients if c["enabled"]]

    if not clients:
        print("❌ 没有可用的账号！")
        return

    # 显示账号信息
    current_account = get_current_account_info()
    print(f"📱 当前使用账号: {current_account['session_name']}")

    # 检查是否需要自动导出频道信息
    if auto_export_channels:
        print(f"\n{'=' * 60}")
        print("🚀 自动导出频道信息...")
        print(f"{'=' * 60}")
        await export_all_accounts_channels()
        print(f"\n{'=' * 60}")
        print("✅ 频道信息导出完成，程序退出")
        print(f"{'=' * 60}")
        return

    # 获取客户端
    client = get_current_client()

    # 检查是否有预设频道配置
    src_dialogs = []
    dst_dialog = None

    # 验证预设频道
    if preset_source_channels or preset_target_channel:
        validated_sources, validated_target = await validate_preset_channels(
            client, preset_source_channels, preset_target_channel
        )

        if validated_sources:
            src_dialogs = validated_sources
            print(f"\n✅ 使用预设源频道: {len(src_dialogs)} 个")
            for i, dialog in enumerate(src_dialogs, 1):
                print(f"  {i}. {get_channel_name(dialog)} ({normalize_channel_id(dialog.id)})")

        if validated_target:
            dst_dialog = validated_target
            print(f"\n✅ 使用预设目标频道: {get_channel_name(dst_dialog)} ({normalize_channel_id(dst_dialog.id)})")

    # 如果没有预设源频道，进行手动选择
    if not src_dialogs:
        src_dialogs = await choose_multiple_dialogs("源频道/群组")

        if not src_dialogs:
            print("❌ 没有选择任何源频道，程序退出。")
            return

    # 如果没有预设目标频道，进行手动选择
    if not dst_dialog:
        dst_dialog = await choose_dialog("目标频道/群组")
        print(f"\n目标: {get_channel_name(dst_dialog)} ({normalize_channel_id(dst_dialog.id)})")

    # 扫描目标频道，预加载去重历史
    if enable_content_deduplication:
        print(f"\n💡 提示：将先扫描目标频道，避免转发重复内容")

        # 检查是否需要重新扫描
        last_message_id, previous_scanned = get_scan_progress(dst_dialog.id)
        choice = "1"  # 默认选择增量扫描
        force_rescan = False

        if last_message_id:
            print(f"📊 检测到之前的扫描进度：已扫描 {previous_scanned} 条消息，最后消息ID: {last_message_id}")
            print(f"💡 选择扫描模式：")
            print(f"  1. 增量扫描 - 只扫描新消息")
            print(f"  2. 重新扫描 - 重新扫描所有消息")
            print(f"  3. 跳过扫描 - 使用现有去重历史")

            while True:
                try:
                    choice = input("请选择扫描模式 (1/2/3): ").strip()
                    if choice == "1":
                        force_rescan = False
                        break
                    elif choice == "2":
                        force_rescan = True
                        break
                    elif choice == "3":
                        print("⏭️ 跳过扫描，使用现有去重历史")
                        break
                    else:
                        print("❌ 输入无效，请输入 1、2 或 3")
                except KeyboardInterrupt:
                    print("\n❌ 用户取消操作")
                    return

        if choice != "3":  # 如果不是跳过扫描
            # 设置目标频道信息
            set_target_channel_info(get_channel_name(dst_dialog), dst_dialog.id)
            scan_count = await scan_target_channel(dst_dialog, scan_limit=target_channel_scan_limit,
                                                   force_rescan=force_rescan)
            if scan_count > 0:
                print(f"🎯 目标频道扫描完成，已预加载 {scan_count} 条消息到去重历史")
        print()

    # 显示选择的源频道
    print(f"\n📋 已选择 {len(src_dialogs)} 个源频道:")
    for i, src_dialog in enumerate(src_dialogs, 1):
        print(f"  {i}. {get_channel_name(src_dialog)} ({normalize_channel_id(src_dialog.id)})")

    # 开始处理每个源频道
    all_results = []
    total_all_messages = 0
    total_all_forwarded = 0
    total_all_ad_filtered = 0
    total_all_content_filtered = 0
    total_all_duplicate_filtered = 0
    total_all_duplicate_albums_skipped = 0
    total_all_errors = 0

    for i, src_dialog in enumerate(src_dialogs, 1):
        print(f"\n{'=' * 60}")
        print(f"🔄 处理第 {i}/{len(src_dialogs)} 个源频道")
        print(f"{'=' * 60}")

        result = await forward_from_single_source(src_dialog, dst_dialog)
        all_results.append(result)

        # 累计统计
        total_all_messages += result["total_messages"]
        total_all_forwarded += result["forwarded_count"]
        total_all_ad_filtered += result["ad_filtered_count"]
        total_all_content_filtered += result["content_filtered_count"]
        total_all_duplicate_filtered += result["duplicate_filtered_count"]
        total_all_duplicate_albums_skipped += result.get("duplicate_albums_skipped", 0)
        total_all_errors += result["error_count"]

        # 显示当前频道的结果
        if result["status"] == "skipped":
            pass
        else:
            print(f"  ✅ 状态: 完成")
            print(f"  📝 总消息数: {result['total_messages']}")
            print(f"  ✅ 成功转发: {result['forwarded_count']}")

            if result["total_messages"] > 0:
                success_rate = (result["forwarded_count"] / result["total_messages"] * 100)
                print(f"  📈 成功率: {success_rate:.1f}%")

    # 显示总体统计信息
    print(f"\n{'=' * 60}")
    print("📊 总体转发统计:")
    print(f"{'=' * 60}")
    print(f"处理频道数: {len(src_dialogs)}")
    print(f"总消息数: {total_all_messages}")
    print(f"成功转发: {total_all_forwarded}")

    total_all_filtered = total_all_ad_filtered + total_all_content_filtered + total_all_duplicate_filtered
    if total_all_messages > 0:
        ad_rate = (total_all_ad_filtered / total_all_messages * 100)
        content_rate = (total_all_content_filtered / total_all_messages * 100)
        duplicate_rate = (total_all_duplicate_filtered / total_all_messages * 100)
        total_rate = (total_all_filtered / total_all_messages * 100)
        success_rate = (total_all_forwarded / total_all_messages * 100)
        print(f"广告过滤率: {ad_rate:.1f}%")
        print(f"内容过滤率: {content_rate:.1f}%")
        print(f"重复过滤率: {duplicate_rate:.1f}%")
        print(f"总过滤率: {total_rate:.1f}%")
        print(f"成功率: {success_rate:.1f}%")

    # 显示每个频道的详细结果
    print(f"\n📋 各频道详细结果:")
    for i, result in enumerate(all_results, 1):
        status_icon = "⚠️" if result["status"] == "skipped" else "✅"
        print(f"  {i}. {status_icon} {result['source_name']}")
        if result["status"] == "skipped":
            print(f"     跳过原因: {result['reason']}")
        else:
            print(
                f"     转发: {result['forwarded_count']} | 广告过滤: {result['ad_filtered_count']} | 内容过滤: {result['content_filtered_count']} | 重复过滤: {result['duplicate_filtered_count']} | 跳过相册: {result.get('duplicate_albums_skipped', 0)} | 错误: {result['error_count']}")

    # 显示全局去重统计
    if enable_content_deduplication:
        dedup_stats = get_dedup_stats()
        print(f"\n🔄 全局去重统计:")
        if dedup_stats['target_channel']:
            print(f"  目标频道: {dedup_stats['target_channel']}")
        print(f"  已记录内容: {dedup_stats['total_unique']} 条")

    # 显示账号统计
    if len(clients) > 1:
        print(f"\n📱 账号使用统计:")
        account_stats = get_account_stats()
        for stat in account_stats:
            status = "当前" if stat["is_current"] else "已用"
            print(f"  {stat['session_name']}: {stat['forward_count']} 条 ({status})")

    print(f"\n{'=' * 60}")
    print("🎉 所有频道处理完成")
    print(f"{'=' * 60}")


# ---------- 独立导出脚本 ----------
async def export_only():
    """仅执行导出功能的独立脚本"""
    if not clients:
        print("❌ 没有可用的账号！请检查账号配置。")
        return

    print("🚀 频道信息导出工具")
    print("=" * 60)

    await export_all_accounts_channels()


# ---------- 运行 ----------
if __name__ == "__main__":
    if not clients:
        print("❌ 没有可用的账号！请检查账号配置。")
        exit(1)

    # 检查命令行参数
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "export":
        # 独立导出模式
        main_client = clients[0]["client"]
        with main_client:
            main_client.loop.run_until_complete(export_only())
    else:
        # 正常模式
        main_client = clients[0]["client"]
        with main_client:
            main_client.loop.run_until_complete(main())
