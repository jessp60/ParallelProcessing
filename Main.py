from requests_html import HTML

with open("simple.html") as file:
    source = file.read()
    html = HTML(html=source)

# Output the entire text and HTML content
# print(html.text)
# print(html.HTML)

match = html.find("title")
print(match[0].text)  # Output the text of the title element
print(match[0].html)  # Output the HTML of the title element

