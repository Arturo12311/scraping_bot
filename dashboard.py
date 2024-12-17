from flask import Flask, render_template_string
import json
import os

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Scrape Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .null { color: #b00; font-weight: bold; }
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border-bottom: 1px solid #ddd;
            vertical-align: top;
        }
        th {
            background-color: #f9f9f9;
            font-weight: bold;
        }
        a {
            color: #1a73e8;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .note { color: #555; font-style: italic; margin-bottom: 20px; }
        .timestamp {
            margin-bottom: 20px;
            font-style: italic;
            color: #333;
        }
    </style>
</head>
<body>
    <h1>Scrape Dashboard</h1>
    {% if last_updated %}
        <div class="timestamp">Last Updated: {{ last_updated }}</div>
    {% endif %}
    {{ data_html|safe }}
</body>
</html>
"""

def format_value(value):
    if value is None:
        return '<span class="null">Out of Stock</span>'
    elif isinstance(value, (dict, list)):
        return convert_to_html(value)  # Recursively convert nested structures
    else:
        return str(value)

def make_clickable_if_url(key):
    # Basic check if key looks like a URL
    if isinstance(key, str) and key.startswith("http"):
        return f'<a href="{key}" target="_blank">{key}</a>'
    return key

def convert_dict_to_table(d):
    rows = []
    for k, v in d.items():
        # skip last_updated here (we display it separately)
        if k == "last_updated":
            continue
        displayed_key = make_clickable_if_url(k)
        val = format_value(v)
        rows.append(f"<tr><th>{displayed_key}</th><td>{val}</td></tr>")
    return "<table>" + "".join(rows) + "</table>"

def convert_list_to_table(lst):
    # If the list contains dictionaries with the same keys, 
    # we can make a header row. Otherwise, just list them out.
    if all(isinstance(item, dict) for item in lst):
        # Extract all keys to form a header
        all_keys = set()
        for item in lst:
            all_keys.update(item.keys())

        all_keys = sorted(all_keys)
        header = "".join(f"<th>{key}</th>" for key in all_keys)
        rows = [f"<tr>{header}</tr>"]
        for item in lst:
            row_values = []
            for key in all_keys:
                val = format_value(item.get(key))
                row_values.append(f"<td>{val}</td>")
            rows.append("<tr>" + "".join(row_values) + "</tr>")

        return "<table>" + "".join(rows) + "</table>"
    else:
        # Just a simple list of values
        items = "".join(f"<tr><td>{format_value(i)}</td></tr>" for i in lst)
        return "<table>" + items + "</table>"

def convert_to_html(data):
    if isinstance(data, dict):
        return convert_dict_to_table(data)
    elif isinstance(data, list):
        return convert_list_to_table(data)
    else:
        return format_value(data)

@app.route("/")
def dashboard():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            data = json.load(f)
    else:
        data = {}

    last_updated = data.get("last_updated")
    data_html = convert_to_html(data)
    return render_template_string(TEMPLATE, data_html=data_html, last_updated=last_updated)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
