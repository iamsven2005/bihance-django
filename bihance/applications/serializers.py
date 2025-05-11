from .models import Application, Job, User
from rest_framework import serializers
from utils.utils import detect_extra_fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'image_url', 'phone',
            'employee', 'bio', 'age', 'created_at', 'updated_at', 'role', 'location'
        ]
        

class JobSerializer(serializers.ModelSerializer):
    employer = UserSerializer(source='employer_id', read_only=True)

    class Meta:
        model = Job
        fields = [
            'job_id', 'name', 'employer', 'start_date', 'end_date', 'salary', 'higher_salary',
            'description', 'requirements', 'posted_date', 'photo_url', 'start_age', 'end_age',
            'gender', 'location', 'job_type', 'location_name', 'company', 'duration', 'pay_type'
        ]
     

class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(source='job_id', read_only=True)
    employee = UserSerializer(source='employee_id', read_only=True)

    class Meta:
        model = Application
        fields = [
            'application_id', 'job', 'employee', 'accept',
            'bio', 'employee_review', 'employer_review', 'employer_id'
        ]


class ApplicationListInputSerializer(serializers.Serializer):
    applicationStatus = serializers.IntegerField(required=False)
    userOnly = serializers.BooleanField(required=False)

    def validate_applicationStatus(self, value): 
        num_value = int(value)
        if num_value < 0 or num_value > 4: 
            raise serializers.ValidationError("Application status can only be from 0 - 4.")
        
        return num_value

    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


class ApplicationCreateInputSerializer(serializers.Serializer):
    jobId = serializers.CharField() 
    employerId = serializers.CharField()
    
    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        return data


class ApplicationPartialUpdateInputSerializer(serializers.Serializer):
    newStatus = serializers.IntegerField(required=False)
    newBio = serializers.CharField(required=False)

    def validate_newStatus(self, value): 
        num_value = int(value)
        if num_value < 0 or num_value > 4: 
            raise serializers.ValidationError("Application status can only be from 0 - 4.")
        
        return num_value
            
    
    def validate(self, data): 
        detect_extra_fields(self.initial_data, self.fields)
        
        has_status = "newStatus" in data
        has_bio = "newBio" in data

        # XOR 
        if has_status ^ has_bio:  
            return data
        raise serializers.ValidationError("Can either update application status or application bio, but not both.")
            

