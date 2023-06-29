"""APITable Datasheet loader for LangChain"""
import requests
from typing import Any, List

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader


def _stringify_value(val: Any) -> str:
    if isinstance(val, str):
        return val
    elif isinstance(val, dict):
        return "\n" + _stringify_dict(val)
    elif isinstance(val, list):
        return "\n".join(_stringify_value(v) for v in val)
    else:
        return str(val)


def _stringify_dict(data: dict) -> str:
    text = ""
    for key, value in data.items():
        text += key + ": " + _stringify_value(data[key]) + "\n"
    return text


class APITableDatasheetLoader(BaseLoader):
    """Loader that loads APITable records with JSON Format."""

    def __init__(
        self,
        access_token: str,
        datasheet_id: str,
        view_id: str,
        cell_format: str | None = "string",
        hostname: str | None = "apitable.com",
        verbose: bool | None = False
    ):
        """Initialize with access token, datasheet_id, and viewId."""
        self.access_token = access_token
        self.datasheet_id = datasheet_id
        self.view_id = view_id
        self.cell_format = cell_format
        self.hostname = hostname
        self.verbose = verbose # Print all records to stdout if True

    def _construct_api_url(self, page_num: int) -> str:
        api_url = (
            "https://api.%s/fusion/v1/datasheets/%s/records?viewId=%s&fieldKey=name&cellFormat=%s&pageNum=%d"
            % (
                self.hostname,
                self.datasheet_id,
                self.view_id,
                self.cell_format,
                page_num
            )
        )
        return api_url

    def _get_records(self) -> Any:
        """Get records from APITable REST API."""
        all_records = []  # List to store all retrieved records
        headers = {"Authorization": "Bearer " + self.access_token}
        page_num = 1

        while True:
            response = requests.get(self._construct_api_url(page_num), headers=headers)
            data = response.json()

            if (response.status_code != 200) or (not data['success']):
                print("Request error", data)
                break
            
            records = data['data']['records']
            totals = data['data']['total']

            all_records.extend(records)  # Add retrieved records to the list
            
            total_of_retrieved = len(all_records)
            if total_of_retrieved >= totals:
                # We've reached the end of the records, break out of the loop
                break

            page_num += 1 # Move to the next page
            print("retrieved %s rows of records..." % (total_of_retrieved))

        print("Successfully retrieved %s rows of records" % (total_of_retrieved))

        if self.verbose:
            print("Printing all records:")
            for i, record in enumerate(all_records):
                print(i, record)

        return all_records

    def load(self) -> List[Document]:
        """Load records"""
        docs = []
        records = self._get_records()
        
        for i, record in enumerate(records):
            content = _stringify_dict(record["fields"])
            source = f"https://{self.hostname}/workbench/{self.datasheet_id}/{self.view_id}/{record['recordId']}"
            metadata = {"source": source, "recordId": record["recordId"]}
            doc = Document(page_content=content, metadata=metadata)
            docs.append(doc)

        return docs
