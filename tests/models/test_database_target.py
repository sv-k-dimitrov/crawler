from uuid import uuid4

from crawler.models.database.job import Job
from crawler.models.database.target import Target
from tests.fabrics.test_database import TestCrawlingDatabaseSetup
from tests.fabrics.test_website import WebsiteFabric


class TestDatabaseModelTarget(TestCrawlingDatabaseSetup, WebsiteFabric):
    def setUp(self):
        super().setUp()

        self.job_instance: Job = Job(depth=3)

        self.session.add(self.job_instance)
        self.session.commit()

    def test_create_target_finished_at_is_emptry_after_creation(self) -> None:
        test_target_instance: Target = Target(
            website=self.website_full_content.website,
            crawling_job_id=self.job_instance.id,
            s3_bucket=None,
            s3_location=None,
            filesystem_location=None,
            website_metadata={
                "label": self.website_full_content.label,
                "safe_key": self.website_full_content.safe_key,
            },
            count_pdf_pages=self.website_full_content.count_pdf_pages,
            count_html_pages=self.website_full_content.count_html_pages,
            largest_pdf_size=self.website_full_content.largest_pdf_size,
            largest_pdf_link=self.website_full_content.largest_pdf_link,
        )

        self.session.add(test_target_instance)
        self.session.commit()

        lookup_target: Target = (
            self.session.query(Target)
            .filter_by(crawling_job_id=self.job_instance.id)
            .first()
        )

        self.assertIsNone(lookup_target.finished_at)

        lookup_target.set_finished(self.session)

        self.assertIsNotNone(lookup_target.finished_at)
