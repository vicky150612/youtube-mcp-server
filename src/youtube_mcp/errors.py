"""Safe, structured application errors."""

class AppError(Exception):
    code = "internal_error"
    default_action = "Try again or contact the maintainer."

    def __init__(self, message: str, next_action: str | None = None):
        super().__init__(message)
        self.message = message
        self.next_action = next_action or self.default_action

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "next_action": self.next_action}


class ValidationError(AppError):
    code = "invalid_input"
    default_action = "Check the input."


class ConstraintError(AppError):
    code = "impossible_constraints"
    default_action = "Adjust the constraints."


class NotFoundError(AppError):
    code = "not_found"
    default_action = "Check the identifier."


class UnavailableError(AppError):
    code = "unavailable"
    default_action = "Choose an available item."


class InsufficientDataError(AppError):
    code = "not_enough_data"
    default_action = "Provide more source data."


class AuthRequiredError(AppError):
    code = "auth_required"
    default_action = "Authorise the requested YouTube access."


class ChannelRequiredError(AppError):
    code = "youtube_signup_required"
    default_action = "Create a YouTube channel before continuing."


class QuotaExceededError(AppError):
    code = "quota_exceeded"
    default_action = "Wait until the next Pacific midnight."


class OverBudgetError(AppError):
    code = "over_budget"
    default_action = "Reduce the scope or wait for the reset."


class UnknownCostError(AppError):
    code = "unknown_cost"
    default_action = "Ask the maintainer to register the operation cost."


class RateLimitedError(AppError):
    code = "rate_limited"
    default_action = "Wait before retrying."


class ConfirmationError(AppError):
    code = "confirmation_failed"
    default_action = "Export the proposal manually if needed."


class ProposalStateError(AppError):
    code = "proposal_invalid"
    default_action = "Generate a fresh proposal."


class ForbiddenError(AppError):
    code = "forbidden"
    default_action = "Check the account and permissions."


class ProviderError(AppError):
    code = "provider_error"
    default_action = "Check configuration and connectivity."
