import re
import os

def update_seo():
    tex_path = 'Resume.tex'
    html_path = 'index.html'

    if not os.path.exists(tex_path):
        print(f"Error: '{tex_path}' not found in the current directory.")
        return

    if not os.path.exists(html_path):
        print(f"Error: '{html_path}' not found in the current directory.")
        return

    with open(tex_path, 'r', encoding='utf-8') as f:
        tex_content = f.read()

    # Extract content between \begin{document} and \end{document}
    match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', tex_content, re.DOTALL)
    if match:
        text = match.group(1)
    else:
        text = tex_content # fallback if document markers not found
        
    # 1. Remove comments
    text = re.sub(r'(?<!\\)%.*$', '', text, flags=re.MULTILINE)
    
    # 2. Escape basic HTML chars (avoid breaking <a> tags we inject next)
    text = text.replace(r'\&', '&amp;')
    
    # 3. Process links: \href{url}{text}
    # This regex ensures we safely extract href regardless of newlines inside the brackets if any
    text = re.sub(r'\\href\{([^{}]+)\}\{([^{}]+)\}', r'<a href="\1">\2</a>', text)
    
    # 4. Handle formatting multiple times to catch nesting
    for _ in range(3):
        text = re.sub(r'\\textbf\{([^{}]+)\}', r'<strong>\1</strong>', text)
        text = re.sub(r'\\textit\{([^{}]+)\}', r'<em>\1</em>', text)
        text = re.sub(r'\\textnormal\{([^{}]+)\}', r'\1', text)
        text = re.sub(r'\\small\{([^{}]+)\}', r'\1', text)
        text = re.sub(r'\\large\{([^{}]+)\}', r'\1', text)
        text = re.sub(r'\\LARGE\{([^{}]+)\}', r'\1', text)
        text = re.sub(r'\\scshape\{([^{}]+)\}', r'\1', text)

    # 4.5. Remove spacing & environment commands completely including their arguments
    text = re.sub(r'\\begin\{center\}', '', text)
    text = re.sub(r'\\end\{center\}', '', text)
    text = re.sub(r'\\begin\s*\{[^}]+\}', '', text)
    text = re.sub(r'\\end\s*\{[^}]+\}', '', text)
    text = re.sub(r'\\vspace\s*\{[^}]*\}', '', text)
    text = re.sub(r'\\hfill', '', text)
    text = re.sub(r'\\hspace\s*\{[^}]*\}', '', text)
    # Remove any linebreaks with optional length arguments like \\[3pt]
    text = re.sub(r'\\\\\s*\[[^\]]+\]', '<br>', text)

    # 5. Extract headings and sections
    text = re.sub(r'\\section\*\s*\{([^{}]+)\}', r'<h2>\1</h2>', text)
    
    # 6. Extract common resume macros
    text = re.sub(r'\\resumeSubheading\s*\{([^{}]+)\}\s*\{([^{}]+)\}\s*\{([^{}]+)\}\s*\{([^{}]+)\}', 
                  r'<h3>\1, \2</h3><p>\3 | \4</p>', text)
    text = re.sub(r'\\resumeProjectHeading\s*\{([^{}]+)\}\s*\{([^{}]+)\}', 
                  r'<h3>\1</h3><p>\2</p>', text)
    text = re.sub(r'\\resumeItem\s*\{([^{}]+)\}\s*\{([^{}]+)\}', 
                  r'<li><strong>\1:</strong> \2</li>', text)
    text = re.sub(r'\\resumeSubItem\s*\{([^{}]+)\}\s*\{([^{}]+)\}', 
                  r'<li><strong>\1:</strong> \2</li>', text)
                  
    # 7. Lists
    text = text.replace(r'\begin{itemize}[leftmargin=*, itemsep=1pt]', '<ul>')
    text = text.replace(r'\begin{itemize}[leftmargin=*]', '<ul>')
    text = text.replace(r'\begin{itemize}', '<ul>')
    text = text.replace(r'\end{itemize}', '</ul>')
    text = text.replace(r'\resumeSubHeadingListStart', '<ul>')
    text = text.replace(r'\resumeSubHeadingListEnd', '</ul>')
    text = text.replace(r'\resumeItemListStart', '<ul>')
    text = text.replace(r'\resumeItemListEnd', '</ul>')
    
    text = re.sub(r'\\item', r'<li>', text)

    # 8. Strip remaining commands
    # e.g., \vspace{...}, \small, \Large
    text = re.sub(r'\\[a-zA-Z]+(?:\[[^\]]*\])?', '', text)
    
    # 9. Clean braces and formatting characters
    text = text.replace('{', '').replace('}', '')
    text = text.replace('\\\\', '<br>')
    text = text.replace('\\', '')
    text = text.replace('~', ' ')
    text = text.replace('textbar', ' | ')
    
    # Convert double/triple dashes to en/em dashes
    text = text.replace('---', '&mdash;')
    text = text.replace('--', '&ndash;')
    
    # 10. Clean up text and convert to lines
    lines = []
    for line in text.split('\n'):
        clean_line = line.strip()
        if not clean_line:
            continue
            
        if clean_line.startswith('<h') or clean_line.startswith('<ul') or clean_line.startswith('</ul') or clean_line.startswith('<li'):
            lines.append(clean_line)
        else:
            lines.append(f"<p>{clean_line}</p>")

    extracted_html = '\n        '.join(lines)

    # Read the existing HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Define replacement block
    marker_start = '<!-- SEO_CONTENT_START -->'
    marker_end = '<!-- SEO_CONTENT_END -->'

    if marker_start in html_content and marker_end in html_content:
        replacement = f"{marker_start}\n    <div class=\"sr-only\">\n        {extracted_html}\n    </div>\n    {marker_end}"
        pattern = re.compile(f"{re.escape(marker_start)}.*?{re.escape(marker_end)}", re.DOTALL)
        new_html = pattern.sub(replacement, html_content)

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
            
        print("Successfully embedded LaTeX text with links into index.html for SEO.")
    else:
        print(f"Error: markers {marker_start} and {marker_end} not found in {html_path}.")

if __name__ == "__main__":
    update_seo()