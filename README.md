# Crawler Service

- Crawl orchestrator/fabric that performs recursive scraping.

- Starts with a root URL and recursively scrapes nested URLs based on the requested depth.

- Allows filtering URLs using regex.

- Blocks scrapes for URLs containing specific extensions.

- Supports granular writes to multiple data stores based on specific requirements.

- **NOTE**: The current implementation is scoped to crawl a single website, and all operations are performed synchronously.

## References

- [Developer Guide](./docs/developer.md)
