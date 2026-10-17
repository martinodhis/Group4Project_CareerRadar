import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { apiGet } from "../services/Api";

const APPLICATION_STATUS_LABELS = {
    SAVED: "Application in progress",
    APPLIED: "Application successful",
    SCREENING: "Under review",
    INTERVIEW: "Interview stage",
    OFFER: "Offer received",
    ACCEPTED: "Offer accepted",
    REJECTED: "Not selected",
};

function ApplicationsDashboard() {
    const [applications, setApplications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const statusLabel = (status) => APPLICATION_STATUS_LABELS[String(status || "").toUpperCase()] || "Application in progress";

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
                    <p>Review the opportunities you are tracking and their current status.</p>
                </section>
                {error && <p className="inline-error" role="alert">{error}</p>}
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
                                            <td><span className="status-pill">{statusLabel(application.status)}</span></td>
                                            <td>{application.applied_at ? new Date(application.applied_at).toLocaleDateString() : "—"}</td>
                                            <td>{application.updated_at ? new Date(application.updated_at).toLocaleDateString() : "—"}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <p className="inline-success" role="status">Please wait for the company to respond to your application.</p>
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
