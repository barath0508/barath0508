#!/usr/bin/env python3
"""
Resume Generator Script
- Reads resume/resume.json
- Renders resume/resume.tex (with robust LaTeX escaping)
- Generates a sleek, interactive GitHub Pages web portal in dist/index.html
"""

import json
import os
import re
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
RESUME_DIR = ROOT_DIR / "resume"
DIST_DIR = ROOT_DIR / "dist"
DATA_FILE = RESUME_DIR / "resume.json"
OUTPUT_TEX = RESUME_DIR / "resume.tex"
OUTPUT_HTML = DIST_DIR / "index.html"


def escape_latex(text: str) -> str:
    """Escapes special characters in text for LaTeX compatibility."""
    if not isinstance(text, str):
        return str(text)

    # Don't escape if it looks like intentional LaTeX command
    if text.startswith("\\") and "{" in text:
        return text

    # Standard LaTeX replacements
    # Note: & is escaped unless already escaped
    text = re.sub(r'(?<!\\)&', r'\&', text)
    text = re.sub(r'(?<!\\)%', r'\%', text)
    text = re.sub(r'(?<!\\)#', r'\#', text)
    text = re.sub(r'(?<!\\)_', r'\_', text)
    # Replace vertical bar separators with LaTeX vert symbol
    text = re.sub(r'\s*\|\s*', r' $\\vert$ ', text)

    return text


def build_latex(data: dict) -> str:
    """Renders resume.tex matching Barath's LaTeX template."""
    personal = data["personal"]
    summary = escape_latex(data.get("summary", ""))
    education = data.get("education", [])
    skills = data.get("skills", [])
    projects = data.get("projects", [])
    experience = data.get("experience", [])
    languages = data.get("languages", [])

    contact_row_2 = f"\\href{{{personal['github']}}}{{{personal['github_display']}}} $\\vert$ \\href{{{personal['linkedin']}}}{{{personal['linkedin_display']}}}"
    if personal.get("portfolio"):
        contact_row_2 += f" $\\vert$ \\href{{{personal['portfolio']}}}{{{personal.get('portfolio_display', personal['portfolio'])}}}"

    lines = [
        r"\documentclass[a4paper,10.5pt]{article}",
        "",
        r"\usepackage[margin=0.65in]{geometry}",
        r"\usepackage{titlesec}",
        r"\usepackage{enumitem}",
        r"\usepackage{hyperref}",
        r"\usepackage{xcolor}",
        "",
        r"\definecolor{darkblue}{RGB}{20,20,20}",
        r"\hypersetup{colorlinks=true, urlcolor=darkblue, linkcolor=darkblue}",
        "",
        r"\pagestyle{empty}",
        r"\setlength{\parindent}{0pt}",
        "",
        r"\titleformat{\section}{\large\bfseries\scshape}{}{0em}{}[\titlerule]",
        r"\titlespacing{\section}{0pt}{10pt}{6pt}",
        "",
        r"\newcommand{\resumeItem}[1]{\item #1}",
        r"\newenvironment{resumeItemize}{\begin{itemize}[leftmargin=*, itemsep=1pt, topsep=2pt]}{\end{itemize}}",
        "",
        r"\newcommand{\resumeProject}[3]{",
        r"  \textbf{#1} \hfill \textit{#2} \\",
        r"  \textit{Tech Stack: #3}",
        r"}",
        "",
        r"\begin{document}",
        "",
        r"% ---------- HEADER ----------",
        r"\begin{center}",
        f"    {{\\LARGE \\textbf{{{escape_latex(personal['name'])}}}}} \\\\[2pt]",
        f"    {escape_latex(personal['title'])} \\\\[2pt]",
        f"    {escape_latex(personal['location'])} $\\vert$ {escape_latex(personal['phone'])} $\\vert$ \\href{{mailto:{personal['email']}}}{{{personal['email']}}} \\\\",
        f"    {contact_row_2}",
        r"\end{center}",
        "",
        r"% ---------- SUMMARY ----------",
        r"\section*{Professional Summary}",
        summary,
        "",
        r"% ---------- EDUCATION ----------",
        r"\section*{Education}",
    ]

    for edu in education:
        lines.append(f"\\textbf{{{escape_latex(edu['degree'])}}} \\hfill {edu['period']} \\\\")
        lines.append(f"{escape_latex(edu['institution'])} \\hfill {escape_latex(edu['score'])} \\\\")
        lines.append(f"\\textit{{{escape_latex(edu['notes'])}}}")

    lines.extend([
        "",
        r"% ---------- TECHNICAL SKILLS ----------",
        r"\section*{Technical Skills}",
        r"\begin{resumeItemize}",
    ])
    for skill in skills:
        lines.append(f"    \\resumeItem{{\\textbf{{{escape_latex(skill['category'])}:}} {escape_latex(skill['items'])}}}")
    lines.extend([
        r"\end{resumeItemize}",
        "",
        r"% ---------- PROJECTS ----------",
        r"\section*{Featured Projects}",
        "",
    ])

    for proj in projects:
        lines.append(f"\\resumeProject{{{escape_latex(proj['title'])}}}{{{escape_latex(proj['platform'])}}}{{{escape_latex(proj['tech_stack'])}}}")
        lines.append(r"\begin{resumeItemize}")
        for bullet in proj.get("bullets", []):
            lines.append(f"    \\resumeItem{{{escape_latex(bullet)}}}")
        lines.append(r"\end{resumeItemize}")
        lines.append(r"\vspace{4pt}")
        lines.append("")

    lines.extend([
        r"\section*{Technical Experience}",
        r"\begin{resumeItemize}",
    ])
    for exp in experience:
        for bullet in exp.get("bullets", []):
            lines.append(f"    \\resumeItem{{{escape_latex(bullet)}}}")
    lines.extend([
        r"\end{resumeItemize}",
        "",
        r"% ---------- LANGUAGES ----------",
        r"\section*{Languages}",
    ])

    lang_str = " \\quad $\\vert$ \\quad ".join(escape_latex(l) for l in languages)
    lines.append(lang_str)
    lines.extend([
        "",
        r"\end{document}",
        "",
    ])

    return "\n".join(lines)


