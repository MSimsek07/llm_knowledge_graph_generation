from fastapi import FastAPI, HTTPException
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from pydantic import BaseModel
from py2neo import Graph
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_community.tools.google_scholar import GoogleScholarQueryRun
from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
import markdown

load_dotenv()

trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "text-to-graph"}))
)
tracer_provider = trace.get_tracer_provider()

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

tracer_provider.add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

app = FastAPI()

FastAPIInstrumentor().instrument_app(app)

class ResearchInput(BaseModel):
    input_text: str

def load_env_variables():
    load_dotenv()
    required_variables = ["OPENAI_API_KEY", "LANGCHAIN_API_KEY", "NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]

    for var in required_variables:
        if not os.getenv(var):
            raise ValueError(f"Environment variable {var} is not set")
    
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["NEO4J_URI"] = "neo4j+s://b01fd59b.databases.neo4j.io"
    os.environ["NEO4J_USERNAME"] = "neo4j"
    os.environ["NEO4J_PASSWORD"] = "KRLbU9N25h1pAId7oceVXrk8vdA2DRCO5ZE2C0lbk7s"

def make_research(input_text: str):
    tool = GoogleScholarQueryRun(api_wrapper=GoogleScholarAPIWrapper(top_k_results=20))
    response = markdown.markdown(tool.run(f"{input_text}"))
    return response

def generate_research_report(response):
    template = """
    You are a well-known writer, and you are going to reply with a well-detailed answer according to the given input about each research paper.
    Just return a paragraph that includes information about all the research papers in the input in a well-detailed way.
    Make sure that you mention the given details for each paper like; paper's title, authors, publication date, and the abstract.
    You must mention the research papers one by one.
    At the end, return all of them in a paragraph in a well-detailed way.
    Response: {question}
    Answer: Let's think step by step.
    """
    prompt = PromptTemplate.from_template(template)
    llm = OpenAI(temperature=0.1, max_tokens=2000)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    question = response
    text = llm_chain.run(question)
    return text

def create_graph():
    return Neo4jGraph()

def create_llm():
    return ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")

def create_llm_transformer(llm):
    system_prompt = """
    # Knowledge Graph Guidelines for GPT-3.5-Turbo-0125
    ## 1. Introduction
    You're an advanced algorithm crafted to extract structured information for constructing knowledge graphs.
    Strive for maximal information extraction from the provided text while upholding accuracy. Avoid introducing
    any extraneous details not explicitly stated.
    - Nodes signify entities and concepts.
    - The primary objective is to ensure simplicity and clarity in the knowledge graph, facilitating accessibility
    for a wide audience.
    ## 2. Node Labeling
    - Consistency: Utilize available node label types consistently.
    Opt for basic or fundamental node labels.
    - For instance, designate any person entity as 'person'. Refrain from using overly specific terms like
    'mathematician' or 'scientist'.
     - Node IDs: Never employ integers as node IDs. Instead, utilize names or human-readable identifiers
    presented in the text.
    - Relationships denote connections among entities or concepts.
    Ensure uniformity and generality in relationship types during knowledge graph construction. Rather than
    utilizing specific and transient relationship types such as 'BECAME_PROFESSOR', opt for more general and
    timeless relationships like 'PROFESSOR'. Emphasize the use of general and timeless relationship types!
    ## 3. Coreference Resolution
    - Maintain Entity Consistency: Consistency is paramount when extracting entities.
    In cases where an entity like "John Doe" is mentioned multiple times but referred to using different names
    or pronouns (e.g., "Joe", "he"), always employ the most comprehensive identifier for that entity throughout
    the knowledge graph. For instance, utilize "John Doe" as the entity ID.
    Remember, coherence and comprehensibility are key aspects of the knowledge graph, underscoring the
    importance of consistency in entity references.
    ## 4. Adherence to Guidelines
    Strictly adhere to the outlined guidelines. Failure to comply will result in termination of the process.
    """
    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), 
         ("human", "Tip: Make sure to answer in the correct format and do not include any explanations. Use the given format to extract information from the following input: {input}")]
    )
    return LLMGraphTransformer(llm=llm, prompt=prompt)

def create_document(text):
    if not text:
        raise ValueError("Text cannot be empty")
    return [Document(page_content=text)]

def convert_to_graph_documents(llm_transformer, documents):
    return llm_transformer.convert_to_graph_documents(documents)

def add_graph_documents(graph, graph_documents):
    graph.add_graph_documents(graph_documents)

def clear_graph_db():
    graph = Graph(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")))
    graph.run("MATCH (n) DETACH DELETE n")

@app.post("/generate_graph")
def generate_graph(data: ResearchInput):
    try:
        load_env_variables()
        graph = create_graph()
        llm = create_llm()
        llm_transformer = create_llm_transformer(llm)

        research_response = make_research(data.input_text)
        research_report = generate_research_report(research_response)
        documents = create_document(research_report)
        graph_documents = convert_to_graph_documents(llm_transformer, documents)
        clear_graph_db()
        add_graph_documents(graph, graph_documents)

        return {
            "research_response": research_response,
            "research_report": research_report,
            "documents": [doc.page_content for doc in documents],
            "graph_documents": [str(doc) for doc in graph_documents]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
