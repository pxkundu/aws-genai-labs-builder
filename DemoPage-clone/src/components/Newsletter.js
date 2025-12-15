import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import './Newsletter.css';

const Newsletter = () => {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email) {
      setIsSubmitted(true);
      setEmail('');
    }
  };

  return (
    <section className="newsletter" ref={ref}>
      <div className="newsletter__bg">
        <div className="newsletter__glow newsletter__glow--1"></div>
        <div className="newsletter__glow newsletter__glow--2"></div>
        <div className="newsletter__pattern"></div>
      </div>

      <motion.div 
        className="newsletter__container"
        initial={{ opacity: 0, y: 40 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.6 }}
      >
        <div className="newsletter__content">
          <span className="newsletter__label">Newsletter</span>
          <h2 className="newsletter__title">
            Follow Our <span className="gradient-text">Journey</span>
          </h2>
          <p className="newsletter__description">
            Get the latest updates on our products, protocol developments, and 
            insights from the frontier of decentralized technology.
          </p>

          {!isSubmitted ? (
            <form className="newsletter__form" onSubmit={handleSubmit}>
              <div className="newsletter__input-wrapper">
                <svg className="newsletter__input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M3 5L10 11L17 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  <rect x="2" y="4" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1.5"/>
                </svg>
                <input
                  type="email"
                  className="newsletter__input"
                  placeholder="Enter your email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className="newsletter__submit">
                <span>Subscribe</span>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M4 10H16M16 10L11 5M16 10L11 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </form>
          ) : (
            <motion.div 
              className="newsletter__success"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4 }}
            >
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2"/>
                <path d="M10 16L14 20L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Thanks for subscribing! Check your inbox to confirm.</span>
            </motion.div>
          )}

          <p className="newsletter__privacy">
            By subscribing, you agree to our <a href="#">Privacy Policy</a> and consent to receive updates.
          </p>
        </div>

        <div className="newsletter__features">
          <div className="newsletter__feature">
            <svg viewBox="0 0 32 32" fill="none">
              <rect x="4" y="6" width="24" height="20" rx="2" stroke="currentColor" strokeWidth="2"/>
              <path d="M4 10L16 18L28 10" stroke="currentColor" strokeWidth="2"/>
            </svg>
            <div>
              <h4>Weekly Digest</h4>
              <p>Curated news and insights every week</p>
            </div>
          </div>
          <div className="newsletter__feature">
            <svg viewBox="0 0 32 32" fill="none">
              <circle cx="16" cy="16" r="12" stroke="currentColor" strokeWidth="2"/>
              <path d="M16 8V16L20 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <div>
              <h4>Early Access</h4>
              <p>Be first to know about new products</p>
            </div>
          </div>
          <div className="newsletter__feature">
            <svg viewBox="0 0 32 32" fill="none">
              <path d="M16 4L20 12H28L22 18L24 28L16 22L8 28L10 18L4 12H12L16 4Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
            </svg>
            <div>
              <h4>Exclusive Content</h4>
              <p>Subscriber-only insights and research</p>
            </div>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default Newsletter;

