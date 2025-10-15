# ir_retriever.py (Optimized Version)
import os
import random
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

try:
    import PyPDF2
except ImportError:
    raise ImportError("PyPDF2 is required for PDF support. Run: pip install PyPDF2")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class SimpleIR:
    """Optimized TF-IDF retriever with caching and faster operations."""

    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.docs: List[str] = []
        self.paths: List[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None
        self._cached_folder = None  # Track which folder is cached
        self._load_docs()

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Optimized PDF extraction with error handling."""
        text_chunks = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                # Limit pages for faster processing
                max_pages = min(len(pdf_reader.pages), 50)  # Limit to 50 pages
                
                for i in range(max_pages):
                    page_text = pdf_reader.pages[i].extract_text()
                    if page_text and len(page_text.strip()) > 50:
                        text_chunks.append(page_text)
                        
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        
        return "\n\n".join(text_chunks)

    def _load_docs(self, folder: Optional[str] = None):
        """
        Optimized document loading with better chunking.
        Only reloads if folder changes (caching mechanism).
        """
        base_dir = folder or self.data_dir
        
        # Check if we already loaded this folder
        if self._cached_folder == base_dir and self.docs:
            print(f"Using cached documents from: {base_dir}")
            return
        
        self.docs = []
        self.paths = []

        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
            print(f"Created data directory at: {base_dir}")
            return

        print(f"Loading documents from: {base_dir}")
        
        for root, _, files in os.walk(base_dir):
            for fn in files:
                if not fn.lower().endswith(('.pdf', '.txt')):
                    continue

                file_path = os.path.join(root, fn)
                text = ""

                # PDF handling
                if fn.lower().endswith('.pdf'):
                    text = self._extract_text_from_pdf(file_path)
                    if not text.strip():
                        continue

                # TXT handling
                elif fn.lower().endswith('.txt'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read().strip()
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue

                # Improved chunking strategy
                if text:
                    chunks = self._smart_chunk(text)
                    for i, chunk in enumerate(chunks):
                        if len(chunk) > 100:  # Minimum chunk size
                            self.docs.append(chunk)
                            rel = os.path.relpath(file_path, base_dir)
                            self.paths.append(f"{rel}#p{i}")

        file_count = len(set([p.split('#')[0] for p in self.paths])) if self.paths else 0
        print(f"Loaded {len(self.docs)} passages from {file_count} file(s)")

        # Build TF-IDF matrix (optimized settings)
        if self.docs:
            self._vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=3000,  # Reduced for speed
                min_df=1,
                max_df=0.9,
                ngram_range=(1, 2)  # Include bigrams for better matching
            )
            try:
                self._matrix = self._vectorizer.fit_transform(self.docs)
                self._cached_folder = base_dir  # Mark as cached
                print("TF-IDF matrix built successfully")
            except Exception as e:
                print(f"Error building TF-IDF matrix: {e}")
                self._matrix = None
        else:
            print("No documents found. Add .txt or .pdf files to data/ directory.")

    def _smart_chunk(self, text: str, chunk_size: int = 800) -> List[str]:
        """
        Intelligent chunking that preserves sentence boundaries.
        """
        # First try paragraph splits
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            # If single paragraph is too large, split by sentences
            if para_size > chunk_size * 1.5:
                sentences = para.split('. ')
                for sent in sentences:
                    sent = sent.strip() + '.'
                    if current_size + len(sent) > chunk_size and current_chunk:
                        chunks.append(' '.join(current_chunk))
                        current_chunk = [sent]
                        current_size = len(sent)
                    else:
                        current_chunk.append(sent)
                        current_size += len(sent)
            
            # Normal paragraph handling
            elif current_size + para_size > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def retrieve(
        self, 
        query: str, 
        topk: int = 5, 
        folder: Optional[str] = None, 
        search_dir: Optional[str] = None,
        randomize: bool = True,  # NEW: Add randomization
        diversity_factor: float = 0.3  # NEW: Control diversity
    ) -> List[Tuple[str, float]]:
        """
        Optimized retrieval with optional randomization for unique results.
        
        Args:
            query: Search query
            topk: Number of results to return
            folder/search_dir: Optional folder to search in
            randomize: If True, adds some randomness to results
            diversity_factor: Higher = more diverse results (0.0-1.0)
        """
        target_folder = folder or search_dir

        # Only reload if folder changes
        if target_folder and target_folder != self._cached_folder:
            self._load_docs(target_folder)
        elif not self.docs or self._matrix is None:
            self._load_docs()

        if not self.docs or self._matrix is None:
            return []

        try:
            # Vectorize query
            qv = self._vectorizer.transform([query])
            
            # Compute similarities
            sims = cosine_similarity(qv, self._matrix).flatten()
            
            # Get more candidates than needed for randomization
            candidate_count = min(topk * 3, len(sims))
            top_indices = np.argsort(sims)[::-1][:candidate_count]
            
            # Filter valid results
            candidates = [(i, sims[i]) for i in top_indices if sims[i] > 0.01]
            
            if not candidates:
                return []
            
            # Apply randomization for variety
            if randomize and len(candidates) > topk:
                # Split into high and medium relevance
                high_rel_count = max(2, topk // 2)
                high_rel = candidates[:high_rel_count]
                medium_rel = candidates[high_rel_count:candidate_count]
                
                # Always include some high relevance
                selected = high_rel[:topk//2]
                
                # Randomly sample from medium relevance
                remaining = topk - len(selected)
                if medium_rel and remaining > 0:
                    # Weight by score for probabilistic selection
                    weights = [score ** (1 - diversity_factor) for _, score in medium_rel]
                    sample_size = min(remaining, len(medium_rel))
                    sampled_indices = random.choices(
                        range(len(medium_rel)), 
                        weights=weights, 
                        k=sample_size
                    )
                    selected.extend([medium_rel[i] for i in sampled_indices])
                
                # Shuffle for variety
                random.shuffle(selected)
                final_results = selected[:topk]
            else:
                final_results = candidates[:topk]
            
            # Convert to return format
            results = [(self.docs[i], float(score)) for i, score in final_results]
            
            return results
            
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []

    def reload_docs(self):
        """Force reload documents from default directory."""
        self._cached_folder = None  # Clear cache
        self._load_docs()


# Quick test
if __name__ == '__main__':
    ir = SimpleIR()
    print("\nTesting optimized retrieval:")
    results = ir.retrieve('photosynthesis', topk=3, randomize=True)
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   {doc[:150]}...")