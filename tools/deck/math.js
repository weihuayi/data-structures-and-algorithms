/* Opt-in LaTeX rendering. Code, SVG labels and select options remain literal. */
document.addEventListener('DOMContentLoaded', () => {
  renderMathInElement(document.querySelector('main'), {
    delimiters: [
      {left: '\\[', right: '\\]', display: true},
      {left: '\\(', right: '\\)', display: false}
    ],
    ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'option', 'svg'],
    throwOnError: false,
    trust: false
  });
});
