from crawler.models.database.job import Job
from crawler.models.database.page import Page, PageContentTypes, PageTypes
from crawler.models.database.target import Target
from crawler.models.shared import WebsiteModelTransformations
from tests.fabrics.test_database import TestCrawlingDatabaseSetup
from tests.fabrics.test_website import WebsiteFabric


class PageFabric(TestCrawlingDatabaseSetup, WebsiteFabric):
    def setUp(self):
        super().setUp()

        self.job_instance: Job = Job(depth=3)
        self.session.add(self.job_instance)
        self.session.commit()

        self.target_instance: Target = (
            WebsiteModelTransformations.website_model_to_Target_SQL_model(
                self.website_full_content, self.job_instance
            )
        )
        self.session.add(self.target_instance)
        self.session.commit()


class TestPageModel(PageFabric):
    def test_creation_of_page_model_and_store_in_database(self) -> None:
        page_url: str = "valid_example_fit_in_column_size"
        example_page_title: str = "example_page_title"
        example_page_content: str = "example_page_content"

        page_instance: Page = Page(
            target_id=self.target_instance.id,
            page_type=PageTypes.HTML.value,
            page_content_type=PageContentTypes.UNKNOWN.value,
            website=page_url,
            has_title=bool(example_page_title),
            has_content=bool(example_page_content),
        )

        self.session.add(page_instance)
        self.session.commit()

        lookup_result: Page = (
            self.session.query(Page)
            .filter_by(
                _website=page_url,
            )
            .first()
        )

        self.assertIsNotNone(lookup_result)
        self.assertIsInstance(lookup_result, Page)

    def test_creation_of_page_model_and_store_in_database_with_longer_url(self) -> None:
        page_url: str = "website_" * 100
        example_page_title: str = "example_page_title"
        example_page_content: str = "example_page_content"

        page_instance: Page = Page(
            target_id=self.target_instance.id,
            page_type=PageTypes.HTML.value,
            page_content_type=PageContentTypes.UNKNOWN.value,
            website=page_url,
            has_title=bool(example_page_title),
            has_content=bool(example_page_content),
        )

        self.session.add(page_instance)
        self.session.commit()

        lookup_result: Page = (
            self.session.query(Page)
            .filter_by(
                website_hash=page_instance.website_hash,
            )
            .first()
        )

        self.assertIsNotNone(lookup_result)
        self.assertIsInstance(lookup_result, Page)
