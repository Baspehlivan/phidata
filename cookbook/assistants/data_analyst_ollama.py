import json

from phi.llm.ollama import Ollama
from phi.assistant.duckdb import DuckDbAssistant

data_analyst = DuckDbAssistant(
    llm=Ollama(model="phi3"),
    semantic_model=json.dumps(
        {
            "tables": [
                {
                    "name": "movies",
                    "description": "Contains information about movies from IMDB.",
                    "path": "/Users/pdagli/Downloads/IMDB-Movie-Data.csv",
                }
            ]
        }
    ),
)

data_analyst.print_response("What is the average rating of movies? Show me the SQL.", markdown=True)
data_analyst.print_response("Show me a histogram of ratings. Choose a bucket size", markdown=True)
