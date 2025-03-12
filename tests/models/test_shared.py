from crawler.models.database.job import Job
from crawler.models.database.target import Target
from crawler.models.shared import WebsiteModelTransformations
from tests.fabrics.test_database import TestCrawlingDatabaseSetup
from tests.fabrics.test_website import WebsiteFabric


class TestWebsiteModelTransformations(TestCrawlingDatabaseSetup, WebsiteFabric):
    def setUp(self):
        super().setUp()

        self.job_instance: Job = Job(depth=3)

        self.session.add(self.job_instance)
        self.session.commit()

    def test_Target_model_properly_created(self) -> None:
        target: Target = WebsiteModelTransformations.website_model_to_Target_SQL_model(
            self.website_full_content, self.job_instance
        )

        self.assertIsInstance(target, Target)
        self.assertEqual(
            target.count_html_pages, self.website_full_content.count_html_pages
        )
        self.assertIsNone(target.s3_bucket)
        self.assertIsNone(target.s3_location)
        self.assertIsNone(target.filesystem_location)
