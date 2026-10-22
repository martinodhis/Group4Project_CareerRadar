import { Link, NavLink, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/UseAuth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [logoutError, setLogoutError] = useState("");

  const handleLogout = async () => {
    if (!window.confirm("Are you sure you want to log out?")) return;

    setLogoutError("");
    try {
      await logout();
    } catch (error) {
      setLogoutError(error.message);
    } finally {
      navigate("/login", { replace: true, state: { message: "You have been signed out." } });
    }
  };

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">
          <span className="brand-dot" aria-hidden="true" />
          Career<span className="brand-accent">Radar</span>
        </Link>

        <nav className="nav-links">
          <NavLink to="/" end>Home</NavLink>
          <NavLink to="/jobs">Jobs</NavLink>
          <NavLink to="/about">About</NavLink>
          {user ? (
            <>
              <NavLink to="/saved-jobs">Saved jobs</NavLink>
              <NavLink to="/dashboard">Applications</NavLink>
              <NavLink to="/alerts">Alerts</NavLink>
              <NavLink to="/profile">Profile</NavLink>
              {user.role?.toUpperCase() === "ADMIN" && <NavLink to="/admin">Admin</NavLink>}
            </>
          ) : (
            <>
              <NavLink to="/login">Sign in</NavLink>
              <NavLink to="/register">Register</NavLink>
            </>
          )}
          {user && <button className="nav-logout" type="button" onClick={handleLogout}>Sign out</button>}
        </nav>
      </div>
      {logoutError && <p className="nav-error" role="alert">{logoutError}</p>}
    </header>
  );
}