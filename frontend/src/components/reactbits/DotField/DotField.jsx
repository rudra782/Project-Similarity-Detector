import { useEffect, useRef } from 'react';
import './DotField.css';

export default function DotField({
  dotColor = '#7dd3fc',
  backgroundColor = 'transparent',
  spacing = 28,
  radius = 1.5,
  influenceRadius = 120,
  className = ''
}) {
  const canvas = useRef(null);

  useEffect(() => {
    const c = canvas.current;
    if (!c) return;

    const ctx = c.getContext('2d');

    const mouse = {
      x: -9999,
      y: -9999
    };

    let frame;
    let ro;

    const resize = () => {
      const rect = c.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);

      c.width = rect.width * dpr;
      c.height = rect.height * dpr;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const handlePointerMove = e => {
      const rect = c.getBoundingClientRect();

      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      if (
        x >= 0 &&
        x <= rect.width &&
        y >= 0 &&
        y <= rect.height
      ) {
        mouse.x = x;
        mouse.y = y;
      } else {
        mouse.x = -9999;
        mouse.y = -9999;
      }
    };

    const draw = () => {
      const rect = c.getBoundingClientRect();

      ctx.clearRect(0, 0, rect.width, rect.height);

      if (backgroundColor !== 'transparent') {
        ctx.fillStyle = backgroundColor;
        ctx.fillRect(0, 0, rect.width, rect.height);
      }

      for (let x = spacing / 2; x < rect.width; x += spacing) {
        for (let y = spacing / 2; y < rect.height; y += spacing) {
          const distance = Math.hypot(
            mouse.x - x,
            mouse.y - y
          );

          const influence = Math.max(
            0,
            1 - distance / influenceRadius
          );

          const scale = 1 + influence * 3;

          ctx.beginPath();
          ctx.fillStyle = dotColor;
          ctx.arc(
            x,
            y,
            radius * scale,
            0,
            Math.PI * 2
          );
          ctx.fill();
        }
      }

      frame = requestAnimationFrame(draw);
    };

    resize();

    ro = new ResizeObserver(resize);
    ro.observe(c);

    // IMPORTANT:
    // listen on window, NOT canvas
    window.addEventListener(
      'pointermove',
      handlePointerMove,
      { passive: true }
    );

    draw();

    return () => {
      cancelAnimationFrame(frame);
      ro.disconnect();

      window.removeEventListener(
        'pointermove',
        handlePointerMove
      );
    };
  }, [
    dotColor,
    backgroundColor,
    spacing,
    radius,
    influenceRadius
  ]);

  return (
    <canvas
      ref={canvas}
      className={`dot-field ${className}`}
      aria-hidden="true"
    />
  );
}