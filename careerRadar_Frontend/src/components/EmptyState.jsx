export default function EmptyState({ title = "No jobs to show", message = "Try again in a little while." }) {
	return (
		<div className="empty-state card">
			<span className="empty-state-icon" aria-hidden="true">✳</span>
			<h3>{title}</h3>
			<p>{message}</p>
		</div>
	);
}