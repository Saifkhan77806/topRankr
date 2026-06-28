def generate_candidate_summary(profile):
    professional = profile.get("professional",{})
    skills = profile.get("skills",{})
    leadership = profile.get("leadership",{})
    summary = f"""
                Candidate Role:
                {professional.get('current_title','')}

                Experience:
                {professional.get('total_experience_years',0)} years

                Industry:
                {professional.get('industry','')}

                Seniority:
                {professional.get('seniority','')}

                Domain Expertise:
                {', '.join(professional.get('domain_expertise',[]))}

                Technical Skills:
                {', '.join(skills.get('technical',[]))}

                Tools:
                {', '.join(skills.get('tools',[]))}

                Soft Skills:
                {', '.join(skills.get('soft_skills',[]))}

                Leadership:
                {leadership.get('has_leadership',False)}

                Team Size:
                {leadership.get('team_size',0)}
            """

    return summary