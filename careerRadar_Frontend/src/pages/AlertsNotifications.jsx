import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import EmptyState from "../components/EmptyState";
import Footer from "../components/Footer";
import Navbar from "../components/Navbar";
import { apiDelete, apiGet, apiPatch, apiPost, apiRequest } from "../services/Api";

function AlertsNotifications() {
    const navigate = useNavigate();
    const [alerts, setAlerts] = useState([]);
    const [notifications, setNotifications] = useState([]);
    const [form, setForm] = useState({ keyword: "", location: "", job_type: "" });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");
    const [updatingAlertId, setUpdatingAlertId] = useState(null);

    const handleRequestError = useCallback((requestError) => {
        if (requestError.status === 401) {
            navigate("/login", {
                replace: true,
                state: { from: "/alerts", message: "Your session has expired. Please sign in again." },
            });
            return;
        }
        setError(requestError.message);
    }, [navigate]);

    const loadData = useCallback(async () => {
        setError("");
        try {
            const [alertsResponse, notificationsResponse] = await Promise.all([
                apiGet("/alerts", { requireAuth: true }),
                apiGet("/notifications", { requireAuth: true }),
            ]);
            setAlerts(alertsResponse.data.alerts);
            setNotifications(notificationsResponse.data.notifications);
        } catch (requestError) {
            handleRequestError(requestError);
        } finally {
            setLoading(false);
        }
    }, [handleRequestError]);

    useEffect(() => {
        let active = true;
        Promise.all([
            apiGet("/alerts", { requireAuth: true }),
            apiGet("/notifications", { requireAuth: true }),
        ])
            .then(([alertsResponse, notificationsResponse]) => {
                if (!active) return;
                setAlerts(alertsResponse.data.alerts);
                setNotifications(notificationsResponse.data.notifications);
            })
            .catch((requestError) => {
                if (active) handleRequestError(requestError);
            })
            .finally(() => {
                if (active) setLoading(false);
            });
        return () => { active = false; };
    }, [handleRequestError]);

    const createAlert = async (event) => {
        event.preventDefault();
        setSaving(true);
        setError("");
        setMessage("");
        try {
            await apiPost("/alerts", {
                keyword: form.keyword.trim(),
                location: form.location.trim() || null,
                job_type: form.job_type.trim() || null,
            }, { requireAuth: true });
            setForm({ keyword: "", location: "", job_type: "" });
            setMessage("Job alert created. Matching new jobs will appear in Notifications after the next job sync.");
            await loadData();
        } catch (requestError) {
            handleRequestError(requestError);
        } finally {
            setSaving(false);
        }
    };

    const deleteAlert = async (alertId) => {
        setError("");
        setMessage("");
        try {
            await apiDelete(`/alerts/${alertId}`, { requireAuth: true });
            setAlerts((current) => current.filter((alert) => alert.id !== alertId));
            setMessage("Job alert deleted.");
        } catch (requestError) {
            handleRequestError(requestError);
        }
    };

    const toggleAlert = async (alert) => {
        setError("");
        setMessage("");
        setUpdatingAlertId(alert.id);
        try {
            const response = await apiRequest(`/alerts/${alert.id}`, {
                method: "PUT",
                body: { is_active: !alert.is_active },
                requireAuth: true,
            });
            setAlerts((current) => current.map((item) =>
                item.id === alert.id ? response.data : item
            ));
            setMessage(response.data.is_active ? "Job alert resumed." : "Job alert paused.");
        } catch (requestError) {
            handleRequestError(requestError);
        } finally {
            setUpdatingAlertId(null);
        }
    };

    const markRead = async (notificationId) => {
        setError("");
        try {
            await apiPatch(`/notifications/${notificationId}/read`, {}, { requireAuth: true });
            setNotifications((current) => current.map((item) =>
                item.id === notificationId ? { ...item, is_read: true } : item
            ));
        } catch (requestError) {
            handleRequestError(requestError);
        }
    };

    const markAllRead = async () => {
        setError("");
        try {
            await apiPatch("/notifications/read-all", {}, { requireAuth: true });
            setNotifications((current) => current.map((item) => ({ ...item, is_read: true })));
        } catch (requestError) {
            handleRequestError(requestError);
        }
    };

    return (
        <div className="site-shell">
            <Navbar />
            <main className="dashboard-page">
                <section className="dashboard-heading">
                    <p className="eyebrow">Stay up to date</p>
                    <h1>Job alerts &amp; notifications</h1>
                    <p>Active alerts create in-app notifications when matching jobs are found during a job sync. Manage alerts here; notifications are shown below.</p>
                </section>
                {error && <p className="inline-error" role="alert">{error}</p>}
                {message && <p className="inline-success" role="status">{message}</p>}
                <section className="admin-section">
                    <div className="admin-section-heading"><div><p className="eyebrow">Saved searches</p><h2>Create a job alert</h2></div></div>
                    <form className="alert-form" onSubmit={createAlert}>
                        <label>Keyword<input value={form.keyword} onChange={(event) => setForm((current) => ({ ...current, keyword: event.target.value }))} placeholder="e.g. data analyst" required maxLength="160" /></label>
                        <label>Location (optional)<input value={form.location} onChange={(event) => setForm((current) => ({ ...current, location: event.target.value }))} placeholder="e.g. London" /></label>
                        <label>Job type (optional)<input value={form.job_type} onChange={(event) => setForm((current) => ({ ...current, job_type: event.target.value }))} placeholder="e.g. Full-time" /></label>
                        <button className="btn" type="submit" disabled={saving}>{saving ? "Creating…" : "Create alert"}</button>
                    </form>
                    {loading ? <p className="page-state">Loading alerts…</p> : alerts.length ? (
                        <ul className="alert-list">
                            {alerts.map((alert) => (
                                <li key={alert.id}>
                                    <span>
                                        <strong>{alert.keyword}</strong>
                                        {[alert.location, alert.job_type].filter(Boolean).map((item) => <small key={item}>{item}</small>)}
                                        <small>{alert.is_active ? "Active" : "Paused"}</small>
                                    </span>
                                    <div className="alert-actions">
                                        <button className="btn btn-ghost" type="button" onClick={() => toggleAlert(alert)} disabled={updatingAlertId !== null}>
                                            {updatingAlertId === alert.id ? "Saving…" : alert.is_active ? "Pause" : "Resume"}
                                        </button>
                                        <button className="btn btn-ghost" type="button" onClick={() => deleteAlert(alert.id)} disabled={updatingAlertId !== null}>Delete</button>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    ) : <EmptyState title="No job alerts yet" message="Create an alert to watch for new roles that match your interests." />}
                </section>
                <section className="admin-section">
                    <div className="admin-section-heading">
                        <div><p className="eyebrow">Recent updates</p><h2>Notifications</h2></div>
                        {notifications.some((item) => !item.is_read) && <button className="btn btn-ghost" type="button" onClick={markAllRead}>Mark all read</button>}
                    </div>
                    {loading ? <p className="page-state">Loading notifications…</p> : notifications.length ? (
                        <ul className="notification-list">
                            {notifications.map((item) => (
                                <li className={item.is_read ? "" : "notification-unread"} key={item.id}>
                                    <div><p>{item.message}</p><small>{item.created_at ? new Date(item.created_at).toLocaleString() : ""}</small></div>
                                    {item.job_id && <Link className="btn btn-ghost" to={`/jobs/${item.job_id}`}>View job</Link>}
                                    {!item.is_read && <button className="btn btn-ghost" type="button" onClick={() => markRead(item.id)}>Mark read</button>}
                                </li>
                            ))}
                        </ul>
                    ) : <EmptyState title="Nothing new" message="Notifications for matching new job listings will appear here." />}
                </section>
                <div className="profile-actions"><button className="btn btn-ghost" type="button" onClick={loadData}>Refresh</button></div>
            </main>
            <Footer />
        </div>
    );
}

export default AlertsNotifications;
