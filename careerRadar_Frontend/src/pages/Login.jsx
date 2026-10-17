import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { useAuth } from "../hooks/UseAuth";
import { getSafeExternalJobUrl } from "../services/JobApi";

function Login({ register = false }) {
    const { user, login, register: createAccount } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const [error, setError] = useState("");
    const [message, setMessage] = useState(location.state?.message || "");
    const [submitting, setSubmitting] = useState(false);

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
        <div className="site-shell">
            <Navbar />
            <main className="auth-page">
                <section className="auth-card">
                    <p className="eyebrow">CareerRadar account</p>
                    <h1>{register ? "Create your account" : "Welcome back"}</h1>
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
                                required
                            />
                            {register && <small className="password-requirements">Use at least 8 characters with an uppercase letter, a lowercase letter, a number, and a symbol.</small>}
                        </label>
                        <button className="btn auth-submit" type="submit" disabled={submitting}>
                            {submitting ? "Please wait…" : register ? "Create account" : "Sign in"}
                        </button>
                    </form>
                    <p className="auth-switch">
                        {register ? "Already registered? " : "New to CareerRadar? "}
                        <Link to={register ? "/login" : "/register"}>{register ? "Sign in" : "Create an account"}</Link>
                    </p>
                </section>
            </main>
            <Footer />
        </div>
    );
}

export default Login;
