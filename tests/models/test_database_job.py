from uuid import UUID

from crawler.managers.shared import create_job, finish_job
from crawler.models.database import Job
from tests.fabrics.test_database import TestCrawlingDatabaseSetup


class TestCreateAndFinishJobHelpers(TestCrawlingDatabaseSetup):
    def test_create_job_helper_success_db_insert(self) -> None:
        example_crawl_depth: int = 3
        job_uuid: str = create_job(example_crawl_depth)

        job_lookup: Job = self.session.query(Job).filter_by(id=job_uuid).first()

        self.assertIsNotNone(job_lookup)
        self.assertEqual(job_lookup.depth, example_crawl_depth)

    def test_finish_job_helper_success_db_insert(self) -> None:
        example_crawl_depth: int = 3
        job_uuid: UUID = create_job(example_crawl_depth)

        finish_job(job_uuid)

        job_lookup: Job = self.session.query(Job).filter_by(id=job_uuid).first()

        self.assertIsNotNone(job_lookup)
        self.assertIsNotNone(job_lookup.finished)
