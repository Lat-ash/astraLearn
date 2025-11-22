from groq import Groq
import re


class SummarizerAgent:
    def __init__(self, api_key, model_name="llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model = model_name

    def summarize(self, text):
        # Extract and clean file names properly
        file_sections = self._split_text_by_files(text)
        
        if not file_sections:
            return "• No content found in the uploaded materials."

        prompt = f"""CRITICAL: You MUST format the response EXACTLY as shown below. Use ONLY bullet points (•) and file headers (📘).

EXAMPLE FORMAT:
📘 File Name 1
• First key point from this file
• Second key point from this file  
• Third key point from this file
• Fourth key point from this file

📘 File Name 2
• First key point from this file
• Second key point from this file
• Third key point from this file

RULES:
- Use ONLY bullet points (•) - no numbers, no dashes, no paragraphs
- Each bullet must start with • followed by a space
- Maximum 6-8 bullet points per file
- Keep each bullet point to 1 line
- Include page references like (p.4) when available
- Use the exact file names provided below

FILES TO SUMMARIZE: {', '.join([section['file_name'] for section in file_sections])}

CONTENT:
{self._format_file_sections(file_sections)}

Now create the summary following EXACTLY the format above. Use ONLY bullet points:"""

        try:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for more consistent formatting
                max_tokens=1500,
            )

            summary = res.choices[0].message.content
            
            # Force bullet point formatting
            return self._force_bullet_formatting(summary, file_sections)
            
        except Exception as e:
            return self._create_forced_bullet_summary(file_sections)

    def _split_text_by_files(self, text):
        """Split text into sections by file markers and remove duplicates"""
        file_sections = []
        seen_files = set()
        
        # Split by file markers
        sections = re.split(r'(?=📚 FILE:|--- FILE:)', text)
        
        for section in sections:
            if not section.strip():
                continue
                
            file_name = self._extract_clean_file_name(section)
            
            # Skip duplicates and incomplete names
            if (file_name and file_name not in seen_files and 
                len(file_name) > 10 and not file_name.endswith('...')):
                
                seen_files.add(file_name)
                content = self._clean_file_content(section, file_name)
                
                if content and len(content) > 100:
                    file_sections.append({
                        'file_name': file_name,
                        'content': content
                    })
        
        return file_sections

    def _extract_clean_file_name(self, text):
        """Extract and clean file name from text section"""
        patterns = [
            r'📚 FILE:\s*([^\n=]+?)(?=\n|$)',
            r'--- FILE:\s*([^\n=]+?)\s*---',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                filename = match.group(1).strip()
                filename = re.sub(r'\.\.\.$', '', filename)
                filename = re.sub(r'\s+', ' ', filename)
                return filename
        
        return None

    def _clean_file_content(self, text, file_name):
        """Remove file markers and clean content"""
        patterns = [
            r'📚 FILE:[^\n]+\n',
            r'--- FILE:[^\n]+---\n',
        ]
        
        clean_text = text
        for pattern in patterns:
            clean_text = re.sub(pattern, '', clean_text)
        
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
        return clean_text.strip()

    def _format_file_sections(self, file_sections):
        """Format file sections for the prompt"""
        formatted = ""
        for section in file_sections:
            formatted += f"\n--- {section['file_name']} ---\n"
            content = section['content']
            if len(content) > 800:
                content = content[:600] + "..."
            formatted += f"{content}\n"
        return formatted

    def _force_bullet_formatting(self, summary, file_sections):
        """Force bullet point formatting by completely rewriting if needed"""
        if not summary:
            return self._create_forced_bullet_summary(file_sections)
        
        # Check if the summary already follows our format
        lines = summary.split('\n')
        has_bullets = any('•' in line for line in lines)
        has_file_headers = any('📘' in line for line in lines)
        
        if has_bullets and has_file_headers:
            # Clean up existing bullet format
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith('📘'):
                    cleaned_lines.append(line)
                elif line.startswith('•'):
                    cleaned_lines.append(line)
                elif line and not line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '-', 'EXAMPLE', 'RULES:')):
                    # Convert non-bullet lines to bullets
                    cleaned_lines.append(f"• {line}")
            
            return '\n'.join(cleaned_lines)
        else:
            # Completely rewrite the summary
            return self._create_forced_bullet_summary(file_sections)

    def _create_forced_bullet_summary(self, file_sections):
        """Create a bullet-point summary by force if AI doesn't comply"""
        summary_lines = []
        
        for section in file_sections:
            summary_lines.append(f"📘 {section['file_name']}")
            
            # Extract key content and create bullet points
            content = section['content']
            
            # Simple extraction of key sentences for bullet points
            sentences = re.split(r'[.!?]+', content)
            key_points = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 20 and len(sentence) < 150 and 
                    len(key_points) < 8 and
                    not any(word in sentence.lower() for word in ['example', 'note:', 'figure', 'table'])):
                    key_points.append(sentence)
            
            # Add bullet points
            for point in key_points[:6]:  # Max 6 points per file
                summary_lines.append(f"• {point}")
            
            summary_lines.append("")  # Empty line between files
        
        return '\n'.join(summary_lines).strip()