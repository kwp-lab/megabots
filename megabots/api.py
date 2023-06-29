import os
from megabots import bot
from megabots.utils import create_api

from lcserve import serving

cur_dir = os.path.dirname(os.path.abspath(__file__))
index_dir = os.path.join(cur_dir, "..", "examples", "files")

INDEX_FILE = "index.pkl"
INDEX_FILE_EXISTS = os.path.exists(INDEX_FILE)

qnabot = bot(
    "qna-over-docs",
    index= INDEX_FILE if INDEX_FILE_EXISTS else "apitable",
    temperature=0,
    verbose=True
)


@serving
def ask(question: str) -> str:
    return qnabot.ask(question)

@serving
def suggestions(question: str) -> list:
    return qnabot.suggestions(question)

@serving
def explore(question: str) -> list:
    result = [
        "青铜/白银/企业这些空间版本有什么不同？",
        "我要如何取消冻结列 ？",
        "青铜版本有空间站人数限制吗？",
        "仪表盘能单独分享吗？",
        "空间站的席位是什么？"
    ]
    return result


app = create_api(qnabot)
