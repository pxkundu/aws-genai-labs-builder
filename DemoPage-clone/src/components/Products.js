import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import './Products.css';

const Products = () => {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1
  });

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 50 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const products = [
    {
      name: 'MetaMask',
      description: 'The world\'s leading self-custodial wallet. Secure, simple, and trusted by over 100 million users worldwide to store, send, and receive crypto.',
      stats: [
        { value: '100M+', label: 'Monthly Users' },
        { value: '30M+', label: 'Mobile Downloads' }
      ],
      icon: (
        <svg viewBox="0 0 40 40" fill="none" className="products__card-icon">
          <path d="M33.5 8L21 17L23.5 11.5L33.5 8Z" fill="#E17726"/>
          <path d="M6.5 8L18.9 17.1L16.5 11.5L6.5 8Z" fill="#E27625"/>
          <path d="M29 27L26 32.5L33 34.5L35 27.1L29 27Z" fill="#E27625"/>
          <path d="M5 27.1L7 34.5L14 32.5L11 27L5 27.1Z" fill="#E27625"/>
          <path d="M13.5 18.5L11.5 21.5L18.5 21.8L18.2 14.5L13.5 18.5Z" fill="#E27625"/>
          <path d="M26.5 18.5L21.7 14.4L21.5 21.8L28.5 21.5L26.5 18.5Z" fill="#E27625"/>
          <path d="M14 32.5L18 30.5L14.5 27.2L14 32.5Z" fill="#E27625"/>
          <path d="M22 30.5L26 32.5L25.5 27.2L22 30.5Z" fill="#E27625"/>
        </svg>
      ),
      accentColor: '#f97316',
      link: '#'
    },
    {
      name: 'Linea',
      description: 'The next-generation zkEVM rollup network. Build and scale your dApps with Ethereum-level security and dramatically lower costs.',
      stats: [
        { value: '3M+', label: 'Unique Addresses' },
        { value: '150+', label: 'dApps Deployed' }
      ],
      icon: (
        <svg viewBox="0 0 40 40" fill="none" className="products__card-icon">
          <circle cx="20" cy="20" r="16" stroke="currentColor" strokeWidth="2"/>
          <path d="M12 20H28" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <path d="M20 12V28" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          <circle cx="20" cy="20" r="6" fill="currentColor" opacity="0.3"/>
        </svg>
      ),
      accentColor: '#6366f1',
      link: '#'
    },
    {
      name: 'Infura',
      description: 'The most powerful suite of high availability APIs and developer tools for Ethereum and IPFS. Connect your dApps to blockchain networks instantly.',
      stats: [
        { value: '430K+', label: 'Developers' },
        { value: '1T+', label: 'API Requests Daily' }
      ],
      icon: (
        <svg viewBox="0 0 40 40" fill="none" className="products__card-icon">
          <path d="M20 6L32 13V27L20 34L8 27V13L20 6Z" stroke="currentColor" strokeWidth="2"/>
          <path d="M20 6V20" stroke="currentColor" strokeWidth="2"/>
          <path d="M20 20L32 13" stroke="currentColor" strokeWidth="2"/>
          <path d="M20 20L8 13" stroke="currentColor" strokeWidth="2"/>
          <circle cx="20" cy="20" r="4" fill="currentColor"/>
        </svg>
      ),
      accentColor: '#ec4899',
      link: '#'
    },
    {
      name: 'MetaMask Developer',
      description: 'Powerful SDKs and APIs for seamless Web3 integration. Build wallet connections and blockchain interactions into any application.',
      stats: [
        { value: '10K+', label: 'Developer Teams' },
        { value: '50K+', label: 'SDK Downloads' }
      ],
      icon: (
        <svg viewBox="0 0 40 40" fill="none" className="products__card-icon">
          <rect x="8" y="10" width="24" height="20" rx="2" stroke="currentColor" strokeWidth="2"/>
          <path d="M14 18L18 22L14 26" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M22 26H28" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      ),
      accentColor: '#22c55e',
      link: '#'
    }
  ];

  return (
    <section className="products" ref={ref}>
      <div className="products__container">
        <motion.div 
          className="products__header"
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <span className="products__label">Our Products</span>
          <h2 className="products__title">
            The most trusted <span className="gradient-text">Web3 infrastructure</span>
          </h2>
          <p className="products__subtitle">
            Our suite of products powers the decentralized web, from self-custody wallets 
            to developer tools and enterprise-grade infrastructure.
          </p>
        </motion.div>

        <motion.div 
          className="products__grid"
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
        >
          {products.map((product, index) => (
            <motion.a 
              key={index} 
              href={product.link}
              className="products__card"
              variants={itemVariants}
              style={{ '--accent-color': product.accentColor }}
              whileHover={{ y: -8, transition: { duration: 0.3 } }}
            >
              <div className="products__card-header">
                <div className="products__card-icon-wrapper" style={{ color: product.accentColor }}>
                  {product.icon}
                </div>
                <svg className="products__card-arrow" width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M7 17L17 7M17 7H9M17 7V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              
              <h3 className="products__card-title">{product.name}</h3>
              <p className="products__card-description">{product.description}</p>
              
              <div className="products__card-stats">
                {product.stats.map((stat, i) => (
                  <div key={i} className="products__card-stat">
                    <span className="products__card-stat-value" style={{ color: product.accentColor }}>
                      {stat.value}
                    </span>
                    <span className="products__card-stat-label">{stat.label}</span>
                  </div>
                ))}
              </div>

              <div className="products__card-glow" style={{ background: product.accentColor }}></div>
            </motion.a>
          ))}
        </motion.div>

        <motion.div 
          className="products__cta"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.8 }}
        >
          <a href="#" className="products__cta-link">
            View All Products
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10H16M16 10L11 5M16 10L11 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
        </motion.div>
      </div>
    </section>
  );
};

export default Products;

