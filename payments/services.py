import random
import uuid


class FakePaymentProvider:
    """
    Fake provider used for local development.

    Default simulation:
    - 80% success
    - 10% failed
    - 10% timeout
    """

    @staticmethod
    def process(payment, force_outcome=None):
        if force_outcome:
            outcome = force_outcome.upper()
        else:
            outcome = random.choices(
                population=["SUCCESS", "FAILED", "TIMEOUT"],
                weights=[80, 10, 10],
                k=1,
            )[0]

        provider_reference = f"FAKE-{uuid.uuid4().hex[:16].upper()}"

        if outcome == "SUCCESS":
            return {
                "provider_reference": provider_reference,
                "status": "SUCCEEDED",
                "message": "Fake payment processed successfully.",
            }

        if outcome == "FAILED":
            return {
                "provider_reference": provider_reference,
                "status": "FAILED",
                "message": "Fake payment failed due to simulated provider decline.",
            }

        return {
            "provider_reference": provider_reference,
            "status": "TIMEOUT",
            "message": "Fake payment timed out.",
        }
