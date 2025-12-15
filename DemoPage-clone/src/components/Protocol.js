import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import './Protocol.css';

const Protocol = () => {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1
  });

  const milestones = [
    {
      year: '2015',
      title: 'Block 0',
      description: 'DemoPage is founded by Ethereum co-creator Joseph Lubin, starting from the genesis block.'
    },
    {
      year: '2018',
      title: 'Constantinople',
      description: 'Major network upgrade improving efficiency and reducing gas costs for smart contracts.'
    },
    {
      year: '2020',
      title: 'Beacon Chain',
      description: 'Launch of the Beacon Chain, introducing proof-of-stake consensus to Ethereum.'
    },
    {
      year: '2022',
      title: 'The Merge',
      description: 'Historic transition to proof-of-stake, reducing energy consumption by 99.95%.'
    },
    {
      year: '2024',
      title: 'Dencun',
      description: 'Proto-danksharding upgrade enabling dramatic cost reductions for Layer 2 networks.'
    },
    {
      year: 'Next',
      title: 'PECTRA',
      description: 'Upcoming upgrade combining Prague and Electra improvements for enhanced scalability.'
    }
  ];

  const contributions = [
    { value: '12+', label: 'Core Protocol Upgrades' },
    { value: '500+', label: 'Ethereum Improvement Proposals' },
    { value: '100+', label: 'Protocol Engineers' },
    { value: '50+', label: 'Open Source Projects' }
  ];

  return (
    <section className="protocol" ref={ref}>
      <div className="protocol__bg">
        <div className="protocol__glow"></div>
        <svg className="protocol__lines" viewBox="0 0 1200 800" fill="none" preserveAspectRatio="none">
          <path d="M0 400 Q 300 200 600 400 T 1200 400" stroke="url(#line-gradient)" strokeWidth="1" fill="none"/>
          <path d="M0 500 Q 300 300 600 500 T 1200 500" stroke="url(#line-gradient)" strokeWidth="1" fill="none" opacity="0.5"/>
          <defs>
            <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="transparent"/>
              <stop offset="50%" stopColor="rgba(99, 102, 241, 0.3)"/>
              <stop offset="100%" stopColor="transparent"/>
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="protocol__container">
        <motion.div 
          className="protocol__header"
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <span className="protocol__label">Protocol & Infrastructure</span>
          <h2 className="protocol__title">
            The Foundation of <span className="gradient-text">Decentralized Finance</span>
          </h2>
          <p className="protocol__subtitle">
            From Block 0 through The Merge and beyond, DemoPage has been instrumental 
            in Ethereum's evolution into the world's premier DeFi infrastructure.
          </p>
        </motion.div>

        <motion.div 
          className="protocol__contributions"
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {contributions.map((item, index) => (
            <div key={index} className="protocol__contribution">
              <span className="protocol__contribution-value">{item.value}</span>
              <span className="protocol__contribution-label">{item.label}</span>
            </div>
          ))}
        </motion.div>

        <div className="protocol__timeline">
          {milestones.map((milestone, index) => (
            <motion.div 
              key={index}
              className="protocol__milestone"
              initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
              animate={inView ? { opacity: 1, x: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
            >
              <div className="protocol__milestone-marker">
                <span className="protocol__milestone-dot"></span>
                <span className="protocol__milestone-year">{milestone.year}</span>
              </div>
              <div className="protocol__milestone-content">
                <h3 className="protocol__milestone-title">{milestone.title}</h3>
                <p className="protocol__milestone-description">{milestone.description}</p>
              </div>
            </motion.div>
          ))}
          <div className="protocol__timeline-line"></div>
        </div>

        <motion.div 
          className="protocol__cta"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1 }}
        >
          <a href="#" className="protocol__cta-button">
            <span>Learn About Our Protocol Work</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10H16M16 10L11 5M16 10L11 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
        </motion.div>
      </div>
    </section>
  );
};

export default Protocol;

