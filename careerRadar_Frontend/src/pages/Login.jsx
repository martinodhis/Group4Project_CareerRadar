import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/UseAuth";
import { getSafeExternalJobUrl } from "../services/JobApi";

function Login({ register = false }) {
    const { user, login, register: createAccount } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const [error, setError] = useState("");
    const [message, setMessage] = useState(location.state?.message || "");
    const [submitting, setSubmitting] = useState(false);
    const [password, setPassword] = useState("");
    const passwordRequirements = [
        { label: "At least 8 characters", satisfied: password.length >= 8 },
        { label: "A lowercase letter", satisfied: /[a-z]/.test(password) },
        { label: "An uppercase letter", satisfied: /[A-Z]/.test(password) },
        { label: "A number", satisfied: /[0-9]/.test(password) },
        { label: "A symbol", satisfied: /[^A-Za-z0-9\s]/.test(password) },
    ];
    const passwordIsValid = passwordRequirements.every(({ satisfied }) => satisfied);

    useEffect(() => {
        if (!user) return;

        const applyUrl = getSafeExternalJobUrl(location.state?.returnTo?.applyUrl);
        if (applyUrl) {
            window.location.assign(applyUrl);
            return;
        }

        const destination = location.state?.returnTo?.path || location.state?.from || (user.role?.toUpperCase() === "ADMIN" ? "/admin" : "/dashboard");
        navigate(destination, { replace: true });
    }, [user, navigate, location.state]);

    if (user) return <main className="page-state">Redirecting…</main>;

    const submit = async (event) => {
        event.preventDefault();
        setError("");
        setMessage("");
        setSubmitting(true);
        const fields = new FormData(event.currentTarget);
        try {
            if (register) {
                await createAccount({
                    first_name: fields.get("first_name"),
                    last_name: fields.get("last_name"),
                    email: fields.get("email"),
                    password: fields.get("password"),
                });
                navigate("/login", {
                    replace: true,
                    state: {
                        message: "Your account was created. Sign in to continue.",
                        returnTo: location.state?.returnTo,
                    },
                });
            } else {
                await login(fields.get("email"), fields.get("password"));
            }
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <main className="auth-layout">
            <div className="auth-shell">
                <aside className="auth-promo" aria-label="CareerRadar benefits">
                    <Link to="/" className="brand auth-brand">
                        <span className="brand-dot" aria-hidden="true" />
                        Career<span className="brand-accent">Radar</span>
                    </Link>
                    <div className="auth-promo-content">
                        <p className="auth-promo-label">{register ? "Your next chapter" : "CareerRadar account"}</p>
                        <h2>{register ? "A new path starts here." : "Welcome back!"}</h2>
                        <p className="auth-promo-description">
                            {register
                                ? "Create your account to discover opportunities, save jobs, and keep your career goals in focus."
                                : "Sign in to pick up where you left off and keep moving toward your next career opportunity."}
                        </p>
                    </div>
                </aside>
                <section className="auth-form-panel">
                    <div className="auth-form-content">
                        <section className="auth-card">
                            <p className="eyebrow">CareerRadar account</p>
                            <h1>{register ? "Create your account" : "Log in"}</h1>
                            <p className="auth-description">
                                {register
                                    ? "Register to save jobs and track your applications."
                                    : "Sign in to manage saved jobs and your application activity."}
                            </p>
                            {message && <p className="inline-success" role="status">{message}</p>}
                            {error && <p className="inline-error" role="alert">{error}</p>}
                            <form className="auth-form" onSubmit={submit}>
                                {register && (
                                    <div className="auth-name-fields">
                                        <label>First name<input name="first_name" autoComplete="given-name" required maxLength="120" /></label>
                                        <label>Last name<input name="last_name" autoComplete="family-name" required maxLength="120" /></label>
                                    </div>
                                )}
                                <label>Email address<input type="email" name="email" autoComplete="email" required /></label>
                                <label>
                                    Password
                                    <input
                                        type="password"
                                        name="password"
                                        autoComplete={register ? "new-password" : "current-password"}
                                        minLength={register ? 8 : undefined}
                                        pattern={register ? "(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9\\s]).{8,}" : undefined}
                                        title={register ? "Use at least 8 characters, including an uppercase letter, a lowercase letter, a number, and a symbol." : undefined}
                                        value={password}
                                        onChange={(event) => setPassword(event.target.value)}
                                        aria-describedby={register ? "password-requirements" : undefined}
                                        aria-invalid={register && password.length > 0 && !passwordIsValid}
                                        required
                                    />
                                    {register && (
                                        <div id="password-requirements" className="password-requirements" aria-live="polite">
                                            <p>{passwordIsValid ? "Password meets all requirements." : "Password must include:"}</p>
                                            <ul>
                                                {passwordRequirements.map(({ label, satisfied }) => (
                                                    <li key={label} className={satisfied ? "is-satisfied" : ""}>
                                                        <span aria-hidden="true">{satisfied ? "✓" : "•"}</span> {label}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </label>
                                <button className="btn auth-submit" type="submit" disabled={submitting || (register && !passwordIsValid)}>
                                    {submitting ? "Please wait…" : register ? "Create account" : "Sign in"}
                                </button>
                            </form>
                            <p className="auth-switch">
                                {register ? "Already registered? " : "Don't have an account? "}
                                <Link to={register ? "/login" : "/register"} state={location.state}>
                                    {register ? "Sign in" : "Sign up"}
                                </Link>
                            </p>
                        </section>
                    </div>
                </section>
            </div>
        </main>
    );
}

export default Login;
