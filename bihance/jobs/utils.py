from applications.serializers import ApplicationSerializer, JobSerializer
from files.serializers import FileSerializer

from .serializers import JobRequirementSerializer


def is_employer_in_job(employer, job):
    return job.employer_id == employer


# Parse Job model object into a JSON object
def to_json_object(job):
    job_serializer = JobSerializer(job)

    data = {
        "job": job_serializer.data,
    }

    if job.application_set.all():
        application_serializer = ApplicationSerializer(
            job.application_set.all(), many=True
        )
        data["applications"] = application_serializer.data
    else:
        data["applications"] = None

    if job.jobrequirement_set.all():
        job_requirement_serializer = JobRequirementSerializer(
            job.jobrequirement_set.all(), many=True
        )
        data["job_requirements"] = job_requirement_serializer.data
    else:
        data["job_requirements"] = None

    if job.file_set.first():
        file_serializer = FileSerializer(job.file_set.first())
        data["file"] = file_serializer.data
    else:
        data["file"] = None

    return data
