import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import './Partners.css';

const Partners = () => {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1
  });

  const partners = [
    { name: 'JPMorgan', initials: 'JP' },
    { name: 'Microsoft', initials: 'MS' },
    { name: 'Mastercard', initials: 'MC' },
    { name: 'Samsung', initials: 'SM' },
    { name: 'PayPal', initials: 'PP' },
    { name: 'EY', initials: 'EY' },
    { name: 'AMD', initials: 'AMD' },
    { name: 'Santander', initials: 'SA' }
  ];

  return (
    <section className="partners" ref={ref}>
      <div className="partners__container">
        <motion.div
          className="partners__header"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5 }}
        >
          <p className="partners__title">Trusted by industry leaders worldwide</p>
        </motion.div>

        <motion.div 
          className="partners__grid"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {partners.map((partner, index) => (
            <motion.div 
              key={index}
              className="partners__logo"
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.1 * index }}
              whileHover={{ scale: 1.05 }}
            >
              <span className="partners__logo-text">{partner.initials}</span>
              <span className="partners__logo-name">{partner.name}</span>
            </motion.div>
          ))}
        </motion.div>

        <motion.div
          className="partners__stats"
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <div className="partners__stat">
            <span className="partners__stat-value">500+</span>
            <span className="partners__stat-label">Enterprise Partners</span>
          </div>
          <div className="partners__stat">
            <span className="partners__stat-value">180+</span>
            <span className="partners__stat-label">Countries</span>
          </div>
          <div className="partners__stat">
            <span className="partners__stat-value">50+</span>
            <span className="partners__stat-label">Fortune 500 Clients</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default Partners;

