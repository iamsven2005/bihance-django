from .serializers import EmployerProfileSerializer
from applications.serializers import JobSerializer, UserSerializer
from files.serializers import FileSerializer


def to_json_object(company): 
    company_serializer = EmployerProfileSerializer(company)
    employer_serializer = UserSerializer(company.employer_id)

    data = {
        "company": company_serializer.data,
        "employer": employer_serializer.data
    }

    associated_jobs = company.employer_id.job_set.all()
    if associated_jobs: 
        job_serializer = JobSerializer(associated_jobs, many=True)
        data["jobs"] = job_serializer.data
    else: 
        data["jobs"] = None 

    associated_file = company.file_set.first()
    if associated_file: 
        file_serializer = FileSerializer(associated_file)
        data["file"] = file_serializer.data
    else: 
        data["file"] = None 

    return data


