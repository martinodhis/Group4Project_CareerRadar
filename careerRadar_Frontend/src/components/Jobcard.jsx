import { Link } from "react-router-dom";
import { formatJobDate, formatSalaryRange } from "../services/JobApi.js";
import JobDescription from "./JobDescription.jsx";

// One reusable card = one job listing. Used on both Home and Jobs.
export default function Jobcard({ job, isSaved, onToggleSave }) {
  if (!job) return null;

  return (
    <article className="job-card card">
      <div className="job-card-top">
        {job.logo ? (
          <img className="job-logo" src={job.logo} alt={`${job.company} logo`} />
        ) : (
          <div className="job-logo job-logo-fallback">{job.company.charAt(0)}</div>
        )}
        <div>
          <h3 className="job-title">
            <Link to={`/jobs/${job.id}`}>{job.title}</Link>
          </h3>
          <p className="job-company">{job.company}</p>
        </div>
      </div>

      <div className="job-meta">
        <span className="tag"> {job.location}</span>
        {job.level && <span className="tag">{job.level}</span>}
        {(job.jobTypes || []).map((type) => (
          <span className="tag" key={type}>{type}</span>
        ))}
      </div>

      <JobDescription className="job-excerpt" description={job.excerpt} />
      <p className="job-salary">{formatSalaryRange(job)}</p>

      <div className="job-card-footer">
        <span className="job-date"> {formatJobDate(job.publishedAt)}</span>
        <div className="job-card-actions">
          <button
            type="button"
            className={`btn btn-save ${isSaved ? "is-saved" : ""}`}
            onClick={() => onToggleSave?.(job.id)}
          >
            {isSaved ? " Saved" : " Save"}
          </button>
          <Link className="btn" to={`/jobs/${job.id}`}>View</Link>
        </div>
      </div>
    </article>
  );
}