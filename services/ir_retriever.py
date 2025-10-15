# ir_retriever.py
# TF-IDF retriever supporting both plain text and PDF files
import os
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

try:
    import PyPDF2
except ImportError:
    raise ImportError("PyPDF2 is required for PDF support. Run: pip install PyPDF2")

# default data directory (same folder as this script /data)
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

class SimpleIR:
    """Simple TF-IDF based information retriever (supports .txt and .pdf)."""

    def __init__(self, data_dir: str = DATA_DIR):
        # allow overriding data_dir (helpful for tests)
        self.data_dir = data_dir
        self.docs: List[str] = []   # list of text passages
        self.paths: List[str] = []  # corresponding file#paragraph identifiers
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._matrix = None
        # load docs from the default data dir at init
        self._load_docs()

    # -------------------------
    # PDF text extraction
    # -------------------------
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file using PyPDF2."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        return text

    # -------------------------
    # Load documents (txt & pdf)
    # -------------------------
    def _load_docs(self, folder: Optional[str] = None):
        """
        Load documents from .txt and .pdf files.
        If 'folder' is provided, load files from that folder (and its subfolders).
        Otherwise use self.data_dir (default DATA_DIR).
        """
        self.docs = []
        self.paths = []

        base_dir = folder or self.data_dir

        # create folder if missing
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
            print(f"Created data directory at: {base_dir}")
            return

        # Walk directory tree so subject/module subfolders are supported
        for root, _, files in os.walk(base_dir):
            for fn in files:
                # only handle supported extensions
                if not fn.lower().endswith(('.pdf', '.txt')):
                    continue

                file_path = os.path.join(root, fn)
                text = ""

                # PDF handling
                if fn.lower().endswith('.pdf'):
                    text = self._extract_text_from_pdf(file_path)
                    if not text.strip():
                        print(f"Warning: No text extracted from {file_path}")
                        continue

                # TXT handling
                elif fn.lower().endswith('.txt'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            text = f.read().strip()
                    except Exception as e:
                        print(f"Error reading text file {file_path}: {e}")
                        continue

                # Split text into passages (paragraph-like chunks)
                if text:
                    paras = [p.strip() for p in text.split('\n\n') if p.strip()]
                    # fallback to single-line splits if double newlines not found
                    if len(paras) <= 1:
                        paras = [p.strip() for p in text.split('\n') if p.strip() and len(p.strip()) > 50]

                    for i, para in enumerate(paras):
                        if len(para) > 30:
                            self.docs.append(para)
                            # store relative path (relative to base_dir) plus paragraph index
                            rel = os.path.relpath(file_path, base_dir)
                            self.paths.append(f"{rel}#p{i}")

        file_count = len(set([p.split('#')[0] for p in self.paths])) if self.paths else 0
        print(f"Loaded {len(self.docs)} passages from {file_count} file(s) under: {base_dir}")

        # Build TF-IDF matrix if we have docs
        if self.docs:
            self._vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=5000,
                min_df=1,
                max_df=0.95
            )
            try:
                self._matrix = self._vectorizer.fit_transform(self.docs)
            except Exception as e:
                print(f"Error building TF-IDF matrix: {e}")
                self._matrix = None
        else:
            print("No documents loaded. Add .txt or .pdf files to the data/ directory.")

    # -------------------------
    # Retrieve top-k passages
    # -------------------------
    def retrieve(self, query: str, topk: int = 5, folder: Optional[str] = None, search_dir: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Retrieve top-k most relevant passages for a given query.
        Supports either 'folder' or legacy 'search_dir' parameter to restrict which files are loaded.
        If neither is provided, searches the default data_dir loaded at init.
        Returns a list of (passage_text, score) tuples.
        """
        # accept either name for backward compatibility
        target_folder = folder or search_dir

        # if user provided a folder, reload docs from that folder
        if target_folder:
            self._load_docs(target_folder)
        elif not self.docs or self._matrix is None:
            # ensure docs are loaded if not already
            self._load_docs()

        if not self.docs or self._matrix is None:
            return []

        # vectorize query and compute cosine similarities
        try:
            qv = self._vectorizer.transform([query])
        except Exception as e:
            print(f"Error transforming query: {e}")
            return []

        sims = linear_kernel(qv, self._matrix).flatten()
        top_idxs = sims.argsort()[::-1][:topk]
        results = [(self.docs[i], float(sims[i])) for i in top_idxs if sims[i] > 0]
        return results

    # -------------------------
    # Utility: reload all docs (default data_dir)
    # -------------------------
    def reload_docs(self):
        """Reload documents from the default data directory."""
        self._load_docs()


# -------------------------
# Quick test when run directly
# -------------------------
if __name__ == '__main__':
    ir = SimpleIR()
    print("\nTesting retrieval (example):")
    results = ir.retrieve('what is photosynthesis', topk=3)
    for i, (doc, score) in enumerate(results, 1):
        print(f"\n{i}. Score: {score:.4f}")
        print(f"   {doc[:200]}...")