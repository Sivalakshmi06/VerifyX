import React, { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();
  const aboutRef = useRef(null);
  const featuresRef = useRef(null);
  const howRef = useRef(null);
  const contactRef = useRef(null);

  const scrollTo = (ref) => ref.current?.scrollIntoView({ behavior: 'smooth' });

  const teamMembers = [
    { name: "Sivalakshmi S", role: "AI & Backend Developer", email: "Sivalakshmi26062006@gmail.com" },
    { name: "Shobika S",     role: "Frontend Developer",     email: "Shobikookies18@gmail.com" },
    { name: "Sanjana R",     role: "ML Model & Data",        email: "" },
    { name: "Swetha K",      role: "UI/UX & Testing",        email: "" },
  ];

  const features = [
    { icon: "📰", title: "Fake News Detection",   desc: "Analyze news articles in English & Tamil using NLP and cross-reference against 10+ trusted sources." },
    { icon: "😡", title: "Emotion Analysis",       desc: "Detect emotional manipulation, fear-mongering, scam tactics, and phishing attempts in messages." },
    { icon: "🎬", title: "Deepfake Detection",     desc: "Multi-method image analysis using ELA, noise patterns, frequency domain, and facial consistency." },
    { icon: "🔍", title: "News Verification",      desc: "Verify any news claim against live RSS feeds from trusted Tamil and English news outlets." },
  ];

  const steps = [
    { num: "01", title: "Paste or Upload",  desc: "Enter text, a URL, or upload an image/video." },
    { num: "02", title: "AI Analysis",      desc: "Our models cross-reference sources and run multi-method checks." },
    { num: "03", title: "Get Results",      desc: "Receive a clear verdict with confidence score and explanation." },
    { num: "04", title: "Stay Informed",    desc: "View history, download reports, and track your analyses." },
  ];

  return (
    <div className="lp-root">

      {/* ── Newspaper background layer ── */}
      <div className="lp-newspaper-bg" aria-hidden="true" />
      <div className="lp-dark-overlay" aria-hidden="true" />

      {/* ── NAV ── */}
      <nav className="lp-nav">
        <div className="lp-nav-logo" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          🗞️ Fake News Detector
        </div>
        <div className="lp-nav-links">
          <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>Home</button>
          <button onClick={() => scrollTo(aboutRef)}>About</button>
          <button onClick={() => scrollTo(featuresRef)}>Features</button>
          <button onClick={() => scrollTo(howRef)}>How It Works</button>
          <button onClick={() => scrollTo(contactRef)}>Contact</button>
          <button className="lp-nav-login" onClick={() => navigate('/login')}>Login</button>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section className="lp-hero">
        <div className="lp-hero-glass">
          <p className="lp-hero-eyebrow">AI · Multilingual · Real-time</p>
          <h1 className="lp-hero-title">AI Fake News<br/>Detection</h1>
          <p className="lp-hero-sub">Check if news is real or fake instantly</p>
          <div className="lp-hero-btns">
            <button className="lp-btn-primary" onClick={() => navigate('/login')}>
              🔍 Detect Now
            </button>
            <button className="lp-btn-secondary" onClick={() => scrollTo(featuresRef)}>
              📖 Learn More
            </button>
          </div>
          <div className="lp-hero-badges">
            {features.map((f, i) => (
              <span key={i} className="lp-badge">{f.icon} {f.title}</span>
            ))}
          </div>
        </div>
      </section>

      {/* ── ABOUT ── */}
      <section className="lp-section" ref={aboutRef} id="about">
        <div className="lp-section-inner">
          <h2 className="lp-section-title">About This Project</h2>
          <p className="lp-section-sub">
            What it is, why it matters, and how it was built.
          </p>

          {/* Project overview */}
          <div className="lp-about-overview">
            <div className="lp-about-text">
              <h3 className="lp-about-heading">What is this?</h3>
              <p>
                The <strong>AI-Based Multilingual Fake News Detection System</strong> is an intelligent
                web platform that helps users verify the authenticity of news articles, social media posts,
                images, and videos — in both <strong>English and Tamil</strong>.
              </p>
              <p>
                In today's digital age, misinformation spreads faster than truth. This system uses
                <strong> Natural Language Processing (NLP)</strong>, <strong>machine learning models</strong>,
                and <strong>live news cross-referencing</strong> to give users an instant, data-backed verdict
                on whether a piece of content is real or fake.
              </p>
              <h3 className="lp-about-heading" style={{ marginTop: '24px' }}>Why does it matter?</h3>
              <p>
                Fake news causes real harm — from public panic and political manipulation to financial scams
                and health misinformation. Our system empowers everyday users to fact-check content before
                sharing it, reducing the spread of misinformation at the source.
              </p>
            </div>

            <div className="lp-about-highlights">
              <div className="lp-highlight-card">
                <span className="lp-highlight-icon">🌐</span>
                <div>
                  <p className="lp-highlight-title">Multilingual</p>
                  <p className="lp-highlight-desc">Supports English & Tamil news detection natively</p>
                </div>
              </div>
              <div className="lp-highlight-card">
                <span className="lp-highlight-icon">🤖</span>
                <div>
                  <p className="lp-highlight-title">AI-Powered</p>
                  <p className="lp-highlight-desc">NLP classifiers + live source cross-referencing</p>
                </div>
              </div>
              <div className="lp-highlight-card">
                <span className="lp-highlight-icon">📡</span>
                <div>
                  <p className="lp-highlight-title">Real-time</p>
                  <p className="lp-highlight-desc">Checks against 10+ live trusted news RSS feeds</p>
                </div>
              </div>
              <div className="lp-highlight-card">
                <span className="lp-highlight-icon">🛡️</span>
                <div>
                  <p className="lp-highlight-title">Scam Detection</p>
                  <p className="lp-highlight-desc">Identifies emotional manipulation & phishing tactics</p>
                </div>
              </div>
              <div className="lp-highlight-card">
                <span className="lp-highlight-icon">🎬</span>
                <div>
                  <p className="lp-highlight-title">Deepfake Analysis</p>
                  <p className="lp-highlight-desc">5-method image forensics: ELA, noise, frequency & more</p>
                </div>
              </div>
              <div className="lp-highlight-card">
                <span className="lp-highlight-icon">📊</span>
                <div>
                  <p className="lp-highlight-title">Confidence Scores</p>
                  <p className="lp-highlight-desc">Every result comes with a detailed explanation & score</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tech stack */}
          <div className="lp-tech-stack">
            <p className="lp-tech-label">Built with</p>
            <div className="lp-tech-pills">
              {['React.js', 'Node.js', 'Flask (Python)', 'MongoDB', 'NLP / TF-IDF', 'EasyOCR', 'OpenCV', 'Google News RSS', 'REST APIs'].map((t, i) => (
                <span key={i} className="lp-tech-pill">{t}</span>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* ── FEATURES ── */}
      <section className="lp-section lp-section-alt" ref={featuresRef} id="features">
        <div className="lp-section-inner">
          <h2 className="lp-section-title">Features</h2>
          <p className="lp-section-sub">Everything you need to fight misinformation.</p>
          <div className="lp-features-grid">
            {features.map((f, i) => (
              <div key={i} className="lp-feature-card">
                <div className="lp-feature-icon">{f.icon}</div>
                <h3 className="lp-feature-title">{f.title}</h3>
                <p className="lp-feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="lp-section" ref={howRef} id="how">
        <div className="lp-section-inner">
          <h2 className="lp-section-title">How It Works</h2>
          <p className="lp-section-sub">Four simple steps to verify any news.</p>
          <div className="lp-steps-grid">
            {steps.map((s, i) => (
              <div key={i} className="lp-step-card">
                <div className="lp-step-num">{s.num}</div>
                <h3 className="lp-step-title">{s.title}</h3>
                <p className="lp-step-desc">{s.desc}</p>
              </div>
            ))}
          </div>
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <button className="lp-btn-primary" onClick={() => navigate('/login')}>
              🔍 Try It Now — No Login Required
            </button>
          </div>
        </div>
      </section>

      {/* ── CONTACT ── */}
      <section className="lp-section lp-section-alt" ref={contactRef} id="contact">
        <div className="lp-section-inner">
          <h2 className="lp-section-title">Contact Us</h2>
          <p className="lp-section-sub">Have questions or feedback? Reach out to the team.</p>
          <div className="lp-contact-list">
            {teamMembers.filter(m => m.email).map((m, i) => (
              <a key={i} href={`mailto:${m.email}`} className="lp-contact-item">
                <span className="lp-contact-icon">✉️</span>
                <div>
                  <p className="lp-contact-name">{m.name}</p>
                  <p className="lp-contact-email">{m.email}</p>
                </div>
              </a>
            ))}
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className="lp-footer">
        © 2026 Fake News Detection System — Built with ❤️ by CSE 3rd Year Students
      </footer>

    </div>
  );
};

export default LandingPage;
