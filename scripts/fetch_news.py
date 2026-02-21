import feedparser
import html
from datetime import datetime, timezone

# AIニュースのRSSフィード（全部無料・APIキー不要）
FEEDS = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "ニュース",
        "emoji": "📰"
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/ai/feed/",
        "category": "ニュース",
        "emoji": "📰"
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        "category": "ニュース",
        "emoji": "📰"
    },
    {
        "name": "MIT Technology Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "category": "ニュース",
        "emoji": "📰"
    },
    {
        "name": "arXiv CS.AI（論文）",
        "url": "http://arxiv.org/rss/cs.AI",
        "category": "論文・研究",
        "emoji": "🔬"
    },
    {
        "name": "arXiv CS.LG（機械学習）",
        "url": "http://arxiv.org/rss/cs.LG",
        "category": "論文・研究",
        "emoji": "🔬"
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "category": "AIモデル・ツール",
        "emoji": "🤗"
    },
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "category": "AIモデル・ツール",
        "emoji": "🤖"
    },
]

CATEGORY_ORDER = ["ニュース", "AIモデル・ツール", "論文・研究"]


def clean_html_tags(text):
    """HTMLタグを除去して文字列をクリーンにする"""
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_articles(feed_info, max_items=5):
    try:
        feed = feedparser.parse(feed_info["url"])
        articles = []
        for entry in feed.entries[:max_items]:
            raw_summary = entry.get("summary", "") or ""
            clean_summary = clean_html_tags(raw_summary)[:200]

            articles.append({
                "title": html.escape(entry.get("title", "タイトルなし")),
                "link": entry.get("link", "#"),
                "summary": html.escape(clean_summary),
                "source": feed_info["name"],
                "category": feed_info["category"],
                "emoji": feed_info["emoji"],
            })
        print(f"  ✓ {feed_info['name']}: {len(articles)}件")
        return articles
    except Exception as e:
        print(f"  ✗ {feed_info['name']}: {e}")
        return []


def generate_html(all_articles, fetch_time):
    jst_str = fetch_time.strftime("%Y年%m月%d日 %H:%M") + " UTC"

    # カテゴリ別に整理
    categories = {}
    for article in all_articles:
        cat = article["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(article)

    sections_html = ""
    for cat in CATEGORY_ORDER:
        if cat not in categories:
            continue
        articles = categories[cat]
        emoji = articles[0]["emoji"] if articles else ""
        cards_html = ""
        for a in articles:
            summary_html = (
                f'<p class="summary">{a["summary"]}…</p>'
                if a["summary"] else ""
            )
            cards_html += f"""
            <a href="{a['link']}" target="_blank" rel="noopener" class="card">
              <span class="source-tag">{a['source']}</span>
              <h3>{a['title']}</h3>
              {summary_html}
              <span class="read-more">続きを読む →</span>
            </a>"""

        sections_html += f"""
        <section class="category-section">
          <h2 class="category-title">{emoji} {cat}</h2>
          <div class="cards">{cards_html}</div>
        </section>"""

    total = len(all_articles)

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#0f0f1a">
  <title>AI最新情報ダッシュボード</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
      background: #0f0f1a;
      color: #e0e0e0;
      min-height: 100vh;
    }}
    header {{
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      padding: 18px 16px 14px;
      text-align: center;
      border-bottom: 1px solid #2a2a4a;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(10px);
    }}
    header h1 {{
      font-size: 1.4rem;
      font-weight: 700;
      background: linear-gradient(135deg, #a78bfa, #60a5fa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .meta {{
      display: flex;
      justify-content: center;
      gap: 12px;
      margin-top: 6px;
      font-size: 0.72rem;
      color: #666;
    }}
    .badge {{
      background: #2a2a4a;
      color: #a78bfa;
      padding: 2px 8px;
      border-radius: 999px;
    }}
    main {{
      padding: 16px;
      max-width: 800px;
      margin: 0 auto;
    }}
    .category-section {{
      margin-bottom: 32px;
    }}
    .category-title {{
      font-size: 0.95rem;
      font-weight: 600;
      color: #a78bfa;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #2a2a4a;
    }}
    .cards {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .card {{
      display: block;
      background: #1a1a2e;
      border: 1px solid #2a2a4a;
      border-radius: 12px;
      padding: 14px;
      text-decoration: none;
      color: inherit;
      transition: border-color 0.15s ease, background 0.15s ease;
    }}
    .card:hover {{ border-color: #4a4a8a; background: #1e1e35; }}
    .card:active {{ transform: scale(0.99); }}
    .source-tag {{
      display: inline-block;
      font-size: 0.68rem;
      background: #2a2a4a;
      color: #a78bfa;
      padding: 2px 8px;
      border-radius: 999px;
      margin-bottom: 7px;
      font-weight: 500;
    }}
    .card h3 {{
      font-size: 0.9rem;
      line-height: 1.45;
      margin-bottom: 6px;
      color: #e8e8e8;
      font-weight: 500;
    }}
    .summary {{
      font-size: 0.78rem;
      color: #777;
      line-height: 1.55;
      margin-bottom: 8px;
    }}
    .read-more {{
      font-size: 0.72rem;
      color: #60a5fa;
      font-weight: 500;
    }}
    footer {{
      text-align: center;
      padding: 24px 16px;
      font-size: 0.72rem;
      color: #444;
      border-top: 1px solid #1a1a2e;
    }}
  </style>
</head>
<body>
  <header>
    <h1>🤖 AI最新情報ダッシュボード</h1>
    <div class="meta">
      <span>更新: {jst_str}</span>
      <span class="badge">{total}件</span>
    </div>
  </header>
  <main>
    {sections_html}
  </main>
  <footer>毎日自動更新 · GitHub Actions + GitHub Pages</footer>
</body>
</html>"""


def main():
    print("=== AIニュース取得開始 ===")
    fetch_time = datetime.now(timezone.utc)

    all_articles = []
    for feed_info in FEEDS:
        articles = fetch_articles(feed_info)
        all_articles.extend(articles)

    print(f"\n合計 {len(all_articles)} 件取得")

    html_content = generate_html(all_articles, fetch_time)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✓ index.html を生成しました")


if __name__ == "__main__":
    main()
