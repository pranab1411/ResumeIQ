"""
modules/portfolio_generator.py
Portfolio Generator Engine for ResumeIQ v2.0.
Auto-populates personal website portfolio from ResumeData.
Supports HTML Portfolio, React SPA Scaffold, and GitHub Pages deployment configuration.
"""

import os
import json
from typing import Dict, Any, Optional
from utils.logger import logger
from utils.paths import get_data_path
from modules.resume_data import ResumeData

class PortfolioGenerator:
    TEMPLATES = ["Minimal HTML", "Personal Website", "React SPA Scaffold"]

    @classmethod
    def generate_portfolio(
        cls,
        resume_data: ResumeData,
        template_name: str = "Minimal HTML",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates full portfolio package based on chosen template.
        """
        if not output_dir:
            output_dir = os.path.join(get_data_path("reports"), "portfolio")
        os.makedirs(output_dir, exist_ok=True)

        if template_name == "React SPA Scaffold":
            return cls._generate_react_scaffold(resume_data, output_dir)
        else:
            return cls._generate_html_portfolio(resume_data, output_dir)

    @classmethod
    def _generate_html_portfolio(cls, rdata: ResumeData, output_dir: str) -> Dict[str, Any]:
        try:
            from jinja2 import Environment, FileSystemLoader
            tpl_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "portfolio_templates")
            env = Environment(loader=FileSystemLoader(tpl_dir))
            tpl = env.get_template("minimal_html.html")

            context = rdata.to_dict()
            html_out = tpl.render(**context)

            index_path = os.path.join(output_dir, "index.html")
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_out)

            # Generate GitHub Pages workflow
            cls._generate_github_pages_config(output_dir)

            logger.info(f"[PortfolioGenerator] Generated HTML portfolio: {index_path}")
            return {"success": True, "path": index_path, "type": "HTML", "output_dir": output_dir}
        except Exception as e:
            logger.error(f"[PortfolioGenerator] Failed HTML portfolio generation: {e}")
            return {"success": False, "error": str(e)}

    @classmethod
    def _generate_react_scaffold(cls, rdata: ResumeData, output_dir: str) -> Dict[str, Any]:
        try:
            src_dir = os.path.join(output_dir, "src")
            os.makedirs(src_dir, exist_ok=True)

            # package.json
            pkg = {
                "name": f"{rdata.candidate_name.lower().replace(' ', '-')}-portfolio",
                "version": "1.0.0",
                "private": True,
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                },
                "scripts": {
                    "start": "react-scripts start",
                    "build": "react-scripts build"
                }
            }
            with open(os.path.join(output_dir, "package.json"), "w", encoding="utf-8") as f:
                json.dump(pkg, f, indent=2)

            # App.js
            app_js = f"""import React from 'react';

const data = {json.dumps(rdata.to_dict(), indent=2)};

export default function App() {{
  return (
    <div style={{{{ padding: '40px', fontFamily: 'sans-serif', background: '#0F172A', color: '#FFF', minHeight: '100vh' }}}}>
      <h1>{{data.candidate_name}}</h1>
      <p>{{data.email}} | {{data.phone}}</p>
      <h2>Skills</h2>
      <ul>
        {{data.skills.map((s, i) => <li key={{i}}>{{s}}</li>)}}
      </ul>
    </div>
  );
}}
"""
            with open(os.path.join(src_dir, "App.js"), "w", encoding="utf-8") as f:
                f.write(app_js)

            cls._generate_github_pages_config(output_dir)

            logger.info(f"[PortfolioGenerator] Generated React scaffold at: {output_dir}")
            return {"success": True, "path": output_dir, "type": "React SPA", "output_dir": output_dir}
        except Exception as e:
            logger.error(f"[PortfolioGenerator] React scaffold generation failed: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def _generate_github_pages_config(output_dir: str):
        workflows_dir = os.path.join(output_dir, ".github", "workflows")
        os.makedirs(workflows_dir, exist_ok=True)
        yml_content = """name: Deploy Portfolio to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
"""
        with open(os.path.join(workflows_dir, "deploy.yml"), "w", encoding="utf-8") as f:
            f.write(yml_content)
