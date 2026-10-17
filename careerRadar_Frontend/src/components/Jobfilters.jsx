// Three controlled <select> dropdowns. The option lists are built
// from the real API data inside the useJobs hook, so they can never
// be out of sync with what's actually on the board.
export default function Jobfilters({
  filters = { industry: "all", level: "all", jobType: "all" },
  options = { industries: [], levels: [], jobTypes: [] },
  onChange = () => {},
  onReset = () => {},
  resultCount = 0,
}) {
  return (
    <section className="filters card">
      <div className="filters-row">
        <label className="filter-field">
          <span>Industry</span>
          <select
            value={filters.industry}
            onChange={(e) => onChange("industry", e.target.value)}
          >
            <option value="all">All industries</option>
            {options.industries.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span>Experience level</span>
          <select
            value={filters.level}
            onChange={(e) => onChange("level", e.target.value)}
          >
            <option value="all">All levels</option>
            {options.levels.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>

        <label className="filter-field">
          <span>Job type</span>
          <select
            value={filters.jobType}
            onChange={(e) => onChange("jobType", e.target.value)}
          >
            <option value="all">All types</option>
            {options.jobTypes.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>

        <button type="button" className="btn btn-ghost" onClick={onReset}>
          Reset filters
        </button>
      </div>

      <div className="filters-meta">
        <span>
          {resultCount} {resultCount === 1 ? "job" : "jobs"} on the radar
        </span>
      </div>
    </section>
  );
}