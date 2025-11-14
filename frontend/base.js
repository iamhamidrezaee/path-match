// Mobile navigation toggle
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.getElementById('primary-navigation');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
}

// Navigate to signup
document.getElementById('signup').addEventListener('click', function() 
{ window.location.href = 'signup.html'; 
});

document.getElementById('signup1').addEventListener('click', function() 
{ window.location.href = 'signup.html'; 
});

// Sticky nav style on scroll
const nav = document.querySelector('.nav');
if (nav) {
  const onScroll = () => {
    if (window.scrollY > 8) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });
}

// Smooth scroll offset is handled by CSS scroll-margin-top

// Reveal on scroll using IntersectionObserver
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!prefersReducedMotion && 'IntersectionObserver' in window) {
  const revealEls = document.querySelectorAll('.reveal');
  const observer = new IntersectionObserver((entries, obs) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      }
    }
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(el => observer.observe(el));
}

// Close mobile menu on link click (single-page nav convenience)
document.addEventListener('click', (e) => {
  const target = e.target;
  if (!(target instanceof Element)) return;
  if (target.closest('.nav-links a') && navLinks && navLinks.classList.contains('open')) {
    navLinks.classList.remove('open');
    if (navToggle) navToggle.setAttribute('aria-expanded', 'false');
  }
});

// Animated dot pattern backgrounds
class DotPattern {
  constructor(canvasId, config = {}) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    
    this.ctx = this.canvas.getContext('2d');
    this.config = {
      dotSize: config.dotSize || 3,
      spacing: config.spacing || 24,
      color: config.color || 'rgba(179, 27, 27, 0.4)',
      animationSpeed: config.animationSpeed || 0.0008,
      waveAmplitude: config.waveAmplitude || 15,
      pattern: config.pattern || 'grid', // 'grid' or 'scatter'
      fadeEdges: config.fadeEdges !== false
    };
    
    this.dots = [];
    this.time = 0;
    this.animationFrame = null;
    
    this.init();
  }
  
  init() {
    this.resize();
    this.createDots();
    this.animate();
    
    window.addEventListener('resize', () => {
      this.resize();
      this.createDots();
    });
  }
  
  resize() {
    const rect = this.canvas.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
  }
  
  createDots() {
    this.dots = [];
    const cols = Math.ceil(this.width / this.config.spacing);
    const rows = Math.ceil(this.height / this.config.spacing);
    
    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const x = i * this.config.spacing + this.config.spacing / 2;
        const y = j * this.config.spacing + this.config.spacing / 2;
        
        this.dots.push({
          baseX: x,
          baseY: y,
          x: x,
          y: y,
          phase: Math.random() * Math.PI * 2,
          opacity: 1
        });
      }
    }
  }
  
  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    this.time += this.config.animationSpeed;
    
    this.dots.forEach(dot => {
      // Wave animation
      const offsetX = Math.sin(this.time + dot.phase) * this.config.waveAmplitude;
      const offsetY = Math.cos(this.time + dot.phase * 0.7) * this.config.waveAmplitude;
      
      dot.x = dot.baseX + offsetX;
      dot.y = dot.baseY + offsetY;
      
      // Fade edges
      if (this.config.fadeEdges) {
        const distFromEdgeX = Math.min(dot.baseX, this.width - dot.baseX);
        const distFromEdgeY = Math.min(dot.baseY, this.height - dot.baseY);
        const fadeDistance = 100;
        const fadeX = Math.min(distFromEdgeX / fadeDistance, 1);
        const fadeY = Math.min(distFromEdgeY / fadeDistance, 1);
        dot.opacity = Math.min(fadeX, fadeY);
      }
      
      // Draw dot
      this.ctx.beginPath();
      this.ctx.arc(dot.x, dot.y, this.config.dotSize, 0, Math.PI * 2);
      
      // Parse color and apply opacity
      const colorMatch = this.config.color.match(/rgba?\(([^)]+)\)/);
      if (colorMatch) {
        const rgbValues = colorMatch[1].split(',').map(v => v.trim());
        if (rgbValues.length === 4) {
          const baseOpacity = parseFloat(rgbValues[3]);
          this.ctx.fillStyle = `rgba(${rgbValues[0]}, ${rgbValues[1]}, ${rgbValues[2]}, ${baseOpacity * dot.opacity})`;
        } else {
          this.ctx.fillStyle = `rgba(${rgbValues.join(', ')}, ${dot.opacity})`;
        }
      } else {
        this.ctx.fillStyle = this.config.color;
      }
      
      this.ctx.fill();
    });
    
    this.animationFrame = requestAnimationFrame(() => this.animate());
  }
  
  destroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }
}

// Initialize dot patterns
document.addEventListener('DOMContentLoaded', () => {
  // Hero section - subtle animated pattern on the right
  new DotPattern('hero-canvas', {
    dotSize: 2.5,
    spacing: 28,
    color: 'rgba(179, 27, 27, 0.35)',
    animationSpeed: 0.0005,
    waveAmplitude: 12,
    fadeEdges: true
  });
  
  // Problem section - denser pattern on the left
  new DotPattern('problem-canvas', {
    dotSize: 2,
    spacing: 22,
    color: 'rgba(179, 27, 27, 0.25)',
    animationSpeed: 0.0006,
    waveAmplitude: 10,
    fadeEdges: true
  });
  
  // CTA section - bold pattern on white background
  new DotPattern('cta-canvas', {
    dotSize: 3,
    spacing: 26,
    color: 'rgba(255, 255, 255, 0.5)',
    animationSpeed: 0.0004,
    waveAmplitude: 15,
    fadeEdges: true
  });
});


