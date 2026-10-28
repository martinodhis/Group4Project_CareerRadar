import Navbar from "../components/Navbar";
import Searchbar from "../components/Searchbar";
import Jobcard from "../components/Jobcard";
import Footer from "../components/Footer";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import { useJobs, useSavedJobs } from "../hooks/UseJobs";
import onlineJobSearch from "../assets/online-job-search.svg";

function Home() {
    const { jobs, loading, error, setSearchTerm, refetch } = useJobs();
    const { savedJobIds, toggleSavedJob, savedJobsError } = useSavedJobs();

    return (
        <>
            <Navbar />

            <main>
                {/* Hero / Introduction */}
                <section className="hero">
                    <h1>Find Your Next Opportunity</h1>

                    <p>
                        Discover job opportunities that match your
                        skills, interests, and career goals.
                    </p>

                    <Searchbar onSearch={setSearchTerm} />
                </section>

                {/* Recent Jobs */}
                <section className="recent-jobs">
                    <h2>Recent Jobs</h2>
                    {savedJobsError && <p className="inline-error" role="alert">{savedJobsError}</p>}

                    {error ? (
                        <ErrorMessage message={error} onRetry={refetch} />
                    ) : loading ? (
                        <div className="job-list" aria-label="Loading jobs">
                            {[1, 2, 3, 4, 5, 6].map((item) => <div className="job-card card skeleton-card" key={item}><span /><span /><span /></div>)}
                        </div>
                    ) : jobs.length ? (
                        <div className="job-list">
                            {jobs.slice(0, 6).map((job) => (
                                <Jobcard
                                    job={job}
                                    key={job.id}
                                    isSaved={savedJobIds.includes(String(job.id))}
                                    onToggleSave={toggleSavedJob}
                                />
                            ))}
                        </div>
                    ) : (
                        <EmptyState title="No recent jobs found" message="Try a different keyword or check back soon for new opportunities." />
                    )}
                </section>

                <section className="job-search-promo" aria-labelledby="job-search-promo-title">
                    <div className="job-search-promo-copy">
                        <p className="eyebrow">Your next opportunity starts here</p>
                        <h2 id="job-search-promo-title">Search online. Find your fit. Apply with confidence.</h2>
                        <p>Explore roles, compare opportunities, and take the next step in your career—all in one place.</p>
                    </div>
                    <img
                        className="job-search-promo-image"
                        src={onlineJobSearch}
                        alt="People searching online for jobs and submitting applications from their computers"
                        loading="lazy"
                    />
                </section>
            </main>

            <Footer />
        </>
    );
}

export default Home;