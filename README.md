# AI Interview Trainer (Flask)

Quick scaffold for an AI interview training web app with a login screen, index page, and a structured layout. Includes a color palette using CSS variables so you can switch themes easily.

Palette (CSS variables are defined in `static/css/styles.css`):

- `--color-primary: #6a7b9d`
- `--color-secondary: #a8b5c8`
- `--color-muted: #b6a9ab`
- `--color-accent: #d5c1a3`
- `--color-bg: #f3f6f4`

Setup (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_APP = 'app.py'
python app.py
```

Then open `http://127.0.0.1:5000`.

Demo credentials:
- username: `admin`
- password: `demo123`

How to change theme/colors:
- Edit the CSS variables in `static/css/styles.css` under the `:root` block, or add extra `[data-theme="..."]` blocks and use `static/js/theme.js` to toggle.
