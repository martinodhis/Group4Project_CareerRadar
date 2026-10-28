import { useEffect, useState } from "react";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { apiGet, apiPatch, apiRequest } from "../services/Api";

const emptyProfile = {
    full_name: "",
    headline: "",
    current_job_title: "",
    career_level: "",
    location: "",
    years_of_experience: 0,
    bio: "",
};
const CAREER_LEVELS = ["Entry Level", "Junior", "Mid-Level", "Senior", "Executive"];

function Profile() {
    const [profile, setProfile] = useState(emptyProfile);
    const [account, setAccount] = useState({ first_name: "", last_name: "", email: "" });
    const [loading, setLoading] = useState(true);
    const [savingProfile, setSavingProfile] = useState(false);
    const [savingAccount, setSavingAccount] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    useEffect(() => {
        let active = true;
        apiGet("/profile")
            .then(({ data }) => {
                if (!active) return;
                setProfile({ ...emptyProfile, ...data });
                setAccount({
                    first_name: data.user?.first_name || "",
                    last_name: data.user?.last_name || "",
                    email: data.user?.email || "",
                });
            })
            .catch((requestError) => {
                if (active) setError(requestError.message);
            })
            .finally(() => {
                if (active) setLoading(false);
            });
        return () => { active = false; };
    }, []);

    const saveProfile = async (event) => {
        event.preventDefault();
        setError("");
        setMessage("");
        setSavingProfile(true);
        try {
            const { data } = await apiRequest("/profile", {
                method: "PUT",
                body: {
                    full_name: profile.full_name || null,
                    headline: profile.headline || null,
                    current_job_title: profile.current_job_title || null,
                    career_level: profile.career_level || null,
                    location: profile.location || null,
                    years_of_experience: Number(profile.years_of_experience) || 0,
                    bio: profile.bio || null,
                },
            });
            setProfile((current) => ({ ...current, ...data }));
            setMessage("Your profile details have been saved.");
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setSavingProfile(false);
        }
    };

    const saveAccount = async (event) => {
        event.preventDefault();
        setError("");
        setMessage("");
        setSavingAccount(true);
        try {
            const { data } = await apiPatch("/users/me", account);
            setAccount({
                first_name: data.first_name || "",
                last_name: data.last_name || "",
                email: data.email || "",
            });
            setMessage("Your account details have been saved.");
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setSavingAccount(false);
        }
    };

    const updateProfileField = (event) => {
        const { name, value } = event.target;
        setProfile((current) => ({ ...current, [name]: value }));
    };
    const updateAccountField = (event) => {
        const { name, value } = event.target;
        setAccount((current) => ({ ...current, [name]: value }));
    };

    return (
        <div className="site-shell">
            <Navbar />
            <main className="dashboard-page">
                <section className="dashboard-heading">
                    <p className="eyebrow">Your account</p>
                    <h1>My profile</h1>
                    <p>Edit your personal details and career profile.</p>
                </section>
                {error && <p className="inline-error" role="alert">{error}</p>}
                {message && <p className="inline-success" role="status">{message}</p>}
                {loading ? <p className="page-state">Loading your profile…</p> : (
                    <>
                        <form className="profile-form" onSubmit={saveAccount}>
                            <section className="admin-section">
                                <div className="admin-section-heading"><div><p className="eyebrow">Sign-in account</p><h2>Personal details</h2></div></div>
                                <div className="profile-fields">
                                    <label>First name<input name="first_name" value={account.first_name} onChange={updateAccountField} required maxLength="120" /></label>
                                    <label>Last name<input name="last_name" value={account.last_name} onChange={updateAccountField} required maxLength="120" /></label>
                                    <label>Email address<input name="email" type="email" value={account.email} onChange={updateAccountField} required maxLength="120" /></label>
                                </div>
                                <button className="btn" type="submit" disabled={savingAccount}>{savingAccount ? "Saving…" : "Save account details"}</button>
                            </section>
                        </form>
                        <form className="profile-form" onSubmit={saveProfile}>
                            <section className="admin-section">
                                <div className="admin-section-heading"><div><p className="eyebrow">Career details</p><h2>Professional profile</h2></div></div>
                                <div className="profile-fields">
                                    <label>Display name<input name="full_name" value={profile.full_name} onChange={updateProfileField} maxLength="240" /></label>
                                    <label><span>Headline <span className="required-indicator">Required</span></span><input name="headline" value={profile.headline} onChange={updateProfileField} placeholder="e.g. Software Developer | React & Python" required maxLength="240" /></label>
                                    <label><span>Current job title <span className="required-indicator">Required</span></span><input name="current_job_title" value={profile.current_job_title} onChange={updateProfileField} required maxLength="160" /></label>
                                    <label><span>Career level <span className="required-indicator">Required</span></span>
                                        <select name="career_level" value={profile.career_level} onChange={updateProfileField} required>
                                            <option value="">Select a career level</option>
                                            {profile.career_level && !CAREER_LEVELS.includes(profile.career_level) && <option value={profile.career_level}>{profile.career_level}</option>}
                                            {CAREER_LEVELS.map((level) => <option key={level} value={level}>{level}</option>)}
                                        </select>
                                    </label>
                                    <label><span>Location <span className="required-indicator">Required</span></span><input name="location" value={profile.location} onChange={updateProfileField} required maxLength="160" /></label>
                                    <label>Years of experience<input name="years_of_experience" type="number" min="0" step="0.5" inputMode="decimal" value={profile.years_of_experience} onChange={updateProfileField} /></label>
                                    <label className="profile-bio">About you<textarea name="bio" rows="5" value={profile.bio} onChange={updateProfileField} /></label>
                                </div>
                                <p className="profile-completion" role="progressbar" aria-label="Profile completion" aria-valuemin="0" aria-valuemax="100" aria-valuenow={profile.profile_completion ?? 0}>
                                    Profile completion: <strong>{profile.profile_completion ?? 0}%</strong>
                                </p>
                                <p className="profile-completion-help">Completion also requires at least 3 skills, education, work experience, and a career goal. The percentage refreshes after saving these details or changing any of those sections.</p>
                                <button className="btn" type="submit" disabled={savingProfile}>{savingProfile ? "Saving…" : "Save career profile"}</button>
                            </section>
                        </form>
                    </>
                )}
            </main>
            <Footer />
        </div>
    );
}

export default Profile;
