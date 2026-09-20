from src.gemini_client import GeminiClient


class GeminiExplainer:
    def __init__(self, client=None):
        self.client = client or GeminiClient()

    def explain_compliance(
        self,
        clause: dict,
        compliance_result: dict,
        standard: dict
    ) -> str:

        clause_type = clause.get(
            "clause_type",
            "Unknown"
        )

        clause_text = clause.get(
            "text",
            ""
        )

        status = compliance_result.get(
            "status",
            "REVIEW"
        )

        reason = compliance_result.get(
            "reason",
            ""
        )

        standard_key = compliance_result.get(
            "standard_key",
            ""
        )

        prompt = f"""
You are the explanation layer of LeaseLens.

The LeaseLens rule engine has ALREADY made the compliance
decision. You must NOT make another decision.

Your ONLY task is to explain the supplied result clearly
and concisely.

AUTHORITATIVE DATA:
- Clause type: {clause_type}
- Lease clause: {clause_text}
- Compliance status: {status}
- Rule engine reason: {reason}
- Standard key: {standard_key}
- Company standard: {standard}

STRICT RULES:

1. Treat the supplied compliance status as final.
2. Treat the supplied rule engine reason as final.
3. Do not change, reinterpret, or reassess the status.
4. Do not create or infer another compliance rule.
5. Do not invent or modify a company standard.
6. Do not claim that a standard is missing when a standard
   is supplied above.
7. Do not introduce facts that are not present above.
8. For REVIEW results, explain the supplied review reason.
9. Do not provide legal advice.
10. Do not independently determine whether the clause is
    compliant or non-compliant.

Write one concise explanation in natural language.

The explanation must:
- describe what the lease clause says;
- explain the supplied company standard when one exists;
- explain the supplied rule engine status and reason;
- preserve the exact meaning of the supplied result.

Return ONLY the explanation.
"""

        return self.client.generate(prompt)