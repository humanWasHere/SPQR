from pathlib import Path


def markdown_to_pdf_doc():
    from markdown_pdf import MarkdownPdf
    from markdown_pdf import Section
    import re

    pdf = MarkdownPdf(toc_level=2)

    # fichier markdown
    markdown_file = Path(__file__).parents[2] / "docs" / "user_documentation" / "user_documentation.md"
    markdown_content = markdown_file.read_text()

    # initiatialisation de la regex
    image_pattern = r'!\[([^\]]+)\]\(([^\)]+\.png) "([^"]+)"\)'
    image_matches = re.findall(image_pattern, markdown_content)

    # remplacement de chaque chaine détectée
    picture_number = 0
    for match in image_matches:
        picture_number += 1
        print(match)
        markdown_content = markdown_content.replace(f'![{match[0]}]({match[1]} "{match[2]}")', f'![python](docs/user_documentation/pictures/Picture{picture_number}.png)')
        # if markdown_content.replace(image, f'![python]({relative_image_path})')

    # détection des sections markdown
    section_pattern = r'(^#{1,2} .+?$)'
    section_matches = re.findall(section_pattern, markdown_content, re.MULTILINE)
    sections = re.split(section_pattern, markdown_content, flags=re.MULTILINE)

    result = []
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        content = sections[i + 1].strip()
        result.append((title, content))

    # écriture de chaque section pour le pdf
    for title, content in result:
        pdf.add_section(Section(f'{title}\n{content}\n', toc=False))

    pdf.meta["title"] = "SPQR - User Documentation"

    pdf.save("SPQR_user_doc.pdf")
