from qdrant_client import QdrantClient,models

import logging
from typing import List

class QdrantDBProvider:

    def __init__(self, url: str, api_key: str):
        self.client = None
        self.url = url
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
     


    def connect(self):
        self.client = QdrantClient(url=self.url, api_key=self.api_key)



    def disconnect(self):
       self.client = None



    def is_collection_existed(self, collection_name: str) -> bool:   
        return self.client.collection_exists(collection_name=collection_name)
    


    def list_all_collections(self) -> List:
        return self.client.get_collections()
    


    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    


    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        else:
            self.logger.warning(f"Collection {collection_name} does not exist.")   



    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):    
        if self.is_collection_existed(collection_name):
            if do_reset:
                self.delete_collection(collection_name)
            else:
                self.logger.warning(f"Collection {collection_name} already exists. Use do_reset=True to reset it.")
                return True
        if not self.is_collection_existed(collection_name):
            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, 
                    distance=models.Distance.COSINE,
                ),
            )

    def ensure_text_index(self, collection_name: str):
        pass
    


    def insert_one(self, collection_name: str, text: str, record_id: str, vector: list, metadata: dict):

        if not self.is_collection_existed(collection_name):
            self.logger.warning(f"Collection {collection_name} does not exist. Please create it first.")
            return False
        try:
            _ =self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:    
            self.logger.error(f"Error while inserting batch: {e}")
            return False
        

    def insert_many(self, collection_name: str, texts: List, vectors: List, 
                    record_ids: List =None, 
                    metadatas: List = None,
                    batch_size: int = 50):

        if len(texts) != len(vectors):
            raise ValueError("texts and vectors must have the same length")

        if not self.is_collection_existed(collection_name):
            self.logger.warning(f"Collection {collection_name} does not exist. Please create it first.")
            return False
        
        if metadatas is None:
            metadatas = [None] * len(texts)

        if len(metadatas) != len(texts):
            raise ValueError("metadatas and texts must have the same length")

        if record_ids is None:
            record_ids = [None] * len(texts)

        if len(record_ids) != len(texts):
            raise ValueError("record_ids and texts must have the same length")

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_records = [
                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x], "metadata": batch_metadatas[x]
                    }
                )

                for x in range(len(batch_texts))
            ]

            try:
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True    
    

    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        response = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit
        )
        return response.points


    def hybrid_search(
        self,
        collection_name: str,
        query_text: str,
        dense_vector: list,
        limit: int,
    ):
        try:
            response = self.client.query_points(
                collection_name=collection_name,
                query=dense_vector,
                limit=limit,
            )
        except Exception as e:
            self.logger.warning(f"Search failed: {e}")
            response = self.client.query_points(
                collection_name=collection_name,
                query=dense_vector,
                limit=limit,
            )
        return response.points