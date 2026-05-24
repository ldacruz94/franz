from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for current information. Use this for latest, recent, news, versions, prices, or uncertain facts."""
    from ddgs import DDGS

    search_queries = [
        query,
        f"{query} latest 2026",
        f"{query} official documentation",
    ]

    seen_urls: set[str] = set()
    formatted_results: list[str] = []

    with DDGS() as ddgs:
        for search_query in search_queries:
            for r in ddgs.text(search_query, max_results=3):
                title = r.get("title", "").strip()
                body = r.get("body", "").strip()
                url = r.get("href", "").strip()

                if not title or not url or url in seen_urls:
                    continue

                seen_urls.add(url)
                formatted_results.append(f"Title: {title}\nURL: {url}\nSnippet: {body}")

                if len(formatted_results) >= 5:
                    break

            if len(formatted_results) >= 5:
                break

    if not formatted_results:
        return "No reliable search results found."

    return (
        "Use ONLY these search results to answer. "
        "If the results are weak or incomplete, say so.\n\n"
        + "\n\n---\n\n".join(formatted_results)
    )
