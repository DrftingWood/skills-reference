"""Presentation strings for the skills reference site."""


def page_shell(title, body, nav):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header><h1>{title}</h1>{nav}</header>
<main>
{body}
</main>
</body>
</html>
"""
