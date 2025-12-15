import React from 'react';
import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import './News.css';

const News = () => {
  const [ref, inView] = useInView({
    triggerOnce: true,
    threshold: 0.1
  });

  const articles = [
    {
      category: 'Product Update',
      title: 'MetaMask Introduces Enhanced Security Features for Portfolio Management',
      excerpt: 'New security features include hardware wallet integration, advanced transaction signing, and improved phishing protection.',
      date: 'Dec 10, 2024',
      readTime: '4 min read',
      featured: true
    },
    {
      category: 'Ethereum',
      title: 'The Road to PECTRA: What\'s Next for Ethereum',
      excerpt: 'An in-depth look at the upcoming Prague-Electra upgrade and its implications for scalability.',
      date: 'Dec 8, 2024',
      readTime: '6 min read',
      featured: false
    },
    {
      category: 'Developer',
      title: 'Building with Linea: A Developer\'s Guide to zkEVM',
      excerpt: 'Everything you need to know to start building scalable dApps on Linea\'s zkEVM network.',
      date: 'Dec 5, 2024',
      readTime: '8 min read',
      featured: false
    },
    {
      category: 'Company',
      title: 'DemoPage Expands Global Team with 100 New Hires',
      excerpt: 'Continued growth in engineering, product, and go-to-market teams across all regions.',
      date: 'Dec 2, 2024',
      readTime: '3 min read',
      featured: false
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  return (
    <section className="news" ref={ref}>
      <div className="news__container">
        <motion.div 
          className="news__header"
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
        >
          <span className="news__label">Latest News</span>
          <h2 className="news__title">
            Stay Updated with <span className="gradient-text">DemoPage</span>
          </h2>
          <p className="news__subtitle">
            The latest product updates, protocol developments, and insights from our team.
          </p>
        </motion.div>

        <motion.div 
          className="news__grid"
          variants={containerVariants}
          initial="hidden"
          animate={inView ? "visible" : "hidden"}
        >
          {articles.map((article, index) => (
            <motion.a 
              key={index}
              href="#"
              className={`news__card ${article.featured ? 'news__card--featured' : ''}`}
              variants={itemVariants}
              whileHover={{ y: -6, transition: { duration: 0.3 } }}
            >
              <div className="news__card-image">
                <div className="news__card-image-placeholder">
                  <svg viewBox="0 0 100 100" fill="none">
                    <rect width="100" height="100" fill="url(#news-gradient)"/>
                    <circle cx="30" cy="35" r="15" fill="rgba(255,255,255,0.1)"/>
                    <path d="M10 70 L40 50 L60 60 L90 35" stroke="rgba(255,255,255,0.2)" strokeWidth="2" fill="none"/>
                    <defs>
                      <linearGradient id="news-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#1a1a2e"/>
                        <stop offset="100%" stopColor="#16213e"/>
                      </linearGradient>
                    </defs>
                  </svg>
                </div>
              </div>
              
              <div className="news__card-content">
                <span className="news__card-category">{article.category}</span>
                <h3 className="news__card-title">{article.title}</h3>
                <p className="news__card-excerpt">{article.excerpt}</p>
                <div className="news__card-meta">
                  <span>{article.date}</span>
                  <span className="news__card-separator">•</span>
                  <span>{article.readTime}</span>
                </div>
              </div>
              
              <div className="news__card-arrow">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                  <path d="M7 17L17 7M17 7H9M17 7V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
            </motion.a>
          ))}
        </motion.div>

        <motion.div 
          className="news__cta"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.6 }}
        >
          <a href="#" className="news__cta-link">
            View All Articles
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10H16M16 10L11 5M16 10L11 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
        </motion.div>
      </div>
    </section>
  );
};

export default News;

