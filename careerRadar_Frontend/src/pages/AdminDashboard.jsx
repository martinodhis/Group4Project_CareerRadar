import { useEffect, useState } from "react";
import EmptyState from "../components/EmptyState";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { apiGet, apiPatch, apiPost } from "../services/Api";

const initialPagination = { page: 1, pages: 1, total: 0, has_next: false, has_prev: false };
const formatDate = (value) => value ? new Date(value).toLocaleString() : "—";
const userLabel = (user) => user ? `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.email : "Unknown user";

function Pager({ label, pagination, onChange }) {
    return (
        <div className="pager">
            <span>{pagination.total} {label} · page {pagination.page} of {Math.max(1, pagination.pages)}</span>
            <div>
                <button className="btn btn-ghost" type="button" disabled={!pagination.has_prev} onClick={() => onChange(pagination.page - 1)}>Previous</button>
                <button className="btn btn-ghost" type="button" disabled={!pagination.has_next} onClick={() => onChange(pagination.page + 1)}>Next</button>
            </div>
        </div>
    );
}

function AdminDashboard() {
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState({ activities: [], applications: [] });
    const [users, setUsers] = useState([]);
    const [activityPagination, setActivityPagination] = useState(initialPagination);
    const [applicationPagination, setApplicationPagination] = useState(initialPagination);
    const [activityPage, setActivityPage] = useState(1);
    const [applicationPage, setApplicationPage] = useState(1);
    const [applicationStatus, setApplicationStatus] = useState("ALL");
    const [refreshKey, setRefreshKey] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [syncing, setSyncing] = useState(false);
    const [syncMessage, setSyncMessage] = useState("");

    useEffect(() => {
        let active = true;
        const params = new URLSearchParams({
            activity_page: String(activityPage),
            application_page: String(applicationPage),
            limit: "25",
            application_status: applicationStatus,
        });
        Promise.all([
            apiGet("/dashboard/admin"),
            apiGet(`/dashboard/admin/activity?${params}`),
            apiGet("/users"),
        ])
            .then(([statsResponse, historyResponse, usersResponse]) => {
                if (!active) return;
                setStats(statsResponse.data);
                setHistory(historyResponse.data);
                setActivityPagination(historyResponse.data.activity_pagination);
                setApplicationPagination(historyResponse.data.application_pagination);
                setUsers(usersResponse.data.users);
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
    }, [activityPage, applicationPage, applicationStatus, refreshKey]);

    const syncJobs = async () => {
        setSyncing(true);
        setSyncMessage("");
        setError("");
        try {
            const response = await apiPost("/jobs/sync", { count: 50 });
            setSyncMessage(`Job sync complete: ${response.data.created} new and ${response.data.updated} updated.`);
            setLoading(true);
            setRefreshKey((current) => current + 1);
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setSyncing(false);
        }
    };

    const changeActivityPage = (page) => {
        setError("");
        setLoading(true);
        setActivityPage(page);
    };
    const changeApplicationPage = (page) => {
        setError("");
        setLoading(true);
        setApplicationPage(page);
    };

    const changeApplicationStatus = (event) => {
        setError("");
        setLoading(true);
        setApplicationPage(1);
        setApplicationStatus(event.target.value);
    };

    const updateAccount = async (account, changes) => {
        setError("");
        try {
            const response = await apiPatch(`/users/${account.id}`, changes);
            setUsers((current) => current.map((item) => item.id === account.id ? response.data : item));
        } catch (requestError) {
            setError(requestError.message);
        }
    };

    return (
        <div className="site-shell">
            <Navbar />
            <main className="dashboard-page admin-page">
                <section className="dashboard-heading admin-heading">
                    <div>
                        <p className="eyebrow">Administration</p>
                        <h1>Admin dashboard</h1>
                        <p>Monitor accounts, recorded user actions, and job applications.</p>
                    </div>
                    <button className="btn" type="button" onClick={syncJobs} disabled={syncing}>
                        {syncing ? "Syncing jobs…" : "Sync jobs from Jobicy"}
                    </button>
                </section>
                {error && <p className="inline-error" role="alert">{error}</p>}
                {syncMessage && <p className="inline-success" role="status">{syncMessage}</p>}
                {loading ? <p className="page-state">Loading administrator data…</p> : stats && (
                    <>
                        <section className="stats-grid" aria-label="Platform statistics">
                            <article className="stat-card"><span>Users</span><strong>{stats.total_users}</strong><small>{stats.active_users} active</small></article>
                            <article className="stat-card"><span>Jobs</span><strong>{stats.total_jobs}</strong><small>{stats.active_jobs} active</small></article>
                            <article className="stat-card"><span>Applications</span><strong>{stats.applications}</strong><small>Tracked by all users</small></article>
                            <article className="stat-card"><span>Awaiting company response</span><strong>{stats.pending_applications}</strong><small>Applications marked as submitted</small></article>
                            <article className="stat-card"><span>Activity events</span><strong>{stats.activity_events}</strong><small>Recorded since activity tracking was enabled</small></article>
                        </section>

                        <section className="admin-section">
                            <div className="admin-section-heading"><div><p className="eyebrow">Audit trail</p><h2>User activity history</h2></div></div>
                            {history.activities.length ? (
                                <>
                                    <div className="table-wrap">
                                        <table>
                                            <thead><tr><th>When</th><th>User</th><th>Action</th><th>Endpoint</th><th>Request details</th></tr></thead>
                                            <tbody>
                                                {history.activities.map((activity) => (
                                                    <tr key={activity.id}>
                                                        <td>{formatDate(activity.created_at)}</td>
                                                        <td><strong>{userLabel(activity.user)}</strong><small>{activity.user?.email}</small></td>
                                                        <td><span className="status-pill">{activity.action.replaceAll("_", " ")}</span></td>
                                                        <td><code>{activity.endpoint}</code></td>
                                                        <td><code>{JSON.stringify(activity.details)}</code></td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                    <Pager label="events" pagination={activityPagination} onChange={changeActivityPage} />
                                </>
                            ) : <EmptyState title="No activity recorded" message="Authenticated searches, job views, saved jobs, sign-ins, and application changes will appear here." />}
                        </section>

                        <section className="admin-section">
                            <div className="admin-section-heading">
                                <div><p className="eyebrow">Application pipeline</p><h2>All user applications</h2></div>
                                <label className="admin-filter">
                                    <span>Filter applications</span>
                                    <select value={applicationStatus} onChange={changeApplicationStatus}>
                                        <option value="ALL">All statuses</option>
                                        <option value="PENDING">Awaiting company response</option>
                                        <option value="SAVED">Saved / not submitted</option>
                                        <option value="SCREENING">Under review</option>
                                        <option value="INTERVIEW">Interview</option>
                                        <option value="OFFER">Offer</option>
                                        <option value="ACCEPTED">Accepted</option>
                                        <option value="REJECTED">Not selected</option>
                                    </select>
                                </label>
                            </div>
                            {history.applications.length ? (
                                <>
                                    <div className="table-wrap">
                                        <table>
                                            <thead><tr><th>User</th><th>Job</th><th>Company</th><th>Status</th><th>Applied</th><th>Updated</th></tr></thead>
                                            <tbody>
                                                {history.applications.map((application) => (
                                                    <tr key={application.id}>
                                                        <td><strong>{userLabel(application.user)}</strong><small>{application.user.email}</small></td>
                                                        <td>{application.job?.title || `Job #${application.job_id}`}</td>
                                                        <td>{application.job?.company_name || "—"}</td>
                                                        <td><span className="status-pill">{application.status}</span></td>
                                                        <td>{formatDate(application.applied_at)}</td>
                                                        <td>{formatDate(application.updated_at)}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                    <Pager label="applications" pagination={applicationPagination} onChange={changeApplicationPage} />
                                </>
                            ) : <EmptyState
                                title={applicationStatus === "PENDING" ? "No pending applications" : "No applications found"}
                                message={applicationStatus === "PENDING"
                                    ? "Applications marked as submitted will appear here until their status changes."
                                    : "Applications tracked by users that match this filter will appear here."}
                            />}
                        </section>

                        <section className="admin-section">
                            <div className="admin-section-heading"><div><p className="eyebrow">Accounts</p><h2>Registered users</h2></div></div>
                            {users.length ? (
                                <div className="table-wrap">
                                    <table>
                                        <thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Last sign-in</th><th>Account</th></tr></thead>
                                        <tbody>
                                            {users.map((account) => (
                                                <tr key={account.id}>
                                                    <td>{userLabel(account)}</td>
                                                    <td>{account.email}</td>
                                                    <td>
                                                        <select aria-label={`Role for ${account.email}`} value={(account.role || "USER").toUpperCase()} onChange={(event) => updateAccount(account, { role: event.target.value })}>
                                                            <option value="USER">User</option>
                                                            <option value="ADMIN">Admin</option>
                                                        </select>
                                                    </td>
                                                    <td>{formatDate(account.last_login)}</td>
                                                    <td>
                                                        <button className="btn btn-ghost" type="button" onClick={() => updateAccount(account, { is_active: !account.is_active })}>
                                                            {account.is_active ? "Disable" : "Activate"}
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : <EmptyState title="No users found" message="Registered accounts will appear here." />}
                        </section>
                    </>
                )}
            </main>
            <Footer />
        </div>
    );
}

export default AdminDashboard;
