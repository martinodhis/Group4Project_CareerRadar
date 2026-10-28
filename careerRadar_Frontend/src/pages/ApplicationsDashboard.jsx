import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { apiGet, apiPatch } from "../services/Api";

const APPLICATION_STATUS_LABELS = {
    SAVED: "Application in progress",
    APPLIED: "Application recorded",
    SCREENING: "Under review",
    INTERVIEW: "Interview stage",
    OFFER: "Offer received",
    ACCEPTED: "Offer accepted",
    REJECTED: "Not selected",
};
const APPLICATION_STATUSES = Object.keys(APPLICATION_STATUS_LABELS);

function ApplicationsDashboard() {
    const [applications, setApplications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [updatingApplicationId, setUpdatingApplicationId] = useState(null);
    const statusLabel = (status) => APPLICATION_STATUS_LABELS[String(status || "").toUpperCase()] || "Application in progress";

    const updateStatus = async (applicationId, status) => {
        setError("");
        setMessage("");
        setUpdatingApplicationId(applicationId);
        try {
            const response = await apiPatch(`/applications/${applicationId}`, { status });
            setApplications((current) => current.map((application) =>
                application.id === applicationId ? response.data : application
            ));
            setMessage("Application status updated.");
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setUpdatingApplicationId(null);
        }
    };

    useEffect(() => {
        let active = true;
        apiGet("/applications")
            .then((response) => {
                if (active) setApplications(response.data.applications);
            })
            .catch((requestError) => {
                if (active) setError(requestError.message);
            })
            .finally(() => {
                if (active) setLoading(false);
            });
        return () => {
            active = false;
        };
    }, []);

    return (
        <div className="site-shell">
            <Navbar />
            <main className="dashboard-page">
                <section className="dashboard-heading">
                    <p className="eyebrow">Your account</p>
                    <h1>My applications</h1>
                    <p>Track applications you submitted on the employer’s website and update their status as it changes.</p>
                </section>
                {error && <p className="inline-error" role="alert">{error}</p>}
                {message && <p className="inline-success" role="status">{message}</p>}
                {loading ? <p className="page-state">Loading your applications…</p> : applications.length ? (
                    <>
                        <div className="table-wrap">
                            <table>
                                <thead><tr><th>Job</th><th>Company</th><th>Status</th><th>Application date</th><th>Last updated</th></tr></thead>
                                <tbody>
                                    {applications.map((application) => (
                                        <tr key={application.id}>
                                            <td>{application.job?.title || `Job #${application.job_id}`}</td>
                                            <td>{application.job?.company_name || "—"}</td>
                                            <td>
                                                <label className="sr-only" htmlFor={`application-status-${application.id}`}>Status for {application.job?.title || `job ${application.job_id}`}</label>
                                                <select
                                                    id={`application-status-${application.id}`}
                                                    value={application.status}
                                                    disabled={updatingApplicationId !== null}
                                                    onChange={(event) => updateStatus(application.id, event.target.value)}
                                                >
                                                    {APPLICATION_STATUSES.map((status) => (
                                                        <option key={status} value={status}>{statusLabel(status)}</option>
                                                    ))}
                                                </select>
                                            </td>
                                            <td>{application.applied_at ? new Date(application.applied_at).toLocaleDateString() : "—"}</td>
                                            <td>{application.updated_at ? new Date(application.updated_at).toLocaleDateString() : "—"}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <p className="profile-completion-help">Statuses are saved to your tracker only. CareerRadar does not submit applications or receive employer updates.</p>
                    </>
                ) : !error && !loading ? (
                    <EmptyState title="No applications tracked yet" message="Open a job listing and mark your application once you have applied." />
                ) : null}
            </main>
            <Footer />
        </div>
    );
}

export default ApplicationsDashboard;
