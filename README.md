# Crawler service
-Crawl orchestrator/ fabric which performs recursive scrape.
-Starting with a root URL and performs recursive scrape of nested URLs based on the requested depth.
-Allows filtering URLs based on regex and blocking scrapes for URLs containing specific extensions.
-Allows granular write to multiple data stores, based on the need.
-NOTE: Current implementation is scroped around crawling a single website and all operations are performed synchronously.

## References

- [Developer Guide](./docs/developer.md)
