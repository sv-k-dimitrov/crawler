from .database.job import Job
from .database.target import Target
from .website import Website


class WebsiteModelTransformations:
    @staticmethod
    def website_model_to_Target_SQL_model(
        website: Website,
        job: Job,
        s3_bucket: str = None,
        s3_location: str = None,
        filesystem_location: str = None,
    ) -> Target:
        return Target(
            website=website.website,
            crawling_job_id=job.id,
            s3_bucket=s3_bucket,
            s3_location=s3_location,
            filesystem_location=filesystem_location,
            website_metadata={
                "label": website.label,
                "safe_key": website.safe_key,
            },
            count_pdf_pages=website.count_pdf_pages,
            count_html_pages=website.count_html_pages,
            largest_pdf_size=website.largest_pdf_size,
            largest_pdf_link=website.largest_pdf_link,
        )
