def generate_jd_summary(jd_profile):

    required = jd_profile.get("skills", {}).get("required", [])

    preferred = jd_profile.get("skills", {}).get("preferred", [])

    summary = f"""
                Role:
                {jd_profile.get('role','')}

                Experience:
                {jd_profile.get('experience_years',0)} years

                Industry:
                {jd_profile.get('industry','')}

                Seniority:
                {jd_profile.get('seniority','')}

                Required Skills:
                {', '.join(required)}

                Preferred Skills:
                {', '.join(preferred)}

                Domain:
                {''.join(
                    jd_profile.get(
                        'domain',
                        []
                    )
                )}
            """

    return summary