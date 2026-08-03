import re
from typing import Dict, Any, List, Optional
from utils.logger import logger

class AICareerChatbot:
    """
    Autonomous Local AI Career & Resume Assistant.
    Provides instant, context-aware resume optimization, ATS scoring guidance,
    formatting advice, and interview preparation tips — 100% free and offline.
    """
    def __init__(self):
        logger.info("Initialized AI Career Chatbot Engine.")

    def get_response(self, user_query: str, context_data: Optional[Dict[str, Any]] = None) -> str:
        query = user_query.strip().lower()
        if not query:
            return "How can I assist you with your resume or job application today?"

        # Extract context variables if available
        candidate_name = context_data.get("candidate_name", "Candidate") if context_data else "Candidate"
        ats_score = context_data.get("ats_score", None) if context_data else None
        missing_skills = context_data.get("missing_skills", []) if context_data else []
        matched_skills = context_data.get("matched_skills", []) if context_data else []
        job_title = context_data.get("job_title", "") if context_data else ""
        mode = context_data.get("mode", "experienced") if context_data else "experienced"

        # 1. Greetings & System Intro
        if any(w in query for w in ["hi", "hello", "hey", "who are you", "what can you do"]):
            return (
                f"Hello {candidate_name}! 👋 I am your AI Career Assistant.\n\n"
                f"I can help you with:\n"
                f"• Boosting your ATS score & matching Job Descriptions\n"
                f"• Formatting font sizes, margins, and section structure\n"
                f"• Writing impactful project bullet points with action verbs\n"
                f"• Tailoring resumes for Fresher vs Experienced roles\n\n"
                f"What would you like to improve on your resume today?"
            )

        # 2. ATS Score & Boosting Advice
        if any(w in query for w in ["ats", "score", "boost", "increase score", "low score"]):
            score_text = f"Your current score is **{ats_score}%**." if ats_score is not None else "You haven't run an analysis yet."
            missing_text = f" Focus on adding these key skills: **{', '.join(missing_skills[:5])}**." if missing_skills else ""
            return (
                f"🚀 **How to Maximize Your ATS Score:**\n\n"
                f"{score_text}{missing_text}\n\n"
                f"1. **Use Exact Keywords**: Incorporate skill names directly from the Job Description into your Skills and Experience sections.\n"
                f"2. **Quantify Achievements**: Use percentages, dollar amounts, or scale numbers (e.g. *'Optimized query performance by 35%'*).\n"
                f"3. **Simple Formatting**: Stick to single-column layouts. Avoid complex text boxes, tables, headers/footers, or graphics that confuse ATS parsers.\n"
                f"4. **Standard Section Headers**: Use clear titles like *'Professional Experience'*, *'Education'*, and *'Technical Skills'*."
            )

        # 3. Typography, Fonts & Font Sizing
        if any(w in query for w in ["font", "size", "typography", "heading", "margin", "format"]):
            return (
                f"🎨 **Professional Resume Typography Guidelines:**\n\n"
                f"• **Recommended Fonts**: Calibri, Arial, Helvetica, Inter, or Georgia.\n"
                f"• **Font Size Hierarchy**:\n"
                f"   - **Your Name**: 20pt – 24pt (Bold)\n"
                f"   - **Section Headers**: 13pt – 15pt (Bold, UPPERCASE)\n"
                f"   - **Job Titles & Degrees**: 11pt – 12pt (Semi-bold)\n"
                f"   - **Body Text & Bullets**: 10pt – 11pt (Regular)\n"
                f"• **Margins & Line Spacing**: Use 0.75-inch (or 1-inch) margins with 1.15 line spacing for comfortable readability."
            )

        # 4. Action Verbs & High-Impact Bullets
        if any(w in query for w in ["action verb", "bullet", "verb", "word", "description", "write experience"]):
            return (
                f"⚡ **High-Impact Action Verbs to Use:**\n\n"
                f"Start every project or job bullet point with a strong action verb:\n\n"
                f"• **Technical & Engineering**: *Architected, Engineered, Developed, Deployed, Automated, Refactored, Integrated*\n"
                f"• **Leadership & Management**: *Spearheaded, Orchestrated, Directed, Overhauled, Mentored, Established*\n"
                f"• **Optimization & Data**: *Boosted, Streamlined, Reduced, Scaled, Maximized, Indexed*\n\n"
                f"💡 **Formula**: [Action Verb] + [Task/Technology] + [Quantified Result]\n"
                f"*Example*: *'Architected REST API in Python handling 50k+ daily users, reducing response latency by 30%.'*"
            )

        # 5. Missing Skills Query
        if any(w in query for w in ["missing", "missing skills", "skill gap", "keyword"]):
            if missing_skills:
                return (
                    f"🔍 **Missing Keywords Detected in Target JD:**\n\n"
                    f"The following required skills were not detected in your current resume text:\n"
                    f"• {', '.join(missing_skills)}\n\n"
                    f"💡 **Recommendation**: Add these terms into your Technical Skills section or weave them into your project bullet points if you have experience with them!"
                )
            else:
                return "Great news! No critical missing skills were detected for your target role, or you haven't performed a JD match analysis yet."

        # 6. Fresher vs Experienced Resume Advice
        if any(w in query for w in ["fresher", "entry level", "graduate", "experienced", "experience"]):
            if mode == "fresher" or "fresher" in query:
                return (
                    f"🎓 **Fresher / Entry-Level Resume Strategy:**\n\n"
                    f"1. **Length**: Strictly 1 page.\n"
                    f"2. **Section Priority**: Name & Contact ➔ Career Objective ➔ Technical Skills ➔ Key Projects ➔ Education ➔ Certifications.\n"
                    f"3. **Project Focus**: Highlight 2-3 technical academic or personal projects. Include GitHub repository links.\n"
                    f"4. **Formatting**: Ensure GitHub/Portfolio links are clean and clickable."
                )
            else:
                return (
                    f"💼 **Experienced Professional Resume Strategy:**\n\n"
                    f"1. **Length**: 1 to 2 pages.\n"
                    f"2. **Section Priority**: Header ➔ Executive Summary ➔ Skills Matrix ➔ Professional Experience ➔ Projects ➔ Education.\n"
                    f"3. **Metrics Focus**: Emphasize career progression, team leadership, revenue impact, and architecture scale numbers."
                )

        # 7. Resume Generator (.docx) Advice
        if any(w in query for w in ["docx", "word", "template", "download", "create resume", "generate"]):
            return (
                f"📄 **AI ATS Resume (.docx) Generation:**\n\n"
                f"You can instantly generate a fully formatted, ATS-compliant Microsoft Word document!\n\n"
                f"1. Go to the **Analyze Resume** tab.\n"
                f"2. Upload your resume and click **🚀 Analyze Resume**.\n"
                f"3. Click **✨ Create AI ATS Recommended Resume (.docx)**.\n\n"
                f"ResumeIQ will automatically rewrite your bullet points with action verbs and save the `.docx` file in the Output folder!"
            )

        # 8. General AI Fallback Answer
        return (
            f"Regarding your query about **'{user_query}'**:\n\n"
            f"For optimal resume performance, ensure your document uses a single-column layout, standard headings, "
            f"and incorporates relevant keywords from your target job position ({job_title or 'Software Engineering'}).\n\n"
            f"Feel free to ask me specifically about **ATS scores**, **font sizes**, **action verbs**, or **missing skills**!"
        )

chatbot_engine = AICareerChatbot()
