"""
This file is an example of what you can build with 🤖Megabots.
It is hosted here: https://huggingface.co/spaces/momegas/megabots

"""

import megabots
from megabots.bot import bot
from megabots.utils import create_interface
import os

prompt = """
Act the role of customer support. You should observe the following rules: If the user asks a question in Chinese, answer it in Chinese. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use the following pieces of context to answer the question at the end.

{context}

Question: {question}
Helpful Answer:
"""

INDEX_FILE = "index.pkl"
INDEX_FILE_EXISTS = os.path.exists(INDEX_FILE)

qnabot = bot(
    "qna-over-docs",
    index= INDEX_FILE if INDEX_FILE_EXISTS else "apitable",
    prompt=prompt,
    temperature=0.2,
    verbose=True
)


if not INDEX_FILE_EXISTS:
    # Save the index to save costs (GPT is used to create the index)
    qnabot.save_index(INDEX_FILE)


text = """
## Vika维格云 - AI客服助手

You can ask this bot anything about vikadata. Here are some examples:
- 维格表怎么收费？
- 支持私有化部署吗？
- 维格表跟 Excel 有什么不同？
  - What’s the difference between 维格表 and Excel
- 维格表可以与企微打通消息通知吗？
- 怎样合并单元格？
- 支持导入和导出Excel吗?
- 你们老板是谁？
- 数据误删除了，如何找回？
"""

iface = create_interface(qnabot, text)
iface.launch(show_error=True)
