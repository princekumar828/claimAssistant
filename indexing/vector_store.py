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
        
        # Always keep numpy embeddings for filtered search fallback
        self.embeddings = np.array(embeddings).astype('float32')

        if faiss:
            # Initialize FAISS
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings)
            print(f"Index created with FAISS ({self.index.ntotal} vectors).")
        else:
            print(f"Index created with Numpy Fallback ({len(self.embeddings)} vectors).")

    def _filter_documents(self, filters: Dict[str, Any]) -> List[int]:
        """Returns indices of documents that match the filters."""
        if not filters:
            return list(range(len(self.documents)))
            
        indices = []
        for i, doc in enumerate(self.documents):
            meta = doc.get('metadata', {})
            match = True
            
            # Date Range Filter
            if 'start_date' in filters or 'end_date' in filters:
                claim_date = meta.get('claim_date')
                if claim_date:
                    if filters.get('start_date') and claim_date < filters['start_date']:
                        match = False
                    if filters.get('end_date') and claim_date > filters['end_date']:
                        match = False
            
            # Exact Match Filters (status, specialty, etc)
            for key in ['status', 'specialty', 'doctor_name', 'claim_id']:
                if key in filters and filters[key]:
                    # Case insensitive match
                    if meta.get(key, '').lower() != filters[key].lower():
                        match = False
                        
            if match:
                indices.append(i)
        
        return indices

    def search(self, query: str, k: int = 5, filters: Dict[str, Any] = None) -> List[Tuple[Dict[str, Any], float]]:
        """
        Searches the index for the query. Returns list of (document, distance).
        """
        self.load_model()
        query_vector = self.model.encode([query])
        
        # 1. Identify valid indices based on filters
        valid_indices = self._filter_documents(filters or {})
        
        # Optimization: If no filters, do standard FAISS search (fastest)
        if (not filters) and self.index:
             distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
             results = []
             for i, idx in enumerate(indices[0]):
                 if idx != -1 and idx < len(self.documents):
                     results.append((self.documents[idx], float(distances[0][i])))
             return results

        # 2. Filtered Search (Manual)
        # If filters exist, we must search manually within the valid subset
        # because IndexFlatL2 doesn't support ID masking easily without IDMap.
        
        if not valid_indices:
            return []
            
        if not hasattr(self, 'embeddings') or self.embeddings is None:
             raise ValueError("Index not initialized/loaded properly. Run /ingest again to enable filtering.")
        
        q = np.array(query_vector).astype('float32')
        
        # Create a subset of embeddings
        subset_embeddings = self.embeddings[valid_indices]
        
        # Vectorized L2 distance on subset: sum((x-y)^2)
        dists = np.sum((subset_embeddings - q)**2, axis=1)
        
        # Get top k indices relative to the subset
        # We need min(k, len(dists))
        curr_k = min(k, len(dists))
        subset_top_k_idx = np.argsort(dists)[:curr_k]
        
        results = []
        for idx in subset_top_k_idx:
            original_idx = valid_indices[idx]
            results.append((self.documents[original_idx], float(dists[idx])))
            
        return results

    def save_index(self):
        # We need to save embeddings for filtered search support upon reload
        # FAISS index saves structure, but we need the raw vectors if we want to do numpy filtering
        # (Technically FAISS index has them, but `reconstruct` is slow/complex depending on index type).
        # For this demo, simply pickling `embeddings` is easiest.
        
        data_to_save = {
            "documents": self.documents,
            "embeddings": self.embeddings if hasattr(self, 'embeddings') else None
        }
        
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(data_to_save, f)
            
        if self.index:
            faiss.write_index(self.index, self.index_file)
            
        print(f"Index and metadata saved to {self.index_file} and {self.metadata_file}")

    def load_index(self):
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.metadata_file, 'rb') as f:
                data = pickle.load(f)
                
            # Handle migration from old format (list) to new format (dict)
            if isinstance(data, list):
                self.documents = data
                # No embeddings loaded, so filtering won't work until re-ingestion
                print("WARNING: Loaded legacy index. Filtering will not work until you run /ingest.")
            else:
                self.documents = data["documents"]
                self.embeddings = data["embeddings"]
                
            print(f"Loaded index with {self.index.ntotal} vectors.")
        else:
            print("Index files not found.")
            
    def get_stats(self):
        return {
            "total_documents": len(self.documents) if self.documents else 0,
            "model_name": self.model_name,
            "backend": "FAISS (Local)"
        }
