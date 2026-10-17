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
    const handleFilterChange = (name, value) => setFilters((current) => ({ ...current, [name]: value }));
    const resetFilters = () => setFilters({ industry: "all", level: "all", jobType: "all" });

    return (
        <>
            <Navbar />

            <main>
                {/* Search */}
                <section className="job-search">
                    <h1>Find Jobs</h1>

                    <Searchbar onSearch={setSearchTerm} />
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

                        {error ? (
                            <ErrorMessage message={error} onRetry={refetch} />
                        ) : loading ? (
                            <div className="job-list" aria-label="Loading jobs">
                                {[1, 2, 3].map((item) => <div className="job-card card skeleton-card" key={item}><span /><span /><span /></div>)}
                            </div>
                        ) : visibleJobs.length ? (
                            <div className="job-list">
                                {visibleJobs.map((job) => (
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