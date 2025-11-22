from groq import Groq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import re


class LangChainRAG:
    def __init__(self, api_key, model_name="llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model = model_name
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Back to normal chunk size
            chunk_overlap=150
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        self.retriever = None
        self.raw_text = ""
        self.file_markers = {}

    def load_text(self, txt):
        self.raw_text = txt
        # Extract and store file markers
        self.file_markers = self._extract_all_file_markers(txt)
        
        chunks = self.splitter.split_text(txt)
        self.vectorstore = FAISS.from_texts(chunks, self.embeddings)
        # Use standard retrieval without strict filters
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 15})

    def run(self, query):
        if not self.retriever:
            return "Please load material first using load_text() method."
            
        # Get relevant documents - remove strict filtering
        docs = self.retriever.get_relevant_documents(query)
        
        # Group by file without aggressive filtering
        file_content = self._group_content_by_file(docs)
        
        # Get all unique file names
        file_names = list(file_content.keys())

        if not file_content:
            # Fallback: use all files if no specific matches
            file_content = self._get_all_files_content()
            file_names = list(file_content.keys())

        prompt = f"""You are an educational assistant. Create a comprehensive explanation using the provided materials.

IMPORTANT RULES:
1. Create ONE clear section for each file that has relevant content
2. Use the exact file names provided
3. Format each file section like this:
   📘 [EXACT FILE NAME]
   (Explained simply — based on your PDF)

   [Content from that file...]

4. Use numbered sections (1., 2., 3.) for main topics
5. Use → for definitions
6. Include specific page references like (p.4) when available
7. Use bullet points for lists
8. Cover the main concepts from each file
9. If a file doesn't have specific information about the query, still include its main topics

USER'S QUESTION: {query}

CONTENT BY FILE:
{self._format_file_content(file_content)}

Create a comprehensive explanation covering the main content from each file. Include all files that have educational content:"""

        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500,
            )
            return res.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def _extract_all_file_markers(self, text):
        """Extract all file markers from the raw text"""
        file_markers = {}
        lines = text.split('\n')
        
        for line in lines:
            if "📚 FILE:" in line:
                match = re.search(r'📚 FILE:\s*([^\n=]+)', line)
                if match:
                    file_name = match.group(1).strip()
                    file_markers[file_name] = True
            elif "--- FILE:" in line:
                match = re.search(r'--- FILE:\s*([^\n=]+)\s*---', line)
                if match:
                    file_name = match.group(1).strip()
                    file_markers[file_name] = True
        
        return file_markers

    def _extract_file_name(self, text):
        """Extract file name from text"""
        # Look for file markers
        patterns = [
            r'📚 FILE:\s*([^\n=]+)',
            r'--- FILE:\s*([^\n=]+)\s*---',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                filename = match.group(1).strip()
                if len(filename) > 3:
                    return filename
        
        # Fallback to known file markers
        for known_file in self.file_markers.keys():
            if known_file.lower() in text.lower():
                return known_file
        
        return "Course Materials"

    def _group_content_by_file(self, docs):
        """Group document content by file names"""
        file_content = {}
        
        for doc in docs:
            file_name = self._extract_file_name(doc.page_content)
            if file_name not in file_content:
                file_content[file_name] = []
            
            # Clean the content
            clean_content = self._clean_content(doc.page_content)
            if clean_content:
                file_content[file_name].append(clean_content)
        
        return file_content

    def _get_all_files_content(self):
        """Fallback: get content from all files when no specific matches"""
        file_content = {}
        # Split the raw text by file markers
        sections = re.split(r'📚 FILE:[^\n]+\n', self.raw_text)
        file_markers = re.findall(r'📚 FILE:\s*([^\n]+)', self.raw_text)
        
        for i, marker in enumerate(file_markers):
            if i < len(sections):
                file_content[marker.strip()] = [sections[i]]
        
        return file_content

    def _clean_content(self, text):
        """Remove file headers and clean up content"""
        patterns = [
            r'📚 FILE:[^\n]+\n',
            r'--- FILE:[^\n]+---',
        ]
        
        clean_text = text
        for pattern in patterns:
            clean_text = re.sub(pattern, '', clean_text)
        
        return clean_text.strip()

    def _format_file_content(self, file_content):
        """Format file content for the prompt"""
        formatted = ""
        for file_name, contents in file_content.items():
            formatted += f"\n--- {file_name} ---\n"
            # Combine content
            combined_content = " ".join(contents)
            # Limit length but ensure meaningful content
            if len(combined_content) > 800:
                preview = combined_content[:700] + "..."
            else:
                preview = combined_content
            formatted += f"{preview}\n"
        return formatted