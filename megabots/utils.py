import gradio as gr
from fastapi import FastAPI
from megabots.bot import Bot
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel


def _custom_openapi(app: FastAPI, version: str):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="🤖 Megabots API",
        version=version,
        description="Use this API to interact with the bot.",
        routes=app.routes,
    )
    return openapi_schema


class Answer(BaseModel):
    text: str


def create_api(bot: Bot, version: str = "0.0.1"):
    app = FastAPI()

    @app.get(
        "/v1/bot/ask/{question}",
        tags=["Bot"],
        summary="Ask bot",
        description="Send question to the bot.",
        responses={200: {"description": "Bot answer"}},
        response_model=Answer,
    )
    async def ask(question: str) -> Answer:
        answer = bot.ask(question)
        return Answer(text=answer)

    app.openapi_schema = _custom_openapi(app, version)

    return app


def create_interface(bot_instance: Bot, markdown: str = ""):
    with gr.Blocks() as interface:
        gr.Markdown(markdown)
        
        with gr.Row():
            with gr.Column():
                chatbot = gr.Chatbot(label="vika维格云客服助手", elem_id="chatbot").style(height=450)
                msg = gr.Textbox(
                    show_label=False,
                    placeholder="Enter text and press enter",
                ).style(container=False)

            output = gr.JSON(label="语料")

        def user(user_message, history):
            return "", history + [[user_message, None]]

        def bot(history):
            print("im here")
            response = bot_instance.ask(history[-1][0])
            history[-1][1] = response
            return history
        
        def print_dataset(dataset):
            return bot_instance.similarity_search_results

        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        ).then(print_dataset, output, output)
        

    return interface
