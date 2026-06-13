from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from parser import *
from extractor import *
from validator import validate_output


class State(TypedDict):

    file_path:str

    docling:dict
    llama:dict

    text:str

    document_type: str

    extracted:dict

    final:dict

# -------- nodes ----------


def docling_node(state):

    return {
        "docling":
        parse_docling(
            state["file_path"]
        )
    }



def llama_node(state):

    return {
        "llama":
        parse_llamaparse(
            state["file_path"]
        )
    }



def merge_node(state):

    return {
        "text":
        merge_parser_output(
            state["docling"],
            state["llama"]
        )
    }



def classify_node(state):

    return {
        "document_type":
        "invoice"
    }



def rule_node(state):

    result = rule_extract(
        state["text"]
    )

    return {
        "extracted":result
    }




def decide(state):

    conf = state["extracted"]["confidence"]

    print(f"🔀 DECISION NODE: confidence={conf}")

    if conf < 0.5:
        print(f"   → Routing to LLM (low confidence)")
        return "llm"

    print(f"   → Routing to VALIDATE (high confidence)")
    return "validate"




def llm_node(state):

    print("⚡ LLM NODE CALLED")
    print(f"   Text length: {len(state['text'])} chars")

    data = llm_extract(
        state["text"]
    )

    print(f"   LLM Result: {data}")

    return {
        "extracted":
        {
            "data":data,
            "confidence":0.9
        }
    }




def validate_node(state):

    data = state["extracted"]["data"]

    data["document_type"]="invoice"

    data["confidence"] = (
        state["extracted"]["confidence"]
    )

    data["extraction_method"]="rule/llm"


    return {
        "final":
        validate_output(data)
    }



# -------- graph ----------


graph = StateGraph(State)


graph.add_node(
    "docling",
    docling_node
)

graph.add_node(
    "llama",
    llama_node
)

graph.add_node(
    "merge",
    merge_node
)

graph.add_node(
    "classify",
    classify_node
)

graph.add_node(
    "rule",
    rule_node
)

graph.add_node(
    "llm",
    llm_node
)

graph.add_node(
    "validate",
    validate_node
)




graph.add_edge(
    START,
    "docling"
)

graph.add_edge(
    START,
    "llama"
)


graph.add_edge(
    "docling",
    "merge"
)

graph.add_edge(
    "llama",
    "merge"
)


graph.add_edge(
    "merge",
    "classify"
)


graph.add_edge(
    "classify",
    "rule"
)



graph.add_conditional_edges(
    "rule",
    decide,
    {
        "llm":"llm",
        "validate":"validate"
    }
)



graph.add_edge(
    "llm",
    "validate"
)


graph.add_edge(
    "validate",
    END
)


app = graph.compile()