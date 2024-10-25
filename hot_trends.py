import requests
import plugins
from plugins import *
from bridge.context import ContextType
from urllib.parse import quote, unquote
from bridge.reply import Reply, ReplyType
from common.log import logger

@plugins.register(name="hot_trends",
                  desc="微博热搜",
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
        help_text = f"发送【微博热搜】"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        if self.content in ["微博热搜"]:
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            config_path = os.path.join(os.path.dirname(__file__),"config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                logger.error(f"请先配置{config_path}文件")
                return

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
        url = "https://v2.alapi.cn/api/new/wbtop"
        payload = {'num':"10",'token': self.config_data['alapi_token']}
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                json_data = response.json()
                print(json_data)
                if isinstance(json_data, dict) and json_data['msg'] == "success":
                    print(json_data)
                    reply_message = ""
                    for item in json_data['data']:
                        title = item['hot_word']
                        url = quote(item['url'])
                        # 将标题和链接添加到字符串中，之间加上一些分隔符，如换行符或空格
                        reply_message += f"【{title}】\n{url}\n\n"
                    return reply_message
                else:
                    logger.error(f"hot_trends返回异常:{json_data}")
            else:
                logger.error(f"hot_trends状态码错误:{response.status_code}")
        except Exception as e:
            logger.error(f"hot_trends抛出异常:{e}")
        return None
