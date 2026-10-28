import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import JobDescription from "../components/JobDescription";
import { useAuth } from "../hooks/UseAuth";
import { apiPost } from "../services/Api";
import { fetchJob, formatSalaryRange } from "../services/JobApi";

function JobDetails() {
    const { id } = useParams();
    const { user } = useAuth();
    const [jobResult, setJobResult] = useState({ id: null, job: null, error: null });
    const [applicationMessage, setApplicationMessage] = useState("");
    const [applicationError, setApplicationError] = useState("");
    const [submitting, setSubmitting] = useState(false);
    const [applicationTracked, setApplicationTracked] = useState(false);
    const [retryCount, setRetryCount] = useState(0);

    useEffect(() => {
        const controller = new AbortController();
        fetchJob(id, controller.signal)
            .then((job) => {
                if (!controller.signal.aborted) setJobResult({ id, job, error: null });
            })
            .catch((requestError) => {
                if (!controller.signal.aborted) setJobResult({ id, job: null, error: requestError.message });
            });
        return () => controller.abort();
    }, [id, retryCount]);

    const loading = jobResult.id !== id;
    const job = loading ? null : jobResult.job;
    const error = loading ? null : jobResult.error;

    const trackApplication = async () => {
        setSubmitting(true);
        setApplicationError("");
        setApplicationMessage("");
        try {
            await apiPost("/applications", {
                job_id: job.id,
                status: "APPLIED",
                applied_at: new Date().toISOString(),
            });
            setApplicationMessage("Application recorded in your tracker. CareerRadar does not submit applications to employers.");
            setApplicationTracked(true);
        } catch (requestError) {
            setApplicationError(requestError.message);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <>
            <Navbar />
            <main>
                {error ? (
                    <section className="job-detail-state"><ErrorMessage message={error} onRetry={() => setRetryCount((current) => current + 1)} /></section>
                ) : loading ? (
                    <section className="job-header job-detail-loading" aria-live="polite">Loading job details…</section>
                ) : job ? (
                    <>
                        <section className="job-header">
                            <h1>{job.title}</h1>
                            <p>{job.company}</p>
                            <p>{job.location}</p>
                        </section>

                        <section className="job-information">
                            <div><strong>Employment Type</strong><p>{job.jobTypes.join(", ") || "Not specified"}</p></div>
                            <div><strong>Experience Level</strong><p>{job.level || "Not specified"}</p></div>
                            <div><strong>Salary</strong><p>{formatSalaryRange(job)}</p></div>
                        </section>

                        <section className="job-description">
                            <h2>Job Description</h2>
                            {job.excerpt
                                ? <JobDescription className="job-description-content" description={job.excerpt} />
                                : <p>See the original listing for the full description.</p>}
                        </section>

                        <section className="job-requirements">
                            <h2>About this opportunity</h2>
                            <p>Review the full role details and requirements on the employer’s listing.</p>
                        </section>

                        <section className="job-application job-actions">
                            {job.url && (user ? (
                                <a href={job.url} target="_blank" rel="noreferrer">Apply on company site <span aria-hidden="true">↗</span></a>
                            ) : (
                                <Link
                                    className="btn"
                                    to="/register"
                                    state={{
                                        message: "Create an account or sign in to continue to this company's job listing.",
                                        returnTo: { path: `/jobs/${job.id}`, applyUrl: job.url },
                                    }}
                                >
                                    Register to apply <span aria-hidden="true">↗</span>
                                </Link>
                            ))}
                            {user ? (
                                <button className="btn" type="button" onClick={trackApplication} disabled={submitting || applicationTracked}>
                                    {submitting ? "Saving…" : applicationTracked ? "Application recorded" : "I have applied"}
                                </button>
                            ) : (
                                <Link className="btn btn-ghost" to="/login" state={{
                                    message: "Sign in to continue to this company's job listing.",
                                    returnTo: { path: `/jobs/${job.id}`, applyUrl: job.url },
                                }}>
                                    Sign in to apply
                                </Link>
                            )}
                            {applicationMessage && <p className="inline-success" role="status">{applicationMessage}</p>}
                            {applicationError && <p className="inline-error" role="alert">{applicationError}</p>}
                        </section>
                    </>
                ) : (
                    <section className="job-detail-state"><EmptyState title="Job not found" message="This role may have closed or is no longer available." /></section>
                )}
            </main>
            <Footer />
        </>
    );
}

export default JobDetails;
