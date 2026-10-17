const ALLOWED_TAGS = new Set([
  'a', 'b', 'blockquote', 'br', 'code', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
  'hr', 'i', 'li', 'ol', 'p', 'pre', 's', 'span', 'strong', 'u', 'ul',
]);

const DISCARDED_TAGS = new Set([
  'embed', 'iframe', 'math', 'noscript', 'object', 'script', 'style', 'svg', 'template',
]);

function sanitizeNode(node) {
  if (node.nodeType === Node.TEXT_NODE) {
    return document.createTextNode(node.textContent || '');
  }
  if (node.nodeType !== Node.ELEMENT_NODE) {
    return document.createDocumentFragment();
  }

  const tagName = node.tagName.toLowerCase();
  if (DISCARDED_TAGS.has(tagName)) {
    return document.createDocumentFragment();
  }

  const children = document.createDocumentFragment();
  for (const child of node.childNodes) {
    children.append(sanitizeNode(child));
  }
  if (!ALLOWED_TAGS.has(tagName)) {
    return children;
  }

  const element = document.createElement(tagName);
  if (tagName === 'a') {
    const href = node.getAttribute('href');
    if (href) {
      try {
        const url = new URL(href, window.location.origin);
        if (['http:', 'https:', 'mailto:'].includes(url.protocol)) {
          element.setAttribute('href', url.href);
          element.setAttribute('target', '_blank');
          element.setAttribute('rel', 'noopener noreferrer');
        }
      } catch {
        // Keep the link text, but discard an invalid destination.
      }
    }
  }
  element.append(children);
  return element;
}

function sanitizeDescription(description) {
  const parsed = new DOMParser().parseFromString(description, 'text/html');
  const safeContent = document.createDocumentFragment();
  for (const child of parsed.body.childNodes) {
    safeContent.append(sanitizeNode(child));
  }

  const container = document.createElement('div');
  container.append(safeContent);
  return container.innerHTML;
}

export default function JobDescription({ description, className }) {
  const content = typeof description === 'string' ? description : '';

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizeDescription(content) }}
    />
  );
}
