import re


def deal_text(text):
    lines = text.strip().split('\n')
    result = []
    current_item = []
    current_indent = None
    if text == 'nan':
        return result
    for line in lines:
        stripped_line = line.lstrip()
        indent = len(line) - len(stripped_line)

        if current_indent is None or indent == current_indent:
            if current_item:
                result.append('\n'.join(current_item))
                current_item = []
            current_indent = indent

        cleaned_line = re.sub(r'^\d+\.\s*', '', line)
        current_item.append(cleaned_line)

    if current_item:
        result.append('\n'.join(current_item))

    return result
