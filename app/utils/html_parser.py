import re
from bs4 import BeautifulSoup
import markdown
from urllib.parse import urljoin


class HTMLCleaner:
    """HTML cleaner and converter for content retrieval."""

    @staticmethod
    async def clean_html(html_content: str, base_url: str = '') -> BeautifulSoup:
        """
        Clean HTML by removing unnecessary elements.
        
        Args:
            html_content: The raw HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            BeautifulSoup object with clean HTML
        """
        # Create BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style, svg, img, iframe, form elements
        for element in soup.find_all(['script', 'style', 'svg', 'iframe', 'form', 
                                     'noscript', 'canvas', 'video', 'audio', 'source']):
            element.decompose()
            
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
            comment.extract()
            
        # Remove hidden elements
        for hidden in soup.find_all(style=re.compile(r'display:\s*none|visibility:\s*hidden')):
            hidden.decompose()
            
        # Make all URLs absolute for better context
        for a_tag in soup.find_all('a', href=True):
            a_tag['href'] = urljoin(base_url, a_tag['href'])
        
        # Replace img tags with their alt text or a placeholder
        for img in soup.find_all('img'):
            alt_text = img.get('alt', '')
            if alt_text:
                img.replace_with(f"[Image: {alt_text}]")
            else:
                img.replace_with("[Image]")
            
        return soup
    
    @staticmethod
    async def extract_title(soup: BeautifulSoup) -> str:
        """Extract the title from HTML."""
        if soup.title:
            return soup.title.string.strip()
        
        # Try to find an h1 if no title
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
            
        return "No title found"
    
    @staticmethod
    async def html_to_markdown(soup: BeautifulSoup) -> str:
        """
        Convert cleaned HTML to markdown.
        
        Args:
            soup: BeautifulSoup object with cleaned HTML
            
        Returns:
            Markdown string
        """
        # Find the main content
        main_content = soup.find('main') or soup.find('article') or soup.body
        
        if not main_content:
            main_content = soup
        
        # Process tables first, as they require special handling
        markdown_content = await HTMLCleaner._convert_tables(main_content)
        
        # Process other elements
        markdown_content = await HTMLCleaner._convert_content(markdown_content)
        
        return markdown_content.strip()
    
    @staticmethod
    async def _convert_tables(content):
        """Convert HTML tables to markdown tables."""
        soup = content
        if isinstance(content, str):
            soup = BeautifulSoup(content, 'html.parser')
        
        for table in soup.find_all('table'):
            markdown_table = []
            
            # Extract headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                for th in header_row.find_all(['th']):
                    headers.append(th.get_text().strip())
            else:
                # Try to get headers from first row
                first_row = table.find('tr')
                if first_row:
                    for th in first_row.find_all(['th', 'td']):
                        headers.append(th.get_text().strip())
            
            if headers:
                markdown_table.append('| ' + ' | '.join(headers) + ' |')
                markdown_table.append('| ' + ' | '.join(['---' for _ in headers]) + ' |')
            
            # Extract rows
            for tr in table.find_all('tr'):
                # Skip header row if we've already processed it
                if tr == header_row or (not header_row and tr == table.find('tr') and any(tr.find_all('th'))):
                    continue
                
                row_data = []
                for td in tr.find_all(['td', 'th']):
                    row_data.append(td.get_text().strip())
                
                if row_data:
                    markdown_table.append('| ' + ' | '.join(row_data) + ' |')
            
            # Replace the table with markdown
            if markdown_table:
                table_markdown = '\n'.join(markdown_table)
                table.replace_with(BeautifulSoup(f"<div>{table_markdown}</div>", 'html.parser'))
        
        return str(soup)
    
    @staticmethod
    async def _convert_content(html_content: str) -> str:
        """
        Convert HTML content to markdown with more robust handling.
        
        Args:
            html_content: HTML content as string
            
        Returns:
            Markdown content
        """
        # Convert headers
        for i in range(6, 0, -1):
            html_content = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', lambda m: f"{'#' * i} {HTMLCleaner._clean_text(m.group(1))}\n\n", html_content, flags=re.DOTALL)
        
        # Convert paragraphs
        html_content = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: f"{HTMLCleaner._clean_text(m.group(1))}\n\n", html_content, flags=re.DOTALL)
        
        # Convert blockquotes
        html_content = re.sub(r'<blockquote[^>]*>(.*?)</blockquote>', lambda m: '\n'.join([f"> {line}" for line in HTMLCleaner._clean_text(m.group(1)).split('\n')]) + '\n\n', html_content, flags=re.DOTALL)
        
        # Convert code blocks
        html_content = re.sub(r'<pre[^>]*><code[^>]*>(.*?)</code></pre>', lambda m: f"```\n{HTMLCleaner._clean_text(m.group(1))}\n```\n\n", html_content, flags=re.DOTALL)
        html_content = re.sub(r'<pre[^>]*>(.*?)</pre>', lambda m: f"```\n{HTMLCleaner._clean_text(m.group(1))}\n```\n\n", html_content, flags=re.DOTALL)
        
        # Convert inline code
        html_content = re.sub(r'<code[^>]*>(.*?)</code>', lambda m: f"`{HTMLCleaner._clean_text(m.group(1))}`", html_content, flags=re.DOTALL)
        
        # Convert strong/bold
        html_content = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', lambda m: f"**{HTMLCleaner._clean_text(m.group(2))}**", html_content, flags=re.DOTALL)
        
        # Convert em/italic
        html_content = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', lambda m: f"*{HTMLCleaner._clean_text(m.group(2))}*", html_content, flags=re.DOTALL)
        
        # Convert lists
        # First handle unordered lists
        html_content = re.sub(r'<ul[^>]*>(.*?)</ul>', lambda m: HTMLCleaner._process_list(m.group(1), ordered=False), html_content, flags=re.DOTALL)
        
        # Then handle ordered lists
        html_content = re.sub(r'<ol[^>]*>(.*?)</ol>', lambda m: HTMLCleaner._process_list(m.group(1), ordered=True), html_content, flags=re.DOTALL)
        
        # Convert links
        html_content = re.sub(r'<a [^>]*href=[\'"]([^\'"]*)[\'"][^>]*>(.*?)</a>', lambda m: f"[{HTMLCleaner._clean_text(m.group(2))}]({m.group(1)})", html_content, flags=re.DOTALL)
        
        # Convert horizontal rules
        html_content = re.sub(r'<hr[^>]*>', '\n---\n\n', html_content)
        
        # Strip remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Handle HTML entities
        html_content = html_content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"').replace('&nbsp;', ' ')
        
        # Clean up excessive whitespace
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)
        
        return html_content
    
    @staticmethod
    def _process_list(list_content, ordered=False):
        """Process list items to proper markdown format."""
        # Extract list items
        items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, flags=re.DOTALL)
        
        markdown_items = []
        for i, item in enumerate(items, 1):
            if ordered:
                markdown_items.append(f"{i}. {HTMLCleaner._clean_text(item)}")
            else:
                markdown_items.append(f"* {HTMLCleaner._clean_text(item)}")
        
        return '\n'.join(markdown_items) + '\n\n'
    
    @staticmethod
    def _clean_text(text):
        """Clean text content by removing extra whitespace."""
        # Remove newlines and extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @classmethod
    async def process_html(cls, html_content: str, base_url: str = '') -> dict:
        """
        Process HTML content into clean format with title and content.
        
        Args:
            html_content: Raw HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary with title, url and content
        """
        soup = await cls.clean_html(html_content, base_url)
        title = await cls.extract_title(soup)
        content = await cls.html_to_markdown(soup)
        
        return {
            "title": title,
            "url": base_url,
            "content": content
        } 