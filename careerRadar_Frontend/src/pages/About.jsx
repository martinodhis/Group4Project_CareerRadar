import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

function About() {
    return (
        <>
            <Navbar />

            <main>
                {/* Introduction */}
                <section className="about-introduction">
                    <h1>About CareerRadar</h1>

                    <p>
                        CareerRadar is a job discovery platform designed
                        to help job seekers find opportunities relevant
                        to their skills, interests, and career goals.
                    </p>
                </section>

                {/* Problem */}
                <section className="about-problem">
                    <h2>The Problem</h2>

                    <p>
                        Finding suitable employment opportunities can be
                        difficult when job vacancies are spread across
                        different platforms.
                    </p>
                </section>

                {/* Target Users */}
                <section className="about-users">
                    <h2>Who Is CareerRadar For?</h2>

                    <ul>
                        <li>University students and recent graduates</li>
                        <li>Junior developers and early-career professionals</li>
                        <li>Career changers</li>
                        <li>Freelancers and experienced professionals</li>
                    </ul>
                </section>

                {/* Features */}
                <section className="about-features">
                    <h2>What CareerRadar Offers</h2>

                    <ul>
                        <li>Job search</li>
                        <li>Job filtering</li>
                        <li>Job details</li>
                        <li>Application tracking</li>
                        <li>Career development tools</li>
                    </ul>
                </section>
            </main>

            <Footer />
        </>
    );
}

export default About;