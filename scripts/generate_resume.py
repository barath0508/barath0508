#!/usr/bin/env python3
"""
Resume Generator Script
- Reads resume/resume.json and resume/resume_full.json
- Renders resume/resume.tex and resume/resume_full.tex (with robust LaTeX escaping)
- Generates an interactive GitHub Pages web portal in dist/index.html (dual-resume support)
- Generates standalone printable HTML resumes in resume/resume_full.html & dist/resume_full.html
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
DATA_FILE_FULL = RESUME_DIR / "resume_full.json"

OUTPUT_TEX = RESUME_DIR / "resume.tex"
OUTPUT_TEX_FULL = RESUME_DIR / "resume_full.tex"

OUTPUT_HTML = DIST_DIR / "index.html"
OUTPUT_HTML_FULL = DIST_DIR / "resume_full.html"
OUTPUT_HTML_FULL_RESUME = RESUME_DIR / "resume_full.html"
OUTPUT_HTML_DEFAULT = DIST_DIR / "resume.html"
OUTPUT_HTML_DEFAULT_RESUME = RESUME_DIR / "resume.html"


def escape_latex(text: str) -> str:
    """Escapes special characters in text for LaTeX compatibility."""
    if not isinstance(text, str):
        return str(text)

    # Don't escape if it looks like intentional LaTeX command
    if text.startswith("\\") and "{" in text:
        return text

    # Standard LaTeX replacements
    text = re.sub(r'(?<!\\)&', r'\&', text)
    text = re.sub(r'(?<!\\)%', r'\%', text)
    text = re.sub(r'(?<!\\)#', r'\#', text)
    text = re.sub(r'(?<!\\)_', r'\_', text)
    # Replace vertical bar separators with LaTeX vert symbol
    text = re.sub(r'\s*\|\s*', r' $\\vert$ ', text)

    return text


def build_latex(data: dict, compact: bool = False) -> str:
    """Renders resume.tex matching Barath's LaTeX template with auto-fit margins."""
    personal = data["personal"]
    summary = escape_latex(data.get("summary", ""))
    education = data.get("education", [])
    skills = data.get("skills", [])
    projects = data.get("projects", [])
    experience = data.get("experience", [])
    languages = data.get("languages", [])

    fontsize = "9.5pt" if compact else "10pt"
    margin = "0.33in" if compact else "0.42in"
    sec_top_space = "3.2pt" if compact else "5pt"
    sec_bot_space = "1.2pt" if compact else "2pt"
    item_sep = "0.2pt" if compact else "0.5pt"
    top_sep = "0.4pt" if compact else "0.8pt"
    proj_vspace = "1.0pt" if compact else "1.6pt"

    contact_row_2 = f"\\href{{{personal['github']}}}{{{personal['github_display']}}} $\\vert$ \\href{{{personal['linkedin']}}}{{{personal['linkedin_display']}}}"
    if personal.get("portfolio"):
        contact_row_2 += f" $\\vert$ \\href{{{personal['portfolio']}}}{{{personal.get('portfolio_display', personal['portfolio'])}}}"

    lines = [
        f"\\documentclass[a4paper,{fontsize}]{{article}}",
        "",
        f"\\usepackage[margin={margin}]{{geometry}}",
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
        f"\\titlespacing{{\\section}}{{0pt}}{{{sec_top_space}}}{{{sec_bot_space}}}",
        "",
        r"\newcommand{\resumeItem}[1]{\item #1}",
        f"\\newenvironment{{resumeItemize}}{{\\begin{{itemize}}[leftmargin=*, itemsep={item_sep}, topsep={top_sep}]}}{{\\end{{itemize}}}}",
        "",
        r"\newcommand{\resumeProject}[3]{",
        r"  \textbf{#1} \hfill \textit{#2} \\",
        r"  \textit{Tech Stack: #3}",
        r"}",
        "",
        r"\newcommand{\resumeSubSection}[1]{%",
        r"  \vspace{3pt}%",
        r"  \noindent\textbf{\textcolor{darkblue}{#1}}\par\vspace{1.5pt}%",
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

    for i, edu in enumerate(education):
        lines.append(f"\\textbf{{{escape_latex(edu['degree'])}}} \\hfill {edu['period']} \\\\")
        notes = edu.get("notes", "")
        if notes:
            lines.append(f"{escape_latex(edu['institution'])} \\hfill {escape_latex(edu['score'])} \\\\")
            if i < len(education) - 1:
                lines.append(f"\\textit{{{escape_latex(notes)}}} \\\\[2pt]")
            else:
                lines.append(f"\\textit{{{escape_latex(notes)}}}")
        else:
            if i < len(education) - 1:
                lines.append(f"{escape_latex(edu['institution'])} \\hfill {escape_latex(edu['score'])} \\\\[2pt]")
            else:
                lines.append(f"{escape_latex(edu['institution'])} \\hfill {escape_latex(edu['score'])}")

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

    current_cat = None
    for proj in projects:
        cat = proj.get("category")
        if cat and cat != current_cat:
            current_cat = cat
            lines.append(f"\\resumeSubSection{{{escape_latex(current_cat)}}}")
        lines.append(f"\\resumeProject{{{escape_latex(proj['title'])}}}{{{escape_latex(proj['platform'])}}}{{{escape_latex(proj['tech_stack'])}}}")
        lines.append(r"\begin{resumeItemize}")
        for bullet in proj.get("bullets", []):
            lines.append(f"    \\resumeItem{{{escape_latex(bullet)}}}")
        lines.append(r"\end{resumeItemize}")
        lines.append(f"\\vspace{{{proj_vspace}}}")
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
    ])

    if languages:
        lines.extend([
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


def render_resume_card_html(data: dict, variant_id: str) -> str:
    """Renders the HTML article markup for a specific resume variant."""
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
    current_cat = None
    for p in projects:
        cat = p.get("category")
        if cat and cat != current_cat:
            current_cat = cat
            icon = "⚡" if ("Hardware" in cat or "Embedded" in cat) else "💻"
            projects_html += f"""
            <div class="project-group-banner">
                <span class="group-icon">{icon}</span>
                <span class="group-title">{cat}</span>
            </div>
            """
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
        notes_html = f'<p class="notes">{e["notes"]}</p>' if e.get("notes") else ""
        edu_html += f"""
        <div class="card edu-card">
            <div class="card-header">
                <h3 class="card-title">{e['degree']}</h3>
                <span class="period-badge">{e['period']}</span>
            </div>
            <p class="institution">{e['institution']} <span class="score">&bull; {e['score']}</span></p>
            {notes_html}
        </div>
        """

    exp_bullets = ""
    for exp in experience:
        for b in exp.get("bullets", []):
            exp_bullets += f"<li>{b}</li>"

    lang_tags = "".join(f'<span class="badge badge-accent">{lang}</span>' for lang in languages)

    portfolio_contact = (
        f'<a href="{personal["portfolio"]}" target="_blank">🌐 {personal.get("portfolio_display", personal["portfolio"])}</a>'
        if personal.get("portfolio")
        else ""
    )

    languages_sec = (
        f"""
        <!-- Languages -->
        <section class="resume-sec">
            <h2 class="section-heading">Languages</h2>
            <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
                {lang_tags}
            </div>
        </section>
        """
        if languages
        else ""
    )

    return f"""
    <article class="resume-paper" id="resume-article-{variant_id}">
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
        {languages_sec}
    </article>
    """


def build_portal_html(data_default: dict, data_full: dict) -> str:
    """Builds a responsive, high-aesthetic web resume portal for GitHub Pages with dual-resume switching."""
    personal = data_full["personal"]

    portfolio_btn = (
        f'<a href="{personal["portfolio"]}" target="_blank" class="btn btn-secondary">Portfolio</a>'
        if personal.get("portfolio")
        else ""
    )

    article_default = render_resume_card_html(data_default, "default")
    article_full = render_resume_card_html(data_full, "full")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personal['name']} | Resume Portal</title>
    <meta name="description" content="Resume of {personal['name']} - Embedded Engineer & IoT Developer">
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
            background: rgba(10, 14, 23, 0.85);
            border-bottom: 1px solid var(--border-color);
            padding: 0.85rem 1.5rem;
        }}

        [data-theme="light"] header.top-nav {{
            background: rgba(248, 250, 252, 0.88);
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
            font-size: 1.25rem;
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
            gap: 0.65rem;
            flex-wrap: wrap;
        }}

        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.48rem 0.95rem;
            border-radius: 8px;
            font-size: 0.86rem;
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
            padding: 0.48rem 0.75rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
        }}

        .theme-toggle:hover {{
            border-color: var(--accent-cyan);
        }}

        /* Control Panel: Resume Profile & Format Switches */
        .controls-wrapper {{
            max-width: 1200px;
            margin: 1.2rem auto 0;
            padding: 0 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .profile-selector {{
            display: flex;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 4px;
            gap: 4px;
        }}

        .profile-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 0.45rem 1rem;
            border-radius: 7px;
            font-size: 0.88rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: var(--font-main);
        }}

        .profile-btn.active {{
            background: rgba(0, 212, 255, 0.16);
            color: var(--accent-cyan);
            box-shadow: 0 2px 8px var(--accent-glow);
        }}

        .view-tabs {{
            display: flex;
            gap: 0.5rem;
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 0.5rem 1rem;
            font-size: 0.92rem;
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
            font-weight: 600;
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

        .project-group-banner {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin: 1.8rem 0 0.9rem 0;
            padding: 0.55rem 1rem;
            background: rgba(0, 212, 255, 0.08);
            border-left: 3px solid var(--accent-cyan);
            border-radius: 0 8px 8px 0;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .project-group-banner .group-icon {{
            font-size: 1.15rem;
        }}

        .project-group-banner .group-title {{
            letter-spacing: -0.2px;
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
            .controls-wrapper {{
                flex-direction: column;
                align-items: stretch;
            }}
            .profile-selector {{
                justify-content: center;
            }}
            .view-tabs {{
                justify-content: center;
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
                <a href="resume_full.pdf" download="Barath_R_Resume_Full.pdf" class="btn btn-primary" id="btn-download">
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg>
                    <span id="btn-download-text">Download Full PDF</span>
                </a>
                <a href="resume_full.pdf" target="_blank" class="btn btn-secondary" id="btn-open-tab">
                    Open PDF Tab
                </a>
                <a href="resume_full.html" target="_blank" class="btn btn-secondary" id="btn-printable" title="View print-ready HTML resume">
                    Printable HTML
                </a>
                <a href="{personal['github']}" target="_blank" class="btn btn-secondary">
                    GitHub
                </a>
                {portfolio_btn}
                <button class="theme-toggle" id="theme-btn" title="Toggle Dark/Light Mode">🌓</button>
            </div>
        </div>
    </header>

    <!-- Controls: Profile Selector & View Mode Tabs -->
    <div class="controls-wrapper">
        <div class="profile-selector">
            <button class="profile-btn active" id="pbtn-full" onclick="switchProfile('full')">
                Embedded Engineer (HW + SW)
            </button>
            <button class="profile-btn" id="pbtn-default" onclick="switchProfile('default')">
                Embedded & IoT (Specialized)
            </button>
        </div>
        <div class="view-tabs">
            <button class="tab-btn active" id="tbtn-pdf" onclick="switchFormat('pdf')">PDF Document</button>
            <button class="tab-btn" id="tbtn-web" onclick="switchFormat('web')">Interactive Web View</button>
        </div>
    </div>

    <!-- Main Content Area -->
    <main class="content-wrap">
        <!-- PDF Viewer View -->
        <section id="pdf-view" class="view-section active">
            <div class="pdf-frame-wrapper">
                <iframe src="resume_full.pdf#toolbar=1" class="pdf-frame" id="pdf-iframe" title="Barath R Resume PDF">
                    <p style="padding: 2rem; text-align: center;">
                        Your browser does not support embedded PDFs.
                        <a href="resume_full.pdf" target="_blank" id="pdf-fallback-link">Click here to download/view the PDF</a>.
                    </p>
                </iframe>
            </div>
        </section>

        <!-- Web Resume View -->
        <section id="web-view" class="view-section">
            <div id="web-content-full">
                {article_full}
            </div>
            <div id="web-content-default" style="display: none;">
                {article_default}
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <p>Built with automated GitHub Actions &bull; Generated from structured <code>resume_full.json</code> &amp; <code>resume.json</code> &bull; Host: GitHub Pages</p>
    </footer>

    <script>
        let currentProfile = 'full'; // 'full' | 'default'
        let currentFormat = 'pdf';   // 'pdf' | 'web'

        const pdfMap = {{
            'full': {{
                'file': 'resume_full.pdf',
                'html': 'resume_full.html',
                'download': 'Barath_R_Resume_Full.pdf',
                'label': 'Download Full PDF'
            }},
            'default': {{
                'file': 'resume.pdf',
                'html': 'resume.html',
                'download': 'Barath_R_Resume_Embedded_IoT.pdf',
                'label': 'Download Embedded PDF'
            }}
        }};

        function updateDisplay() {{
            // 1. Profile buttons
            document.getElementById('pbtn-full').classList.toggle('active', currentProfile === 'full');
            document.getElementById('pbtn-default').classList.toggle('active', currentProfile === 'default');

            // 2. Format buttons & view sections
            document.getElementById('tbtn-pdf').classList.toggle('active', currentFormat === 'pdf');
            document.getElementById('tbtn-web').classList.toggle('active', currentFormat === 'web');
            document.getElementById('pdf-view').classList.toggle('active', currentFormat === 'pdf');
            document.getElementById('web-view').classList.toggle('active', currentFormat === 'web');

            // 3. Web article visibility
            document.getElementById('web-content-full').style.display = currentProfile === 'full' ? 'block' : 'none';
            document.getElementById('web-content-default').style.display = currentProfile === 'default' ? 'block' : 'none';

            // 4. Update PDF iframe & action links
            const info = pdfMap[currentProfile];
            const iframe = document.getElementById('pdf-iframe');
            if (iframe && iframe.getAttribute('src') !== info.file + '#toolbar=1') {{
                iframe.src = info.file + '#toolbar=1';
            }}
            const fallback = document.getElementById('pdf-fallback-link');
            if (fallback) fallback.href = info.file;

            const btnDl = document.getElementById('btn-download');
            if (btnDl) {{
                btnDl.href = info.file;
                btnDl.setAttribute('download', info.download);
                document.getElementById('btn-download-text').innerText = info.label;
            }}

            const btnOpen = document.getElementById('btn-open-tab');
            if (btnOpen) btnOpen.href = info.file;

            const btnPrint = document.getElementById('btn-printable');
            if (btnPrint) btnPrint.href = info.html;
        }}

        function switchProfile(profile) {{
            currentProfile = profile;
            updateDisplay();
        }}

        function switchFormat(fmt) {{
            currentFormat = fmt;
            updateDisplay();
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


def build_standalone_print_html(data: dict, compact: bool = False) -> str:
    """Generates an elegant, print-optimized A4 HTML resume with clean typography and instant Ctrl+P support."""
    personal = data["personal"]
    summary = data.get("summary", "")
    education = data.get("education", [])
    skills = data.get("skills", [])
    projects = data.get("projects", [])
    experience = data.get("experience", [])
    languages = data.get("languages", [])

    page_margin = "4.5mm 9mm 4.5mm 9mm" if compact else "8mm 11mm 8mm 11mm"
    body_size = "8.1pt" if compact else "8.9pt"
    body_lh = "1.21" if compact else "1.29"
    header_mb = "3.5px" if compact else "8px"
    sec_title_mt = "3px" if compact else "7px"
    sec_title_mb = "1.2px" if compact else "2.5px"
    edu_proj_mb = "1.2px" if compact else "3.2px"
    bullet_mb = "0.3px" if compact else "0.8px"
    name_size = "16.5pt" if compact else "19.5pt"
    title_size = "9.2pt" if compact else "10.5pt"
    contact_size = "8.1pt" if compact else "8.8pt"
    sec_title_size = "9.2pt" if compact else "9.8pt"
    bullet_size = "8.1pt" if compact else "8.8pt"
    skill_size = "8.2pt" if compact else "9.0pt"
    stack_size = "7.8pt" if compact else "8.5pt"

    skills_rows = ""
    for s in skills:
        skills_rows += f"""
        <div class="skill-line">
            <span class="skill-name">{s['category']}:</span>
            <span class="skill-val">{s['items']}</span>
        </div>
        """

    projects_rows = ""
    current_cat = None
    for p in projects:
        cat = p.get("category")
        if cat and cat != current_cat:
            current_cat = cat
            projects_rows += f"""
            <div class="proj-group-title">{cat}</div>
            """
        bullets = "".join(f"<li>{b}</li>" for b in p.get("bullets", []))
        projects_rows += f"""
        <div class="proj-item">
            <div class="proj-head">
                <span class="proj-title">{p['title']}</span>
                <span class="proj-plat">{p['platform']}</span>
            </div>
            <div class="proj-stack">Tech Stack: {p['tech_stack']}</div>
            <ul class="proj-bullets">
                {bullets}
            </ul>
        </div>
        """

    edu_rows = ""
    for e in education:
        notes_div = f'<div class="edu-notes">{e["notes"]}</div>' if e.get("notes") else ""
        edu_rows += f"""
        <div class="edu-item">
            <div class="edu-head">
                <span class="edu-deg">{e['degree']}</span>
                <span class="edu-period">{e['period']}</span>
            </div>
            <div class="edu-sub">
                <span>{e['institution']}</span>
                <span class="edu-score">{e['score']}</span>
            </div>
            {notes_div}
        </div>
        """

    exp_bullets = ""
    for exp in experience:
        for b in exp.get("bullets", []):
            exp_bullets += f"<li>{b}</li>"

    languages_sec = (
        f"""
        <div class="sec-title">Languages</div>
        <div class="languages-line">{" &nbsp;&bull;&nbsp; ".join(languages)}</div>
        """
        if languages
        else ""
    )

    portfolio_link = (
        f'<a href="{personal["portfolio"]}" target="_blank">{personal.get("portfolio_display", personal["portfolio"])}</a>'
        if personal.get("portfolio")
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personal['name']} - {personal['title']}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: A4;
            margin: {page_margin};
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: {body_size};
            line-height: {body_lh};
            color: #1a1a1a;
            background: #ffffff;
        }}

        .print-btn-bar {{
            background: #0f172a;
            color: #ffffff;
            padding: 10px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }}

        .print-btn {{
            background: #00d4ff;
            color: #000000;
            border: none;
            padding: 6px 14px;
            font-weight: 700;
            border-radius: 6px;
            cursor: pointer;
        }}

        .page-wrap {{
            max-width: 820px;
            margin: 0 auto;
            padding: 24px 28px;
            background: #ffffff;
        }}

        header.header {{
            text-align: center;
            margin-bottom: {header_mb};
        }}

        h1.name {{
            font-size: {name_size};
            font-weight: 700;
            letter-spacing: -0.3px;
            color: #111827;
            margin-bottom: 2px;
        }}

        .title {{
            font-size: {title_size};
            font-weight: 600;
            color: #0369a1;
            margin-bottom: 3px;
        }}

        .contact-line {{
            font-size: {contact_size};
            color: #4b5563;
        }}

        .contact-line a {{
            color: #111827;
            text-decoration: none;
        }}

        .contact-line a:hover {{
            text-decoration: underline;
        }}

        .sec-title {{
            font-size: {sec_title_size};
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: #111827;
            border-bottom: 1.2px solid #111827;
            padding-bottom: 1.5px;
            margin-top: {sec_title_mt};
            margin-bottom: {sec_title_mb};
        }}

        .summary-p {{
            text-align: justify;
            color: #27272a;
            margin-bottom: 3px;
            font-size: {bullet_size};
        }}

        .edu-item, .proj-item {{
            margin-bottom: {edu_proj_mb};
        }}

        .edu-head, .proj-head {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }}

        .edu-deg, .proj-title {{
            font-weight: 700;
            color: #09090b;
            font-size: {bullet_size};
        }}

        .edu-period, .proj-plat {{
            font-style: italic;
            color: #4b5563;
            font-size: 8.5pt;
        }}

        .edu-sub {{
            display: flex;
            justify-content: space-between;
            font-size: 8.5pt;
            color: #374151;
        }}

        .edu-score {{
            font-weight: 600;
        }}

        .edu-notes {{
            font-size: 8pt;
            font-style: italic;
            color: #6b7280;
        }}

        .skill-line {{
            margin-bottom: 1.8px;
            font-size: {skill_size};
        }}

        .skill-name {{
            font-weight: 700;
            color: #18181b;
        }}

        .skill-val {{
            color: #374151;
        }}

        .proj-stack {{
            font-size: {stack_size};
            font-style: italic;
            color: #0284c7;
            margin-bottom: 1.5px;
        }}

        ul.proj-bullets, ul.exp-bullets {{
            list-style: disc outside;
            margin-left: 18px;
            color: #27272a;
        }}

        ul.proj-bullets li, ul.exp-bullets li {{
            margin-bottom: {bullet_mb};
            font-size: {bullet_size};
        }}

        .languages-line {{
            font-size: 9.2pt;
            color: #27272a;
        }}

        .proj-group-title {{
            font-size: 9.3pt;
            font-weight: 700;
            color: #0369a1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 8px;
            margin-bottom: 4px;
            padding-bottom: 2px;
            border-bottom: 1px dashed #cbd5e1;
            break-after: avoid;
            page-break-after: avoid;
        }}

        .proj-item, .edu-item, .card {{
            break-inside: avoid;
            page-break-inside: avoid;
        }}

        .sec-title {{
            break-after: avoid;
            page-break-after: avoid;
        }}

        @media print {{
            .print-btn-bar {{
                display: none !important;
            }}
            .page-wrap {{
                padding: 0;
                margin: 0;
                max-width: 100%;
            }}
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="print-btn-bar">
        <span>Barath R - Embedded Engineer Resume (Printable Preview)</span>
        <button class="print-btn" onclick="window.print()">Print / Save as PDF (Ctrl+P)</button>
    </div>

    <div class="page-wrap">
        <header class="header">
            <h1 class="name">{personal['name']}</h1>
            <div class="title">{personal['title']}</div>
            <div class="contact-line">
                {personal['location']} &nbsp;|&nbsp; {personal['phone']} &nbsp;|&nbsp; <a href="mailto:{personal['email']}">{personal['email']}</a>
            </div>
            <div class="contact-line">
                <a href="{personal['github']}">{personal['github_display']}</a> &nbsp;|&nbsp;
                <a href="{personal['linkedin']}">{personal['linkedin_display']}</a> &nbsp;|&nbsp;
                {portfolio_link}
            </div>
        </header>

        <div class="sec-title">Professional Summary</div>
        <p class="summary-p">{summary}</p>

        <div class="sec-title">Education</div>
        {edu_rows}

        <div class="sec-title">Technical Skills</div>
        {skills_rows}

        <div class="sec-title">Featured Projects</div>
        {projects_rows}

        <div class="sec-title">Technical Experience</div>
        <ul class="exp-bullets">
            {exp_bullets}
        </ul>
        {languages_sec}
    </div>
</body>
</html>
"""


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE}")
    if not DATA_FILE_FULL.exists():
        raise FileNotFoundError(f"Missing {DATA_FILE_FULL}")

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data_default = json.load(f)

    with open(DATA_FILE_FULL, "r", encoding="utf-8") as f:
        data_full = json.load(f)

    # 1. Generate resume.tex (Specialized Embedded & IoT)
    tex_default = build_latex(data_default, compact=True)
    OUTPUT_TEX.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_TEX, "w", encoding="utf-8") as f:
        f.write(tex_default)
    print(f"Generated LaTeX (Embedded): {OUTPUT_TEX}")

    # 2. Generate resume_full.tex (Embedded Engineer HW + SW)
    tex_full = build_latex(data_full, compact=False)
    with open(OUTPUT_TEX_FULL, "w", encoding="utf-8") as f:
        f.write(tex_full)
    print(f"Generated LaTeX (Full HW & SW): {OUTPUT_TEX_FULL}")

    # 3. Generate dist/index.html (Interactive dual-resume portal)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    portal_html = build_portal_html(data_default, data_full)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(portal_html)
    print(f"Generated Web Portal: {OUTPUT_HTML}")

    # 4. Generate standalone printable HTML resumes
    print_html_full = build_standalone_print_html(data_full, compact=False)
    with open(OUTPUT_HTML_FULL, "w", encoding="utf-8") as f:
        f.write(print_html_full)
    with open(OUTPUT_HTML_FULL_RESUME, "w", encoding="utf-8") as f:
        f.write(print_html_full)

    print_html_default = build_standalone_print_html(data_default, compact=True)
    with open(OUTPUT_HTML_DEFAULT, "w", encoding="utf-8") as f:
        f.write(print_html_default)
    with open(OUTPUT_HTML_DEFAULT_RESUME, "w", encoding="utf-8") as f:
        f.write(print_html_default)
    print(f"Generated Printable Resumes: {OUTPUT_HTML_FULL} & {OUTPUT_HTML_DEFAULT}")

    # 5. Automatically compile PDFs locally via headless Chrome / Edge if available
    browser_paths = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    browser_exe = next((p for p in browser_paths if p.exists()), None)
    if browser_exe:
        import subprocess
        import shutil
        import tempfile
        pdf_targets = [
            (OUTPUT_HTML_FULL_RESUME, RESUME_DIR / "resume_full.pdf"),
            (OUTPUT_HTML_DEFAULT_RESUME, RESUME_DIR / "resume.pdf"),
        ]
        for src_html, target_pdf in pdf_targets:
            temp_profile = tempfile.mkdtemp(prefix="browser_pdf_")
            try:
                cmd = [
                    str(browser_exe),
                    "--headless",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    f"--user-data-dir={temp_profile}",
                    f"--print-to-pdf={target_pdf}",
                    str(src_html),
                ]
                subprocess.run(cmd, check=True, timeout=15)
                shutil.copy(target_pdf, DIST_DIR / target_pdf.name)
                shutil.copy(target_pdf, ROOT_DIR / target_pdf.name)
                print(f"Generated PDF (via {browser_exe.name}): {target_pdf}")
            except Exception as e:
                print(f"Note: Local PDF generation for {target_pdf.name} skipped ({e})")
            finally:
                shutil.rmtree(temp_profile, ignore_errors=True)


if __name__ == "__main__":
    main()
