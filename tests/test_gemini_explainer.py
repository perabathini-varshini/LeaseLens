from src.gemini_explainer import GeminiExplainer


class FakeGeminiClient:
    def __init__(self, response):
        self.last_prompt = None
        self.response = response

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response


def create_explainer(response):
    return GeminiExplainer(
        client=FakeGeminiClient(response)
    )


def create_clause():
    return {
        "clause_type": "SECURITY_DEPOSIT",
        "text": (
            "The tenant shall pay a security deposit "
            "of INR 60000."
        )
    }


def create_standard():
    return {
        "currency": "INR",
        "min_amount": 30000,
        "max_amount": 50000,
        "allow_forfeiture": False
    }


def test_compliant_status_is_preserved():
    fake_response = (
        "The lease specifies a monthly rent of INR 50000. "
        "The rule engine marked this clause as COMPLIANT."
    )

    explainer = create_explainer(fake_response)

    clause = {
        "clause_type": "RENT",
        "text": "The monthly rent is INR 50000."
    }

    compliance_result = {
        "status": "COMPLIANT",
        "reason": (
            "Rent amount is specified and no prohibited "
            "unilateral rent modification was detected."
        ),
        "standard_key": "rent"
    }

    explanation = explainer.explain_compliance(
        clause,
        compliance_result,
        {
            "currency": "INR",
            "allow_unilateral_modification": False
        }
    )

    assert "COMPLIANT" in explanation


def test_non_compliant_status_is_preserved():
    fake_response = (
        "The security deposit is INR 60000, which exceeds "
        "the maximum allowed amount of INR 50000. "
        "The rule engine marked this clause as NON_COMPLIANT."
    )

    explainer = create_explainer(fake_response)

    compliance_result = {
        "status": "NON_COMPLIANT",
        "reason": (
            "Security deposit exceeds the maximum "
            "allowed amount."
        ),
        "standard_key": "security_deposit"
    }

    explanation = explainer.explain_compliance(
        create_clause(),
        compliance_result,
        create_standard()
    )

    assert "NON_COMPLIANT" in explanation


def test_review_status_is_preserved():
    fake_response = (
        "This clause requires REVIEW because the "
        "information supplied to the rule engine "
        "is ambiguous."
    )

    explainer = create_explainer(fake_response)

    clause = {
        "clause_type": "MAINTENANCE",
        "text": (
            "The tenant is responsible for maintenance "
            "and some repairs."
        )
    }

    compliance_result = {
        "status": "REVIEW",
        "reason": (
            "Responsibility for major repairs "
            "could not be clearly determined."
        ),
        "standard_key": "maintenance"
    }

    explanation = explainer.explain_compliance(
        clause,
        compliance_result,
        {
            "required": True,
            "tenant_responsible_for_major_repairs": False
        }
    )

    assert "REVIEW" in explanation


def test_explainer_prompt_is_grounded():
    fake_response = (
        "The security deposit exceeds the permitted maximum."
    )

    explainer = create_explainer(fake_response)

    fake_client = explainer.client

    compliance_result = {
        "status": "NON_COMPLIANT",
        "reason": (
            "Security deposit exceeds the maximum "
            "allowed amount."
        ),
        "standard_key": "security_deposit"
    }

    explainer.explain_compliance(
        create_clause(),
        compliance_result,
        create_standard()
    )

    prompt = fake_client.last_prompt

    assert prompt is not None

    assert (
        "The LeaseLens rule engine has ALREADY made "
        "the compliance"
        in prompt
    )

    assert (
        "Do not change, reinterpret, or reassess the status."
        in prompt
    )

    assert (
        "Do not create or infer another compliance rule."
        in prompt
    )

    assert (
        "Do not invent or modify a company standard."
        in prompt
    )

    assert (
        "Do not introduce facts that are not present above."
        in prompt
    )

    assert "NON_COMPLIANT" in prompt
    assert "security_deposit" in prompt
    assert "max_amount" in prompt