def build_html(data: dict) -> str:
    """Builds a responsive, high-aesthetic web resume portal for GitHub Pages."""
    personal = data["personal"]
    summary = data.get("summary", "")
    education = data.get("education", [])
    skills = data.get("skills", [])
    projects = data.get("projects", [])
    experience = data.get("experience", [])
    languages = data.get("languages", [])

    skills_html = ""
    for s in skills:
        items = [f'<span class="skill-tag">{item.strip()}</span>' for item in s["items"].split(",")]
        skills_html += f"""
        <div class="skill-group">
            <h4 class="skill-category">{s['category']}</h4>
            <div class="skill-tags">{' '.join(items)}</div>
        </div>
        """

    projects_html = ""
    for p in projects:
        bullets = "".join(f"<li>{b}</li>" for b in p.get("bullets", []))
        projects_html += f"""
        <div class="card project-card">
            <div class="card-header">
                <div>
                    <h3 class="card-title">{p['title']}</h3>
                    <div class="card-platform"><span class="badge">{p['platform']}</span></div>
                </div>
            </div>
            <p class="tech-stack"><strong>Tech Stack:</strong> {p['tech_stack']}</p>
            <ul class="bullet-list">
                {bullets}
            </ul>
        </div>
        """

    edu_html = ""
    for e in education:
        edu_html += f"""
        <div class="card edu-card">
            <div class="card-header">
                <h3 class="card-title">{e['degree']}</h3>
                <span class="period-badge">{e['period']}</span>
            </div>
            <p class="institution">{e['institution']} <span class="score">&bull; {e['score']}</span></p>
            <p class="notes">{e['notes']}</p>
        </div>
        """

    exp_bullets = ""
    for exp in experience:
        for b in exp.get("bullets", []):
            exp_bullets += f"<li>{b}</li>"

    lang_tags = "".join(f'<span class="badge badge-accent">{lang}</span>' for lang in languages)

    portfolio_btn = (
        f'<a href="{personal["portfolio"]}" target="_blank" class="btn btn-secondary">Portfolio</a>'
        if personal.get("portfolio")
        else ""
    )
    portfolio_contact = (
        f'<a href="{personal["portfolio"]}" target="_blank">🌐 {personal.get("portfolio_display", personal["portfolio"])}</a>'
        if personal.get("portfolio")
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personal['name']} | Resume</title>
    <meta name="description" content="Resume of {personal['name']} - {personal['title']}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0e17;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.85);
            --border-color: rgba(0, 212, 255, 0.18);
            --border-hover: rgba(0, 212, 255, 0.45);
            --accent-cyan: #00d4ff;
            --accent-glow: rgba(0, 212, 255, 0.25);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
            --font-main: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}

        [data-theme="light"] {{
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-card: rgba(255, 255, 255, 0.95);
            --border-color: #e2e8f0;
            --border-hover: #00d4ff;
            --accent-cyan: #0077b6;
            --accent-glow: rgba(0, 119, 182, 0.15);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.25s ease, border-color 0.25s ease;
        }}

        body {{
            background-color: var(--bg-primary);
            color: var(--text-primary);
            font-family: var(--font-main);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* Navigation Header */
        header.top-nav {{
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(14px);
            background: rgba(10, 14, 23, 0.8);
            border-bottom: 1px solid var(--border-color);
            padding: 0.85rem 1.5rem;
        }}

        [data-theme="light"] header.top-nav {{
            background: rgba(248, 250, 252, 0.85);
        }}

        .nav-container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .brand-title {{
            font-size: 1.3rem;
            font-weight: 700;
            letter-spacing: -0.5px;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .brand-title span.highlight {{
            color: var(--accent-cyan);
        }}

        .badge-status {{
            font-size: 0.72rem;
            background: rgba(0, 212, 255, 0.12);
            color: var(--accent-cyan);
            border: 1px solid var(--border-color);
            padding: 2px 8px;
            border-radius: 999px;
            font-family: var(--font-mono);
        }}

        .nav-actions {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.88rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.2s ease;
        }}

        .btn-primary {{
            background: linear-gradient(135deg, #00d4ff, #0077b6);
            color: #ffffff;
            box-shadow: 0 4px 14px var(--accent-glow);
        }}

        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px var(--accent-glow);
        }}

        .btn-secondary {{
            background: var(--bg-secondary);
            color: var(--text-primary);
            border-color: var(--border-color);
        }}

        .btn-secondary:hover {{
            border-color: var(--accent-cyan);
            color: var(--accent-cyan);
        }}

        .theme-toggle {{
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
        }}

        .theme-toggle:hover {{
            border-color: var(--accent-cyan);
        }}

        /* View Mode Tabs */
        .tabs-container {{
            max-width: 1200px;
            margin: 1.2rem auto 0;
            padding: 0 1.5rem;
            display: flex;
            gap: 0.5rem;
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 0.5rem 1rem;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            font-family: var(--font-main);
        }}

        .tab-btn.active {{
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
        }}

        /* Main Container */
        main.content-wrap {{
            max-width: 1200px;
            width: 100%;
            margin: 1.5rem auto;
            padding: 0 1.5rem 3rem;
            flex: 1;
        }}

        .view-section {{
            display: none;
        }}

        .view-section.active {{
            display: block;
            animation: fadeIn 0.3s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* PDF Viewer Container */
        .pdf-frame-wrapper {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
            height: 85vh;
            position: relative;
        }}

        .pdf-frame {{
            width: 100%;
            height: 100%;
            border: none;
        }}

        /* Web Resume Aesthetic */
        .resume-paper {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 2.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(10px);
        }}

        .resume-header {{
            text-align: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }}

        .resume-header h1 {{
            font-size: 2.3rem;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.5px;
        }}

        .resume-subtitle {{
            font-size: 1.05rem;
            color: var(--accent-cyan);
            font-weight: 500;
            margin-top: 0.3rem;
        }}

        .contact-links {{
            margin-top: 0.8rem;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1.2rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }}

        .contact-links a {{
            color: var(--text-primary);
            text-decoration: none;
        }}

        .contact-links a:hover {{
            color: var(--accent-cyan);
            text-decoration: underline;
        }}

        section.resume-sec {{
            margin-bottom: 2rem;
        }}

        .section-heading {{
            font-size: 1.15rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
            color: var(--text-primary);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 0.3rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .section-heading::before {{
            content: "";
            display: inline-block;
            width: 4px;
            height: 16px;
            background: var(--accent-cyan);
            border-radius: 2px;
        }}

        .summary-text {{
            color: var(--text-secondary);
            font-size: 0.98rem;
            line-height: 1.7;
        }}

        .card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }}

        .card:hover {{
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
        }}

        .card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .badge {{
            font-size: 0.75rem;
            font-family: var(--font-mono);
            background: rgba(0, 212, 255, 0.1);
            color: var(--accent-cyan);
            border: 1px solid var(--border-color);
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 600;
        }}

        .period-badge {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        .tech-stack {{
            font-size: 0.88rem;
            color: var(--accent-cyan);
            font-family: var(--font-mono);
            margin-bottom: 0.75rem;
        }}

        .bullet-list {{
            list-style: disc inside;
            color: var(--text-secondary);
            font-size: 0.93rem;
            margin-left: 0.5rem;
        }}

        .bullet-list li {{
            margin-bottom: 0.4rem;
        }}

        .skill-group {{
            margin-bottom: 1rem;
        }}

        .skill-category {{
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.4rem;
        }}

        .skill-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }}

        .skill-tag {{
            font-size: 0.82rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 3px 10px;
            border-radius: 6px;
        }}

        footer.site-footer {{
            border-top: 1px solid var(--border-color);
            text-align: center;
            padding: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        @media (max-width: 768px) {{
            .resume-paper {{
                padding: 1.5rem;
            }}
            .card-header {{
                flex-direction: column;
                gap: 0.3rem;
            }}
            .pdf-frame-wrapper {{
                height: 65vh;
            }}
        }}
    </style>
</head>
<body>

    <!-- Header Navigation -->
    <header class="top-nav">
        <div class="nav-container">
            <div class="brand-title">
                <span>{personal['name']}</span>
                <span class="highlight">/ Resume</span>
                <span class="badge-status">CI/CD Automated</span>
            </div>
            <div class="nav-actions">
                <a href="resume.pdf" download="Barath_R_Resume.pdf" class="btn btn-primary" id="btn-download">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg>
                    Download PDF
                </a>
                <a href="resume.pdf" target="_blank" class="btn btn-secondary">
                    Open PDF Tab
                </a>
                <a href="{personal['github']}" target="_blank" class="btn btn-secondary">
                    GitHub Profile
                </a>
                {portfolio_btn}
                <button class="theme-toggle" id="theme-btn" title="Toggle Dark/Light Mode">🌓</button>
            </div>
        </div>
    </header>

    <!-- View Tabs -->
    <div class="tabs-container">
        <button class="tab-btn active" onclick="switchView('pdf-view', this)">PDF Document</button>
        <button class="tab-btn" onclick="switchView('web-view', this)">Interactive Web Resume</button>
    </div>

    <!-- Main Content Area -->
    <main class="content-wrap">
        <!-- PDF Viewer View -->
        <section id="pdf-view" class="view-section active">
            <div class="pdf-frame-wrapper">
                <iframe src="resume.pdf#toolbar=1" class="pdf-frame" title="Barath R Resume PDF">
                    <p style="padding: 2rem; text-align: center;">
                        Your browser does not support embedded PDFs.
                        <a href="resume.pdf" target="_blank">Click here to download/view the PDF</a>.
                    </p>
                </iframe>
            </div>
        </section>

        <!-- Web Resume View -->
        <section id="web-view" class="view-section">
            <article class="resume-paper">
                <header class="resume-header">
                    <h1>{personal['name']}</h1>
                    <p class="resume-subtitle">{personal['title']}</p>
                    <div class="contact-links">
                        <span>📍 {personal['location']}</span>
                        <span>📞 {personal['phone']}</span>
                        <a href="mailto:{personal['email']}">✉️ {personal['email']}</a>
                        <a href="{personal['github']}" target="_blank">💻 {personal['github_display']}</a>
                        <a href="{personal['linkedin']}" target="_blank">🔗 {personal['linkedin_display']}</a>
                        {portfolio_contact}
                    </div>
                </header>

                <!-- Professional Summary -->
                <section class="resume-sec">
                    <h2 class="section-heading">Professional Summary</h2>
                    <p class="summary-text">{summary}</p>
                </section>

                <!-- Education -->
                <section class="resume-sec">
                    <h2 class="section-heading">Education</h2>
                    {edu_html}
                </section>

                <!-- Technical Skills -->
                <section class="resume-sec">
                    <h2 class="section-heading">Technical Skills</h2>
                    {skills_html}
                </section>

                <!-- Featured Projects -->
                <section class="resume-sec">
                    <h2 class="section-heading">Featured Projects</h2>
                    {projects_html}
                </section>

                <!-- Technical Experience -->
                <section class="resume-sec">
                    <h2 class="section-heading">Technical Experience</h2>
                    <div class="card">
                        <ul class="bullet-list">
                            {exp_bullets}
                        </ul>
                    </div>
                </section>

                <!-- Languages -->
                <section class="resume-sec">
                    <h2 class="section-heading">Languages</h2>
                    <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
                        {lang_tags}
                    </div>
                </section>
            </article>
        </section>
    </main>

    <footer class="site-footer">
        <p>Built with automated GitHub Actions &bull; Generated from structured <code>resume.json</code> &bull; Host: GitHub Pages</p>
    </footer>

    <script>
        function switchView(viewId, btn) {{
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');
            btn.classList.add('active');
        }}

        // Theme Toggle
        const themeBtn = document.getElementById('theme-btn');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        let currentTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', currentTheme);

        themeBtn.addEventListener('click', () => {{
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', currentTheme);
            localStorage.setItem('theme', currentTheme);
        }});
    </script>
</body>
</html>
"""


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Generate resume.tex
    tex_content = build_latex(data)
    OUTPUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_TEX, "w", encoding="utf-8") as f:
        f.write(tex_content)
    print(f"Generated LaTeX: {OUTPUT_TEX}")

    # 2. Generate dist/index.html
    html_content = build_html(data)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated Web Portal: {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
