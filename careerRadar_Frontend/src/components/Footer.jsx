import { Link } from "react-router-dom";

export default function Footer() {
	return (
		<footer className="footer">
			<div className="container footer-inner">
				<Link to="/" className="brand footer-brand">
					<span className="brand-dot" aria-hidden="true" />
					Career<span className="brand-accent">Radar</span>
				</Link>
				<p>Find your next opportunity with CareerRadar.</p>
				<span className="footer-copyright">© {new Date().getFullYear()} CareerRadar</span>
			</div>
		</footer>
	);
}