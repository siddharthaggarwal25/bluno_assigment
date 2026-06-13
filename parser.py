import os
from docling.document_converter import DocumentConverter
from llama_cloud import LlamaCloud

client = LlamaCloud(api_key="llx-dh2z0Qj8w4FKN6BJ4Xqdamqo2S160PhV7nAAHVZEeS2j2aM3")
converter = DocumentConverter()

def parse_docling(path: str):

    try:

        result = converter.convert(path)

        if result.document:

            markdown_output = (
                result.document.export_to_markdown()
            )


            print("Docling markdown output:", markdown_output)

            return {
                "source": "docling",
                "text": markdown_output,
                "error": None
            }


        else:

            return {
                "source": "docling",
                "text": "",
                "error": "Failed to extract document"
            }



    except Exception as e:

        return {
            "source": "docling",
            "text": "",
            "error": str(e)
        }
    

def parse_llamaparse(path: str):

    try:

        # upload pdf
        file_obj = client.files.create(
            file=path,
            purpose="parse"
        )


        # parse pdf
        result = client.parsing.parse(
            file_id=file_obj.id,

            tier="agentic",

            version="latest",

            expand=[
                "markdown_full",
                "text_full"
            ]
        )


        markdown_output = (
            result.markdown_full
            or ""
        )

        print("LlamaParse markdown output:", markdown_output)


        return {
            "source": "llamaparse",
            "text": markdown_output,
            "error": None
        }
        



    except Exception as e:


        return {
            "source": "llamaparse",
            "text": "",
            "error": str(e)
        }


def merge_parser_output(a,b):

    text = (
        a["text"]
        + "\n"
        + b["text"]
    )

    return text