import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import "./GlassNavbar.css";

const menus = [
  {
    id: "analyze",
    label: "Analyze",
    links: [
      { label: "New Analysis", description: "Start a new project comparison.", to: "/analyze" },
      { label: "How analysis works", description: "See how each signal is evaluated.", to: "/how-it-works" },
    ],
  },
  {
    id: "repository",
    label: "Repository",
    links: [
      { label: "Browse Projects", description: "Explore previously analyzed work.", to: "/projects" },
      { label: "New Analysis", description: "Compare a project with the repository.", to: "/analyze" },
    ],
  },
  {
    id: "how-it-works",
    label: "How It Works",
    links: [
      { label: "Similarity Pipeline", description: "Follow the analysis from input to result.", to: "/how-it-works" },
      { label: "Algorithms", description: "Review the techniques behind each score.", to: "/how-it-works" },
    ],
  },
];

const panelMotion = {
  initial: { opacity: 0, height: 0, y: -6 },
  animate: { opacity: 1, height: "auto", y: 0 },
  exit: { opacity: 0, height: 0, y: -6 },
  transition: { duration: 0.24, ease: [0.22, 1, 0.36, 1] },
};

export default function GlassNavbar({ LinkComponent }) {
  const [openMenu, setOpenMenu] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const navRef = useRef(null);

  const closeAll = () => {
    setOpenMenu(null);
    setMobileOpen(false);
  };

  useEffect(() => {
    const handlePointerDown = (event) => {
      if (!navRef.current?.contains(event.target)) closeAll();
    };
    const handleKeyDown = (event) => {
      if (event.key === "Escape") closeAll();
    };
    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <header className="glass-nav-shell" ref={navRef}>
      <nav className="glass-navbar" aria-label="Main navigation">
        <LinkComponent to="/" className="glass-nav-brand" onClick={closeAll}>
          <span className="glass-nav-mark">PS</span>
          <span>Project Similarity</span>
        </LinkComponent>

        <div className="glass-nav-desktop">
          {menus.map((menu) => (
            <button
              key={menu.id}
              type="button"
              className="glass-nav-trigger"
              aria-expanded={openMenu === menu.id}
              aria-controls={`nav-dropdown-${menu.id}`}
              onClick={() => setOpenMenu(openMenu === menu.id ? null : menu.id)}
            >
              {menu.label}
              <span className="glass-nav-chevron" aria-hidden="true">⌄</span>
            </button>
          ))}
        </div>

        <LinkComponent to="/analyze" className="glass-nav-cta" onClick={closeAll}>
          New Analysis <span aria-hidden="true">→</span>
        </LinkComponent>

        <button
          type="button"
          className="glass-nav-menu-button"
          aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={mobileOpen}
          aria-controls="mobile-navigation-panel"
          onClick={() => {
            setOpenMenu(null);
            setMobileOpen(!mobileOpen);
          }}
        >
          <span /><span />
        </button>
      </nav>

      <AnimatePresence mode="wait">
        {openMenu && (
          <motion.div
            {...panelMotion}
            id={`nav-dropdown-${openMenu}`}
            className="glass-nav-dropdown"
          >
            <div className="glass-nav-dropdown-inner">
              <p>{menus.find((menu) => menu.id === openMenu).label}</p>
              {menus.find((menu) => menu.id === openMenu).links.map((link) => (
                <LinkComponent key={link.label} to={link.to} className="glass-nav-card" onClick={closeAll}>
                  <span><strong>{link.label}</strong><small>{link.description}</small></span>
                  <i aria-hidden="true">→</i>
                </LinkComponent>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div {...panelMotion} id="mobile-navigation-panel" className="glass-nav-mobile">
            {[menus[0].links[0], menus[1].links[0], menus[2].links[0]].map((link, index) => (
              <LinkComponent key={link.label} to={link.to} onClick={closeAll}>
                <span>{menus[index].label}</span><i aria-hidden="true">→</i>
              </LinkComponent>
            ))}
            <LinkComponent to="/analyze" className="glass-nav-mobile-cta" onClick={closeAll}>
              New Analysis <span aria-hidden="true">→</span>
            </LinkComponent>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
