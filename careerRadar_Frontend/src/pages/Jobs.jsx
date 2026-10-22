import { useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import Searchbar from "../components/Searchbar";
import Jobfilters from "../components/Jobfilters";
import Jobcard from "../components/Jobcard";
import Footer from "../components/Footer";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { useJobs, useSavedJobs } from "../hooks/UseJobs";

function Jobs() {
    const { jobs, loading, error, setSearchTerm, refetch } = useJobs();
    const { savedJobIds, toggleSavedJob, savedJobsError } = useSavedJobs();
    const [filters, setFilters] = useState({ industry: "all", level: "all", jobType: "all" });
    const [page, setPage] = useState(1);
    const pageSize = 6;
    const options = useMemo(() => ({
        industries: [...new Set(jobs.flatMap((job) => job.industry || []))],
        levels: [...new Set(jobs.map((job) => job.level).filter(Boolean))],
        jobTypes: [...new Set(jobs.flatMap((job) => job.jobTypes || []))],
    }), [jobs]);
    const visibleJobs = jobs.filter((job) =>
        (filters.industry === "all" || (job.industry || []).includes(filters.industry)) &&
        (filters.level === "all" || job.level === filters.level) &&
        (filters.jobType === "all" || (job.jobTypes || []).includes(filters.jobType))
    );
    const pageCount = Math.ceil(visibleJobs.length / pageSize);
    const currentPage = Math.min(page, Math.max(pageCount, 1));
    const pageJobs = visibleJobs.slice((currentPage - 1) * pageSize, currentPage * pageSize);
    const handleSearch = (query) => {
        setPage(1);
        setSearchTerm(query);
    };
    const handleFilterChange = (name, value) => {
        setPage(1);
        setFilters((current) => ({ ...current, [name]: value }));
    };
    const resetFilters = () => {
        setPage(1);
        setFilters({ industry: "all", level: "all", jobType: "all" });
    };

    return (
        <>
            <Navbar />

            <main>
                {/* Search */}
                <section className="job-search">
                    <h1>Find Jobs</h1>

                    <Searchbar onSearch={handleSearch} />
                </section>

                {/* Search Results */}
                <section className="job-results">

                    {/* Filters */}
                    <aside className="filters">
                            <Jobfilters
                                filters={filters}
                                options={options}
                                onChange={handleFilterChange}
                                onReset={resetFilters}
                                resultCount={visibleJobs.length}
                            />
                    </aside>

                    {/* Results */}
                    <section className="results">
                        <div className="results-header">
                            <h2>Job Opportunities</h2>
                        </div>
                        {savedJobsError && <p className="inline-error" role="alert">{savedJobsError}</p>}
                        {!error && !loading && pageCount > 1 && (
                            <nav className="job-pagination" aria-label="Job listings pagination">
                                <span>
                                    Showing {(currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, visibleJobs.length)} of {visibleJobs.length} jobs
                                    <span className="job-pagination-page"> · Page {currentPage} of {pageCount}</span>
                                </span>
                                <div>
                                    <button
                                        className="btn btn-ghost"
                                        type="button"
                                        disabled={currentPage === 1}
                                        onClick={() => setPage(Math.max(1, currentPage - 1))}
                                    >
                                        Previous
                                    </button>
                                    <button
                                        className="btn btn-ghost"
                                        type="button"
                                        disabled={currentPage === pageCount}
                                        onClick={() => setPage(Math.min(pageCount, currentPage + 1))}
                                    >
                                        Next
                                    </button>
                                </div>
                            </nav>
                        )}

                        {error ? (
                            <ErrorMessage message={error} onRetry={refetch} />
                        ) : loading ? (
                            <div className="job-list" aria-label="Loading jobs">
                                {[1, 2, 3].map((item) => <div className="job-card card skeleton-card" key={item}><span /><span /><span /></div>)}
                            </div>
                        ) : visibleJobs.length ? (
                            <div className="job-list">
                                {pageJobs.map((job) => (
                                    <Jobcard
                                        job={job}
                                        key={job.id}
                                        isSaved={savedJobIds.includes(String(job.id))}
                                        onToggleSave={toggleSavedJob}
                                    />
                                ))}
                            </div>
                        ) : (
                            <EmptyState title="No matching jobs" message="Adjust your search or filters to see more opportunities." />
                        )}

                    </section>
                </section>
            </main>

            <Footer />
        </>
    );
}

export default Jobs;