from bs4 import BeautifulSoup
import re


class Cleaner:

    def clean_html(self, html):
        """Remove scripts/styles, nav/header/footer/aside tags and common ad elements.
        Return cleaned plain text.
        """
        soup = BeautifulSoup(html, "html.parser")

        # remove script/style/noscript
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()

        # remove common layout blocks
        for selector in [
            "header",
            "footer",
            "nav",
            "aside",
            ".sidebar",
            ".advert",
            ".ads",
            ".cookie",
            "#header",
            "#footer",
        ]:
            for t in soup.select(selector):
                t.decompose()

        # remove elements with ad-like ids/classes
        for t in soup.find_all(
            True,
            {
                "class": re.compile(
                    r"(^|\\s)(ad|ads|advert|banner|promo|cookie)(\\s|$)", re.I
                )
            },
        ):
            t.decompose()
        for t in soup.find_all(
            True,
            {
                "id": re.compile(
                    r"(^|\\s)(ad|ads|advert|banner|promo|cookie)(\\s|$)", re.I
                )
            },
        ):
            t.decompose()

        # focus on article, main, section, div
        texts = []
        candidates = soup.find_all(["article", "main", "section", "div", "p"])
        if not candidates:
            # fallback to body text
            body = soup.body
            if body:
                return " ".join(body.stripped_strings)
            return ""

        seen = set()
        for c in candidates:
            text = " ".join(c.stripped_strings)
            # drop very short or obviously non-text
            if len(text) < 50:
                continue
            # deduplicate
            if text in seen:
                continue
            seen.add(text)
            texts.append(text)

        # join preserving paragraph breaks
        return "\n\n".join(texts)
