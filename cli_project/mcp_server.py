from mcp.server.fastmcp import FastMCP

from pydantic import Field
mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}



@mcp.tool(name="read_doc_contents", description="Read the contents of a document and return it as a string")
def read_documents(doc_id: str = Field(description="Id of the document to read")) -> str:
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found.")
    return docs[doc_id]

@mcp.tool(name="edit_document", description="Edit a document by replacing a string in the documents contents")
def edit_document(doc_id: str = Field(description="Id of the document to edit"),
                  old_string: str = Field(description="The string to replace"),
                  new_string: str = Field(description="The string to replace with")) -> str:
    """Edit a document by replacing old_string with new_string."""
    if doc_id not in docs:
        raise ValueError(f"Document {doc_id} not found.")

    if old_string not in docs[doc_id]:
        raise ValueError(f"String '{old_string}' not found in document {doc_id}.")

    docs[doc_id] = docs[doc_id].replace(old_string, new_string)
    result = docs[doc_id]

    # Ensure we always return a string
    return result if result is not None else ""

    


# TODO: Write a resource to return all doc id's
# TODO: Write a resource to return the contents of a particular doc
# TODO: Write a prompt to rewrite a doc in markdown format
# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
