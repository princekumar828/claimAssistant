import os
import pickle
import numpy as np
from typing import List, Dict, Any, Tuple

# Try to import FAISS and SentenceTransformer
try:
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    # These will be handled in requirements.txt, but for robustness:
    print(f"CRITICAL IMPORT ERROR: {e}")
    faiss = None
    SentenceTransformer = None

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_file: str = "faiss_index.bin", metadata_file: str = "metadata.pkl"):
        self.model_name = model_name
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = None
        self.documents = [] # Parallel list to index integers
        self.model = None

    def load_model(self):
        if self.model is None:
            print(f"Loading embedding model: {self.model_name}...")
            if SentenceTransformer is None:
                raise ImportError("sentence-transformers not installed. Please pip install sentence-transformers.")
            self.model = SentenceTransformer(self.model_name)

    def create_index(self, documents: List[Dict[str, Any]]):
        """
        Creates an index from a list of documents.
        Each document must have 'text' key.
        """
        self.load_model()
        texts = [doc['text'] for doc in documents]
        print(f"Encoding {len(texts)} documents...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        self.documents = documents
        
        if faiss:
            # Initialize FAISS
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings).astype('float32'))
            print(f"Index created with FAISS ({self.index.ntotal} vectors).")
        else:
            # Fallback to Numpy
            self.embeddings = np.array(embeddings).astype('float32')
            print(f"Index created with Numpy Fallback ({len(self.embeddings)} vectors).")

    def search(self, query: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the index for the query. Returns list of (document, distance).
        """
        self.load_model()
        query_vector = self.model.encode([query])
        
        if self.index:
            # FAISS Search
            distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx < len(self.documents):
                    results.append((self.documents[idx], float(distances[0][i])))
            return results
        else:
            # Numpy Search (Cosine Similarity / Euclidean Logic)
            # Use L2 distance to match FAISS behavior: ||a-b||^2
            # but for simplicity in demo verify, we can use dot product if normalized, 
            # let's stick to L2 for consistency with FAISS code above.
            
            # Allow fallback if embeddings exist
            if not hasattr(self, 'embeddings') or self.embeddings is None:
                 raise ValueError("Index not initialized.")
            
            q = np.array(query_vector).astype('float32')
            
            # Vectorized L2 distance: sum((x-y)^2)
            dists = np.sum((self.embeddings - q)**2, axis=1)
            
            # Get top k indices
            indices = np.argsort(dists)[:k]
            
            results = []
            for idx in indices:
                results.append((self.documents[idx], float(dists[idx])))
            return results

    def save_index(self):
        if self.index:
            faiss.write_index(self.index, self.index_file)
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.documents, f)
            print(f"Index and metadata saved to {self.index_file} and {self.metadata_file}")

    def load_index(self):
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'rb') as f:
                self.documents = pickle.load(f)
            print(f"Loaded index with {self.index.ntotal} vectors.")
        else:
            print("Index files not found.")
            
    def get_stats(self):
        return {
            "total_documents": len(self.documents) if self.documents else 0,
            "model_name": self.model_name,
            "backend": "FAISS (Local)"
        }
