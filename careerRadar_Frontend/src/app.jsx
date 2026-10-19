import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/UseAuth';
import About from './pages/About';
import AlertsNotifications from './pages/AlertsNotifications';
import AdminDashboard from './pages/AdminDashboard';
import ApplicationsDashboard from './pages/ApplicationsDashboard';
import Home from './pages/Home';
import JobDetails from './pages/JobDetails';
import Jobs from './pages/Jobs';
import Login from './pages/Login';
import Profile from './pages/Profile';
import SavedJobs from './pages/SavedJobs';
import "./styles/global.css";

function ProtectedRoute({ children, adminOnly = false }) {
    const { user, loading, sessionError } = useAuth();
    const location = useLocation();
    if (loading) return <main className="page-state">Checking your session…</main>;
    if (sessionError) {
        return (
            <main className="page-state session-error" role="alert">
                <p>Could not verify your account: {sessionError}</p>
                <button className="btn" type="button" onClick={() => window.location.reload()}>Refresh the page</button>
            </main>
        );
    }
    if (!user) {
        return (
            <Navigate
                to="/register"
                replace
                state={{
                    message: "Create an account or sign in to browse job opportunities.",
                    returnTo: { path: `${location.pathname}${location.search}` },
                }}
            />
        );
    }
    if (adminOnly && user.role?.toUpperCase() !== 'ADMIN') {
        return (
            <main className="admin-access-page">
                <section className="admin-access-card card">
                    <p className="eyebrow">Administrator setup</p>
                    <h1>Administrator access required</h1>
                    <p>You are signed in as <strong>{user.email}</strong>. Regular accounts cannot view system users, history, or applications.</p>
                    <p>To make this account an administrator, run this from the <code>CareerRadar_Backend</code> folder on the server:</p>
                    <code className="admin-command">./.venv/bin/flask --app run.py promote-admin "{user.email}"</code>
                    <p>Confirm the promotion in the terminal, then sign out and sign in again. Only run this command on a backend you control.</p>
                    <Link className="btn" to="/dashboard">Return to my applications</Link>
                </section>
            </main>
        );
    }
    return children;
}

function AppRoutes() {
    return (
        <AuthProvider>
            <Routes>
                <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
                <Route path="/jobs" element={<ProtectedRoute><Jobs /></ProtectedRoute>} />
                <Route path="/jobs/:id" element={<ProtectedRoute><JobDetails /></ProtectedRoute>} />
                <Route path="/about" element={<About />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Login register />} />
                <Route
                    path="/dashboard"
                    element={<ProtectedRoute><ApplicationsDashboard /></ProtectedRoute>}
                />
                <Route
                    path="/profile"
                    element={<ProtectedRoute><Profile /></ProtectedRoute>}
                />
                <Route
                    path="/saved-jobs"
                    element={<ProtectedRoute><SavedJobs /></ProtectedRoute>}
                />
                <Route
                    path="/alerts"
                    element={<ProtectedRoute><AlertsNotifications /></ProtectedRoute>}
                />
                <Route
                    path="/admin"
                    element={<ProtectedRoute adminOnly><AdminDashboard /></ProtectedRoute>}
                />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </AuthProvider>
    );
}

function App() {
    return (
        <BrowserRouter>
            <AppRoutes />
        </BrowserRouter>
    );
}

export default App;