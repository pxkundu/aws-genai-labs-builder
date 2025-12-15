import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Header.css';

const Header = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { 
      label: 'Products', 
      submenu: ['MetaMask', 'Linea', 'Infura', 'MetaMask Developer'] 
    },
    { 
      label: 'Ecosystem', 
      submenu: ['Partners', 'Developers', 'Community'] 
    },
    { 
      label: 'Company', 
      submenu: ['About', 'Careers', 'News', 'Contact'] 
    },
    { label: 'Blog', submenu: null }
  ];

  return (
    <motion.header 
      className={`header ${isScrolled ? 'header--scrolled' : ''}`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
    >
      <div className="header__container">
        <a href="#" className="header__logo">
          <svg className="header__logo-icon" viewBox="0 0 40 40" fill="none">
            <circle cx="20" cy="20" r="18" stroke="url(#logo-gradient)" strokeWidth="2"/>
            <path d="M12 20L18 26L28 14" stroke="url(#logo-gradient)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <defs>
              <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1"/>
                <stop offset="50%" stopColor="#8b5cf6"/>
                <stop offset="100%" stopColor="#06b6d4"/>
              </linearGradient>
            </defs>
          </svg>
          <span className="header__logo-text">DemoPage</span>
        </a>

        <nav className="header__nav">
          {navLinks.map((link, index) => (
            <div key={index} className="header__nav-item">
              <a href="#" className="header__nav-link">
                {link.label}
                {link.submenu && (
                  <svg className="header__nav-arrow" width="12" height="12" viewBox="0 0 12 12">
                    <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </a>
              {link.submenu && (
                <div className="header__dropdown">
                  {link.submenu.map((item, i) => (
                    <a key={i} href="#" className="header__dropdown-link">{item}</a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>

        <div className="header__actions">
          <a href="#" className="header__action-link">Developers</a>
          <button className="header__cta">
            <span>Get Started</span>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8H13M13 8L9 4M13 8L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        <button 
          className="header__mobile-toggle"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          aria-label="Toggle menu"
        >
          <span className={`header__mobile-bar ${isMobileMenuOpen ? 'open' : ''}`}></span>
          <span className={`header__mobile-bar ${isMobileMenuOpen ? 'open' : ''}`}></span>
          <span className={`header__mobile-bar ${isMobileMenuOpen ? 'open' : ''}`}></span>
        </button>
      </div>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            className="header__mobile-menu"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            {navLinks.map((link, index) => (
              <a key={index} href="#" className="header__mobile-link">{link.label}</a>
            ))}
            <button className="header__cta header__cta--mobile">
              <span>Get Started</span>
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
};

export default Header;

