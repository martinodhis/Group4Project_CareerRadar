import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import JobDescription from "../components/JobDescription";
import { apiDelete, apiGet } from "../services/Api";
import { formatJobDate } from "../services/JobApi";

function SavedJobs() {
    const [savedJobs, setSavedJobs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        let active = true;
        apiGet("/saved-jobs")
            .then(({ data }) => {
                if (active) setSavedJobs(data.saved_jobs);
            })
            .catch((requestError) => {
                if (active) setError(requestError.message);
            })
            .finally(() => {
                if (active) setLoading(false);
            });
        return () => { active = false; };
    }, []);

    const removeSavedJob = async (jobId) => {
        setError("");
        try {
            await apiDelete(`/saved-jobs/${encodeURIComponent(jobId)}`);
            setSavedJobs((current) => current.filter((saved) => saved.job_id !== jobId));
        } catch (requestError) {
            setError(requestError.message);
        }
    };

    return (
        <div className="site-shell">
            <Navbar />
            <main className="dashboard-page">
                <section className="dashboard-heading">
                    <p className="eyebrow">Your opportunities</p>
                    <h1>Saved jobs</h1>
                    <p>Keep interesting roles close while you decide where to apply.</p>
                </section>
                {error && <p className="inline-error" role="alert">{error}</p>}
                {loading ? <p className="page-state">Loading your saved jobs…</p> : savedJobs.length ? (
                    <div className="job-list">
                        {savedJobs.map(({ job_id: jobId, job, created_at: savedAt }) => (
                            <article className="job-card card" key={jobId}>
                                <h2 className="job-title"><Link to={`/jobs/${jobId}`}>{job.title}</Link></h2>
                                <p className="job-company">{job.company_name || "Company"} · {job.location || "Location not specified"}</p>
                                <JobDescription className="job-excerpt" description={job.description || "No description provided."} />
                                <div className="job-card-footer">
                                    <span className="job-date">Saved {formatJobDate(savedAt)}</span>
                                    <div className="job-card-actions">
                                        <Link className="btn" to={`/jobs/${jobId}`}>View job</Link>
                                        <button className="btn btn-ghost" type="button" onClick={() => removeSavedJob(jobId)}>Remove</button>
                                    </div>
                                </div>
                            </article>
                        ))}
                    </div>
                ) : <EmptyState title="No saved jobs" message="Save jobs from the listings page and they will appear here." />}
            </main>
            <Footer />
        </div>
    );
}

export default SavedJobs;
