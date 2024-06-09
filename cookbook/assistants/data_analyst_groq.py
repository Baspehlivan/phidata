import json
import os
os.environ['GROQ_API_KEY'] = "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"

from phi.llm.groq import Groq
from phi.assistant.duckdb import DuckDbAssistant

data_analyst = DuckDbAssistant(
    llm=Groq(model="llama3-8b-8192"),
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
