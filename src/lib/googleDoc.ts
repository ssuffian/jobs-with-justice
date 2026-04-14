/*
 * googleDoc.ts — fetch and clean content from public Google Docs
 *
 * EXPORTED FUNCTIONS
 * ------------------
 * fetchGoogleDocHtml(docId, tabId?)
 *   Fetches a Google Doc (or specific tab) exported as HTML, strips
 *   Google-specific markup, and returns clean HTML safe to render with
 *   set:html in Astro. Preserves: headings, paragraphs, lists, tables,
 *   links (with target=_blank), images (src/alt only), and inline
 *   formatting (bold, italic, underline) detected from the doc's CSS.
 *   Strips: the first <h1> (Google exports the doc title as h1),
 *   empty <p>s, all class/style/id attributes, <script> tags.
 *
 * fetchGoogleDocText(docId, tabId?)
 *   Fetches a Google Doc (or specific tab) as plain text.
 *
 * USAGE NOTES
 * -----------
 * - The doc must be publicly accessible ("Anyone with the link can view").
 * - Tab IDs look like "t.brhmcroz5hsj" — find them in the doc URL when the tab is open.
 * - Both functions return '' on any fetch or parse failure (never throw).
 * - DOC_ID is the long alphanumeric string in the Google Docs URL:
 *     https://docs.google.com/document/d/<DOC_ID>/edit
 */

function cleanGoogleDocHtml(html: string): string {
  const classFormats = new Map<string, string[]>();
  const styleMatch = html.match(/<style[^>]*>([\s\S]*?)<\/style>/i);
  if (styleMatch) {
    const css = styleMatch[1];
    const ruleRegex = /\.([\w-]+)\s*\{([^}]*)\}/g;
    let m;
    while ((m = ruleRegex.exec(css)) !== null) {
      const className = m[1];
      const rules = m[2].toLowerCase();
      const tags: string[] = [];
      if (/font-weight\s*:\s*(700|bold)/.test(rules)) tags.push('b');
      if (/font-style\s*:\s*italic/.test(rules)) tags.push('em');
      if (/text-decoration[^;]*underline/.test(rules)) tags.push('u');
      if (tags.length) classFormats.set(className, tags);
    }
  }

  const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
  if (!bodyMatch) return '';
  let body = bodyMatch[1];

  body = body.replace(/<script[\s\S]*?<\/script>/gi, '');

  body = body.replace(/<a [^>]*>/gi, (match) => {
    const hrefMatch = match.match(/href="([^"]*)"/);
    return hrefMatch ? `<a href="${hrefMatch[1]}" target="_blank" rel="noopener noreferrer">` : '<a>';
  });

  body = body.replace(/<img [^>]*>/gi, (match) => {
    const srcMatch = match.match(/src="([^"]*)"/);
    const altMatch = match.match(/alt="([^"]*)"/);
    if (!srcMatch) return '';
    const alt = altMatch ? ` alt="${altMatch[1]}"` : '';
    return `<img src="${srcMatch[1]}"${alt}>`;
  });

  body = body.replace(/<span([^>]*)>/gi, (_, attrs) => {
    const tags = new Set<string>();
    const classMatch = attrs.match(/class="([^"]*)"/);
    if (classMatch) {
      for (const cls of classMatch[1].split(/\s+/)) {
        for (const t of (classFormats.get(cls) || [])) tags.add(t);
      }
    }
    const styleVal = (attrs.match(/style="([^"]*)"/)?.[1] || '').toLowerCase();
    if (/font-weight\s*:\s*(700|bold)/.test(styleVal)) tags.add('b');
    if (/font-style\s*:\s*italic/.test(styleVal)) tags.add('em');
    if (/text-decoration[^;]*underline/.test(styleVal)) tags.add('u');
    return [...tags].map(t => `<${t}>`).join('');
  });
  body = body.replace(/<\/span>/gi, '</u></em></b>');

  body = body.replace(/<(h[1-6]|p|ul|ol|li|b|strong|em|i|u|br|hr|table|thead|tbody|tfoot|tr|th|td)[^>]*>/gi, '<$1>');
  body = body.replace(/<\/?div[^>]*>/gi, '');
  body = body.replace(/<p>\s*(<br\s*\/?>\s*)*<\/p>/gi, '');
  body = body.replace(/<h1>[^<]*<\/h1>/, '');

  return body.trim();
}

export async function fetchGoogleDocHtml(docId: string, tabId?: string): Promise<string> {
  try {
    const url = tabId
      ? `https://docs.google.com/document/d/${docId}/export?format=html&tab=${tabId}`
      : `https://docs.google.com/document/d/${docId}/export?format=html`;
    const res = await fetch(url);
    if (!res.ok) return '';
    return cleanGoogleDocHtml(await res.text());
  } catch {
    return '';
  }
}

export interface HiringPosition {
  title: string;
  timeFrame: string;
  payment: string;
  tabId: string;
}

export async function fetchHiringIndex(docId: string, indexTabId: string): Promise<HiringPosition[]> {
  try {
    const url = `https://docs.google.com/document/d/${docId}/export?format=html&tab=${indexTabId}`;
    const res = await fetch(url);
    if (!res.ok) return [];
    const html = await res.text();

    const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    if (!bodyMatch) return [];
    const body = bodyMatch[1];

    const positions: HiringPosition[] = [];

    // Split on top-level list items (level-0) which contain position names
    // Structure: <ul ...-0><li>Title</li></ul> followed by <ul ...-1><li>metadata</li>...</ul>
    const parts = body.split(/<ul[^>]*lst-kix_[^>]*-0[^>]*>/i);

    for (const part of parts) {
      // Extract position title from the first <li> in a level-0 list
      const titleMatch = part.match(/<li[^>]*>[\s\S]*?<\/li>/i);
      if (!titleMatch) continue;
      const title = titleMatch[0].replace(/<[^>]+>/g, '').replace(/&nbsp;/g, '').trim();
      if (!title) continue;

      // Extract metadata from the subsequent level-1 list
      const level1Match = part.match(/<ul[^>]*lst-kix_[^>]*-1[^>]*>([\s\S]*?)<\/ul>/i);
      if (!level1Match) continue;

      const items = level1Match[1].match(/<li[^>]*>[\s\S]*?<\/li>/gi) || [];
      let timeFrame = '';
      let payment = '';
      let tabId = '';

      for (const item of items) {
        const text = item.replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').trim();
        if (text.startsWith('Time Frame:')) timeFrame = text.replace('Time Frame:', '').trim();
        else if (text.startsWith('Payment:')) payment = text.replace('Payment:', '').trim();
        else if (text.startsWith('Tab:')) tabId = text.replace('Tab:', '').trim();
      }

      if (title && tabId) {
        positions.push({ title, timeFrame, payment, tabId });
      }
    }

    return positions;
  } catch {
    return [];
  }
}

export async function fetchGoogleDocText(docId: string, tabId?: string): Promise<string> {
  try {
    const url = tabId
      ? `https://docs.google.com/document/d/${docId}/export?format=txt&tab=${tabId}`
      : `https://docs.google.com/document/d/${docId}/export?format=txt`;
    const res = await fetch(url);
    if (!res.ok) return '';
    return (await res.text()).trim();
  } catch {
    return '';
  }
}
