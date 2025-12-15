import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import Hero from './components/Hero';
import Partners from './components/Partners';
import Products from './components/Products';
import Protocol from './components/Protocol';
import About from './components/About';
import News from './components/News';
import Newsletter from './components/Newsletter';
import Footer from './components/Footer';
import './App.css';

function App() {
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    // Simulate page load
    setIsLoaded(true);

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth'
          });
        }
      });
    });
  }, []);

  return (
    <div className={`app ${isLoaded ? 'app--loaded' : ''}`}>
      <Header />
      <main className="main">
        <Hero />
        <Partners />
        <Products />
        <Protocol />
        <About />
        <News />
        <Newsletter />
      </main>
      <Footer />
    </div>
  );
}

export default App;

