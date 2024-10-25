import requests
import plugins
from plugins import *
from bridge.context import ContextType
from urllib.parse import unquote
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL_VVHAN = "https://api.vvhan.com/api/" #https://api.vvhan.com/

@plugins.register(name="hot_trends",
                  desc="热搜插件",
                  version="1.0",
                  author="masterke",
                  desire_priority=100)
class hot_trends(Plugin):
    content = None
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"目前支持的热搜类型有: \n微博热搜、知乎热搜、哔哩哔哩热搜、贴吧热搜、抖音热搜、IT资讯"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        if self.content in ["微博热搜","知乎热搜","哔哩哔哩热搜","贴吧热搜","抖音热搜","IT资讯"]:
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = self.hot_trends()
            if result != None:
                reply.type = ReplyType.TEXT
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def hot_trends(self):
        # 热榜类型         
        match(self.content):
            case "微博热搜": hot_trends_type = "wbHot"
            case "知乎热搜": hot_trends_type = "zhihuHot"
            case "哔哩哔哩热搜": hot_trends_type = "bili"
            case "贴吧热搜": hot_trends_type = "baiduRY"
            case "抖音热搜": hot_trends_type = "douyinHot"
            case "IT资讯":hot_trends_type = "itNews"

        url = BASE_URL_VVHAN + "hotlist?type=" + hot_trends_type
        try:
            response = requests.get(url)
            if response.status_code == 200:
                json_data = response.json()
                print(json_data)
                if isinstance(json_data, dict) and json_data['success'] == True:
                    result = f"🚀更新时间：{json_data['update_time']}"
                    topics = json_data['data']
                    for i, topic in enumerate(topics[:10], 1):
                        hot = topic.get('hot', '无热度参数, 0')
                        formatted_str = f"\n{i}. {topic['title']} ({hot} 浏览)\nURL: {topic['url']}"
                        result += formatted_str
                    logger.info(result)
                    return result
                else:
                    logger.error(f"热搜接口返回数据异常:{json_data}")
            else:
                logger.error(f"热搜接口返回状态码错误:{response.status_code}")
        except Exception as e:
            logger.error(f"热搜接口抛出异常:{e}")
                
        logger.error("所有接口都挂了,无法获取")
        return None
