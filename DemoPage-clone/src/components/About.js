import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import './About.css';

const About = () => {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1
  });

  const features = [
    {
      icon: (
        <svg viewBox="0 0 40 40" fill="none">
          <circle cx="20" cy="20" r="16" stroke="currentColor" strokeWidth="2"/>
          <path d="M14 20L18 24L26 16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      ),
      title: 'Security First',
      description: 'Enterprise-grade security with rigorous audits and battle-tested infrastructure protecting billions in assets.'
    },
    {
      icon: (
        <svg viewBox="0 0 40 40" fill="none">
          <path d="M20 8V32" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M8 20H32" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="20" cy="20" r="12" stroke="currentColor" strokeWidth="2"/>
        </svg>
      ),
      title: 'Global Scale',
      description: 'Infrastructure serving millions of users across 180+ countries, processing billions of transactions.'
    },
    {
      icon: (
        <svg viewBox="0 0 40 40" fill="none">
          <rect x="8" y="12" width="24" height="16" rx="2" stroke="currentColor" strokeWidth="2"/>
          <path d="M12 20H18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M12 24H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="26" cy="22" r="4" stroke="currentColor" strokeWidth="2"/>
        </svg>
      ),
      title: 'Open Source',
      description: 'Committed to transparency and collaboration through open-source development and public audits.'
    },
    {
      icon: (
        <svg viewBox="0 0 40 40" fill="none">
          <path d="M20 8L32 16V28L20 36L8 28V16L20 8Z" stroke="currentColor" strokeWidth="2"/>
          <path d="M20 20V36" stroke="currentColor" strokeWidth="2"/>
          <path d="M20 20L32 16" stroke="currentColor" strokeWidth="2"/>
          <path d="M20 20L8 16" stroke="currentColor" strokeWidth="2"/>
        </svg>
      ),
      title: 'Decentralized',
      description: 'Building technology that puts control back in users\' hands, enabling true financial sovereignty.'
    }
  ];

  const team = [
    { name: 'Joseph Lubin', role: 'Founder & CEO', image: 'JL' },
    { name: 'Sarah Thompson', role: 'Chief Technology Officer', image: 'ST' },
    { name: 'Michael Chen', role: 'Head of Product', image: 'MC' },
    { name: 'Elena Rodriguez', role: 'VP Engineering', image: 'ER' }
  ];

  return (
    <section className="about" ref={ref}>
      <div className="about__container">
        <div className="about__grid">
          <motion.div 
            className="about__content"
            initial={{ opacity: 0, x: -50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <span className="about__label">About DemoPage</span>
            <h2 className="about__title">
              First Mover in <span className="gradient-text">Web3</span>
            </h2>
            <p className="about__description">
              DemoPage was founded by Ethereum's co-creator, Joseph Lubin, with a vision 
              to build technology that makes finance more open, accessible, and equitable for everyone.
            </p>
            <p className="about__description">
              From our founding in 2015 through today, we've grown from a small team of 
              blockchain enthusiasts into a global organization with over 900 employees 
              across 30+ countries, all united by our mission to unlock the potential of 
              decentralized technology.
            </p>

            <div className="about__ctas">
              <a href="#" className="about__cta about__cta--primary">
                <span>Our Story</span>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M4 10H16M16 10L11 5M16 10L11 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </a>
              <a href="#" className="about__cta about__cta--secondary">
                <span>Join Our Team</span>
              </a>
            </div>
          </motion.div>

          <motion.div 
            className="about__visual"
            initial={{ opacity: 0, x: 50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="about__team-grid">
              {team.map((member, index) => (
                <motion.div 
                  key={index}
                  className="about__team-member"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={inView ? { opacity: 1, scale: 1 } : {}}
                  transition={{ duration: 0.4, delay: 0.4 + index * 0.1 }}
                >
                  <div className="about__team-avatar">
                    <span>{member.image}</span>
                  </div>
                  <h4 className="about__team-name">{member.name}</h4>
                  <p className="about__team-role">{member.role}</p>
                </motion.div>
              ))}
            </div>
            <div className="about__visual-glow"></div>
          </motion.div>
        </div>

        <motion.div 
          className="about__features"
          initial={{ opacity: 0, y: 50 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          {features.map((feature, index) => (
            <div key={index} className="about__feature">
              <div className="about__feature-icon">
                {feature.icon}
              </div>
              <h3 className="about__feature-title">{feature.title}</h3>
              <p className="about__feature-description">{feature.description}</p>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default About;

