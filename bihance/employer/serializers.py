from rest_framework import serializers
from utils.utils import detect_extra_fields


# Data is based on the fields defined
def validate_company_record(initial_data, fields, data):
    detect_extra_fields(initial_data, fields)
                    
    # Check dual existence 
    industry = data.get("industry")
    other_industry = data.get("otherIndustry")
    if industry and industry.lower() == "other" and not other_industry: 
        raise serializers.ValidationError("OtherIndustry field is not present.")
    
    # Update values
    if industry and industry.lower() == "other" and other_industry: 
        data["industry"] = other_industry
        data.pop("otherIndustry")

    # Same as above 
    talent_needs = data.get("talentNeeds")
    other_talent_needs = data.get("otherTalentNeeds")
    if talent_needs and "other" in talent_needs and not other_talent_needs: 
        raise serializers.ValidationError("OtherTalentNeeds field is not present.")
    
    if talent_needs and "other" in talent_needs and other_talent_needs: 
        data["talentNeeds"] = talent_needs + other_talent_needs
        while "other" in data["talentNeeds"]:
            data["talentNeeds"].remove("other")
        data.pop("otherTalentNeeds")
        
    return data


class EmployerCreateInputSerializer(serializers.Serializer): 
    companyName = serializers.CharField()
    companyWebsite = serializers.CharField()
    contactName = serializers.CharField(required=False)
    contactRole = serializers.CharField(required=False)
    companySize = serializers.CharField(required=False)
    industry = serializers.CharField(required=False)
    # If industry = other
    otherIndustry = serializers.CharField(required=False)
    talentNeeds = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False
    )
    # If talentNeeds contains other
    otherTalentNeeds = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False
    )
    workStyle = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False 
    )
    hiringTimeline = serializers.CharField(required=False)
    featuredPartner = serializers.BooleanField(required=False)
    
    def validate(self, data): 
        data = validate_company_record(self.initial_data, self.fields, data)
        return data
        


class EmployerPartialUpdateInputSerializer(serializers.Serializer): 
    companyName = serializers.CharField(required=False)
    companyWebsite = serializers.CharField(required=False)
    contactName = serializers.CharField(required=False)
    contactRole = serializers.CharField(required=False)
    companySize = serializers.CharField(required=False)
    industry = serializers.CharField(required=False)
    # If industry = other
    otherIndustry = serializers.CharField(required=False)
    talentNeeds = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False
    )
    # If talentNeeds contains other
    otherTalentNeeds = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False
    )
    workStyle = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=False 
    )
    hiringTimeline = serializers.CharField(required=False)
    featuredPartner = serializers.BooleanField(required=False)

    def validate(self, data): 
        data = validate_company_record(self.initial_data, self.fields, data)
        if not data:
            raise serializers.ValidationError("Must update at least one field.")
        return data

        
