class ScoreEngine:
    def __init__(self, eqs_result, auth_result, nlp_result):
        self.eqs = eqs_result or {}
        self.auth = auth_result or {}
        self.nlp = nlp_result or {}

    def engagement_score(self):
        return min(max(self.eqs.get("EQS", 0), 0), 1)

    def authenticity_score(self):
        return min(max(self.auth.get("Authenticity_Index", 0), 0), 1)

    def consistency_score(self):
        return min(max(self.eqs.get("engagement_consistency", 0), 0), 1)

    def audience_alignment_score(self):
        scores = self.nlp.get("Niche_Scores", {})

        total = sum(scores.values())
        if total == 0:
            return 0.3  # general creator

        primary = max(scores.values())
        alignment = primary / total

        return round(min(alignment, 1), 3)

    def compute_iis(self):
        eqs = self.engagement_score()
        auth = self.authenticity_score()
        consistency = self.consistency_score()
        alignment = self.audience_alignment_score()

        iis = (
            0.35 * eqs +
            0.30 * auth +
            0.20 * consistency +
            0.15 * alignment
        )

        return {
            "Influencer_Intelligence_Score": round(iis, 3),
            "Score_Breakdown": {
                "Engagement_Quality": round(eqs, 3),
                "Authenticity": round(auth, 3),
                "Consistency": round(consistency, 3),
                "Audience_Alignment": round(alignment, 3)
            },
            "Verdict": self._verdict(iis)
        }

    def _verdict(self, score):
        if score >= 0.75:
            return "HIGHLY RECOMMENDED"
        elif score >= 0.55:
            return "POTENTIAL COLLAB"
        else:
            return "LOW PRIORITY"
