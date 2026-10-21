import { SESSION_EXPIRED_MESSAGE, TOKEN_NOT_YET_VALID_MESSAGE } from "../services/Api";

export default function ErrorMessage({ message = "Something went wrong.", onRetry }) {
  const refreshPage = message === SESSION_EXPIRED_MESSAGE || message === TOKEN_NOT_YET_VALID_MESSAGE;

  return (
    <div className="error-message card" role="alert">
      <span className="error-icon" aria-hidden="true">!</span>
      <div>
        <h3>We couldn't load this right now</h3>
        <p>{message}</p>
      </div>
      {onRetry && (
        <button
          className="btn btn-ghost"
          type="button"
          onClick={refreshPage ? () => window.location.reload() : onRetry}
        >
          {refreshPage ? "Refresh the page" : "Try again"}
        </button>
      )}
    </div>
  );
}
