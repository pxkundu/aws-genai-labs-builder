import React from 'react';
import { motion } from 'framer-motion';
import './Hero.css';

const Hero = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 40 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.8,
        ease: [0.25, 0.46, 0.45, 0.94]
      }
    }
  };

  const stats = [
    { value: '100M+', label: 'Monthly Active Users' },
    { value: '$20B+', label: 'Assets Under Custody' },
    { value: '10K+', label: 'Developer Teams' },
    { value: '7+', label: 'Years Building Web3' }
  ];

  return (
    <section className="hero">
      {/* Background Effects */}
      <div className="hero__bg">
        <div className="hero__glow hero__glow--1"></div>
        <div className="hero__glow hero__glow--2"></div>
        <div className="hero__glow hero__glow--3"></div>
        <div className="hero__grid"></div>
        <div className="hero__particles">
          {[...Array(30)].map((_, i) => (
            <span key={i} className="hero__particle" style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`
            }}></span>
          ))}
        </div>
      </div>

      <motion.div 
        className="hero__content"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="hero__badge" variants={itemVariants}>
          <span className="hero__badge-dot"></span>
          <span>Building the Future of Finance</span>
        </motion.div>

        <motion.h1 className="hero__title" variants={itemVariants}>
          Building the Era of
          <span className="hero__title-gradient"> Decentralized</span>
          <br />
          <span className="hero__title-gradient">Finance</span>
        </motion.h1>

        <motion.p className="hero__description" variants={itemVariants}>
          DemoPage is the leading blockchain and web3 software company. 
          We connect people and markets through distributed, open-source infrastructure, 
          empowering users to take control of their digital assets and identity.
        </motion.p>

        <motion.div className="hero__ctas" variants={itemVariants}>
          <button className="hero__cta hero__cta--primary">
            <span>Explore Our Products</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 10H16M16 10L11 5M16 10L11 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <button className="hero__cta hero__cta--secondary">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M8 6L14 10L8 14V6Z" fill="currentColor"/>
            </svg>
            <span>Watch Video</span>
          </button>
        </motion.div>

        <motion.div className="hero__stats" variants={itemVariants}>
          {stats.map((stat, index) => (
            <div key={index} className="hero__stat">
              <span className="hero__stat-value">{stat.value}</span>
              <span className="hero__stat-label">{stat.label}</span>
            </div>
          ))}
        </motion.div>
      </motion.div>

      {/* Animated Ethereum Logo */}
      <motion.div 
        className="hero__visual"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 0.5, ease: 'easeOut' }}
      >
        <div className="hero__eth-container">
          <svg className="hero__eth-logo" viewBox="0 0 256 417" fill="none">
            <path opacity="0.6" d="M127.961 0L125.166 9.5V285.168L127.961 287.958L255.923 212.32L127.961 0Z" fill="url(#eth-gradient-1)"/>
            <path opacity="0.8" d="M127.962 0L0 212.32L127.962 287.959V154.158V0Z" fill="url(#eth-gradient-2)"/>
            <path opacity="0.6" d="M127.961 312.187L126.386 314.108V412.306L127.961 416.905L255.999 236.587L127.961 312.187Z" fill="url(#eth-gradient-1)"/>
            <path opacity="0.8" d="M127.962 416.905V312.187L0 236.587L127.962 416.905Z" fill="url(#eth-gradient-2)"/>
            <path opacity="0.2" d="M127.961 287.958L255.922 212.32L127.961 154.159V287.958Z" fill="url(#eth-gradient-3)"/>
            <path opacity="0.6" d="M0 212.32L127.962 287.959V154.158L0 212.32Z" fill="url(#eth-gradient-3)"/>
            <defs>
              <linearGradient id="eth-gradient-1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1"/>
                <stop offset="100%" stopColor="#8b5cf6"/>
              </linearGradient>
              <linearGradient id="eth-gradient-2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8b5cf6"/>
                <stop offset="100%" stopColor="#06b6d4"/>
              </linearGradient>
              <linearGradient id="eth-gradient-3" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#06b6d4"/>
                <stop offset="100%" stopColor="#6366f1"/>
              </linearGradient>
            </defs>
          </svg>
          <div className="hero__eth-glow"></div>
          <div className="hero__eth-ring hero__eth-ring--1"></div>
          <div className="hero__eth-ring hero__eth-ring--2"></div>
          <div className="hero__eth-ring hero__eth-ring--3"></div>
        </div>
      </motion.div>

      {/* Scroll Indicator */}
      <motion.div 
        className="hero__scroll"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
      >
        <span>Scroll to explore</span>
        <div className="hero__scroll-indicator">
          <span className="hero__scroll-dot"></span>
        </div>
      </motion.div>
    </section>
  );
};

export default Hero;

